#!/usr/bin/env python3
"""
FastAPI Backend for RAG Bot React UI
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path
import logging
import asyncio
from tempfile import NamedTemporaryFile
import shutil
from config import Config

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_servers.rag_server.document_processor import DocumentProcessor
from mcp_servers.rag_server.vector_store import VectorStore
from mcp_servers.rag_server.rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 300

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
    relevant_docs_count: int

class SearchResponse(BaseModel):
    results: List[dict]
    total_results: int

class StatsResponse(BaseModel):
    total_documents: int
    total_vectors: int
    unique_sources: int
    sources: List[str]
    embedding_model: str

class UploadResponse(BaseModel):
    message: str
    files_processed: int
    chunks_added: int

# Initialize FastAPI app
app = FastAPI(title="RAG Bot API", description="REST API for RAG Bot", version="1.0.0")

# CORS middleware for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
HF_TOKEN = Config.get_YOUR_HF_TOKEN_HERE()
doc_processor = None
vector_store = None
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG components on startup"""
    global doc_processor, vector_store, rag_pipeline
    
    logger.info("Initializing RAG components...")
    doc_processor = DocumentProcessor()
    vector_store = VectorStore(index_path="web_rag_index")
    rag_pipeline = RAGPipeline(HF_TOKEN)
    
    # Auto-load documents from data directory
    data_dir = Path("data")
    if data_dir.exists():
        logger.info("Auto-loading documents from data directory...")
        await load_documents_from_directory(str(data_dir))
    
    logger.info("RAG components initialized successfully!")

async def load_documents_from_directory(directory_path: str) -> dict:
    """Load documents from a directory"""
    directory = Path(directory_path)
    
    if not directory.exists():
        return {"files_processed": 0, "chunks_added": 0, "error": "Directory not found"}
    
    files_processed = 0
    total_chunks = 0
    
    for file_path in directory.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in doc_processor.supported_extensions:
            try:
                # Extract text
                text = doc_processor.extract_text(str(file_path))
                
                # Split into chunks
                chunks = doc_processor.split_text(text, chunk_size=1000, chunk_overlap=200)
                
                # Add to vector store
                metadata = [{"source": str(file_path), "chunk_id": i} for i in range(len(chunks))]
                vector_store.add_documents(chunks, metadata)
                
                files_processed += 1
                total_chunks += len(chunks)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
    
    return {"files_processed": files_processed, "chunks_added": total_chunks}

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG Bot API is running!", "status": "healthy"}

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question using RAG"""
    try:
        # Search for relevant documents
        relevant_docs = vector_store.search(request.question, top_k=3)
        
        if not relevant_docs:
            raise HTTPException(
                status_code=404, 
                detail="No relevant documents found to answer your question."
            )
        
        # Generate answer
        answer = rag_pipeline.generate_answer(
            request.question, 
            relevant_docs, 
            max_tokens=request.max_tokens
        )
        
        # Extract sources
        sources = list(set([
            Path(doc.metadata.get("source", "Unknown")).name 
            for doc, _ in relevant_docs
        ]))
        
        return QuestionResponse(
            answer=answer,
            sources=sources,
            relevant_docs_count=len(relevant_docs)
        )
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for relevant documents"""
    try:
        results = vector_store.search(request.query, top_k=request.top_k)
        
        formatted_results = []
        for doc, score in results:
            source = Path(doc.metadata.get("source", "Unknown")).name
            formatted_results.append({
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "source": source,
                "score": float(score),
                "metadata": doc.metadata
            })
        
        return SearchResponse(
            results=formatted_results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        stats = vector_store.get_stats()
        
        return StatsResponse(
            total_documents=stats["total_documents"],
            total_vectors=stats["total_vectors"],
            unique_sources=stats["unique_sources"],
            sources=stats.get("sources", []),
            embedding_model=stats["embedding_model"]
        )
        
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        files_processed = 0
        total_chunks = 0
        
        for file in files:
            # Check file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in doc_processor.supported_extensions:
                continue
            
            # Save uploaded file temporarily
            with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # Process the document
                text = doc_processor.extract_text(tmp_path)
                chunks = doc_processor.split_text(text, chunk_size=1000, chunk_overlap=200)
                
                # Add to vector store
                metadata = [{"source": file.filename, "chunk_id": i} for i in range(len(chunks))]
                vector_store.add_documents(chunks, metadata)
                
                files_processed += 1
                total_chunks += len(chunks)
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_path)
        
        return UploadResponse(
            message=f"Successfully processed {files_processed} files",
            files_processed=files_processed,
            chunks_added=total_chunks
        )
        
    except Exception as e:
        logger.error(f"Error in upload_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/clear")
async def clear_documents():
    """Clear all documents from the vector store"""
    try:
        vector_store.clear()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        logger.error(f"Error in clear_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve React static files (after build)
@app.get("/app/{path:path}")
async def serve_react_app(path: str):
    """Serve React app static files"""
    react_build_dir = Path("web_ui/build")
    file_path = react_build_dir / path
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    else:
        # Return index.html for client-side routing
        index_path = react_build_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="React app not built")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
