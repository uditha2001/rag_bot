#!/usr/bin/env python3
"""
Simple Web Interface for RAG Bot
A basic HTML/JavaScript interface served by FastAPI
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path
from config import Config
import logging
import json
from tempfile import NamedTemporaryFile
import shutil

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_servers.rag_server.document_processor import DocumentProcessor
from mcp_servers.rag_server.vector_store import VectorStore
from mcp_servers.rag_server.rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 300

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

# Initialize FastAPI app
app = FastAPI(title="RAG Bot Simple Web UI", version="1.0.0")

# Global components
# Configuration
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
    vector_store = VectorStore(index_path="simple_web_rag_index")
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
                text = doc_processor.extract_text(str(file_path))
                chunks = doc_processor.split_text(text, chunk_size=1000, chunk_overlap=200)
                metadata = [{"source": str(file_path), "chunk_id": i} for i in range(len(chunks))]
                vector_store.add_documents(chunks, metadata)
                
                files_processed += 1
                total_chunks += len(chunks)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
    
    return {"files_processed": files_processed, "chunks_added": total_chunks}

# HTML Interface
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the main web interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Bot - Simple Web Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .tabs { 
            display: flex; 
            background: #f8f9fa; 
            border-bottom: 1px solid #e9ecef;
        }
        .tab { 
            flex: 1; 
            padding: 20px; 
            cursor: pointer; 
            border: none; 
            background: none; 
            font-size: 16px;
            transition: all 0.3s;
        }
        .tab.active { 
            background: white; 
            border-bottom: 3px solid #667eea;
            color: #667eea;
            font-weight: bold;
        }
        .tab:hover { background: #e9ecef; }
        .content { 
            padding: 30px; 
            min-height: 600px;
        }
        .hidden { display: none; }
        .chat-container { 
            height: 500px; 
            border: 1px solid #e9ecef; 
            border-radius: 10px;
            display: flex;
            flex-direction: column;
        }
        .messages { 
            flex: 1; 
            padding: 20px; 
            overflow-y: auto; 
            background: #f8f9fa;
        }
        .message { 
            margin-bottom: 15px; 
            padding: 15px 20px; 
            border-radius: 18px; 
            max-width: 80%;
            animation: slideIn 0.3s ease;
        }
        .message.user { 
            background: #667eea; 
            color: white; 
            margin-left: auto; 
            text-align: right;
        }
        .message.bot { 
            background: white; 
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message.error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb;
        }
        .sources { 
            margin-top: 10px; 
            padding-top: 10px; 
            border-top: 1px solid #e9ecef; 
            font-size: 0.9em;
            opacity: 0.8;
        }
        .input-area { 
            padding: 20px; 
            border-top: 1px solid #e9ecef; 
            background: white;
            display: flex;
            gap: 10px;
        }
        .input-area input { 
            flex: 1; 
            padding: 15px; 
            border: 1px solid #e9ecef; 
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .input-area input:focus { border-color: #667eea; }
        .btn { 
            padding: 15px 30px; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px;
            transition: all 0.3s;
        }
        .btn-primary { 
            background: #667eea; 
            color: white; 
        }
        .btn-primary:hover { 
            background: #5a67d8; 
            transform: translateY(-2px);
        }
        .btn:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
            transform: none !important;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold;
            color: #333;
        }
        .form-group input, .form-group select { 
            width: 100%; 
            padding: 12px; 
            border: 1px solid #e9ecef; 
            border-radius: 8px;
            font-size: 16px;
        }
        .results { 
            margin-top: 20px; 
        }
        .result-item { 
            background: white; 
            border: 1px solid #e9ecef; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .result-header { 
            display: flex; 
            justify-content: between; 
            align-items: center; 
            margin-bottom: 10px;
        }
        .result-score { 
            background: #667eea; 
            color: white; 
            padding: 4px 12px; 
            border-radius: 15px; 
            font-size: 0.9em;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px;
        }
        .stat-card { 
            background: white; 
            border: 1px solid #e9ecef; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 10px;
        }
        .upload-area { 
            border: 2px dashed #e9ecef; 
            border-radius: 10px; 
            padding: 40px; 
            text-align: center; 
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        .upload-area:hover { 
            border-color: #667eea; 
            background: #f8f9fa;
        }
        .loading { 
            display: inline-block; 
            width: 20px; 
            height: 20px; 
            border: 3px solid #f3f3f3; 
            border-top: 3px solid #667eea; 
            border-radius: 50%; 
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @media (max-width: 768px) {
            .tabs { flex-direction: column; }
            .message { max-width: 95%; }
            .input-area { flex-direction: column; }
            .container { margin: 10px; border-radius: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 RAG Bot</h1>
            <p>Retrieval-Augmented Generation System</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('chat')">💬 Chat</button>
            <button class="tab" onclick="showTab('search')">🔍 Search</button>
            <button class="tab" onclick="showTab('upload')">📄 Upload</button>
            <button class="tab" onclick="showTab('stats')">📊 Statistics</button>
        </div>
        
        <div class="content">
            <!-- Chat Tab -->
            <div id="chat" class="tab-content">
                <div class="chat-container">
                    <div class="messages" id="messages">
                        <div class="message bot">
                            Hello! I'm your RAG Bot assistant. I can answer questions about the documents in my knowledge base. What would you like to know?
                        </div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="chatInput" placeholder="Ask me anything about your documents..." onkeypress="handleChatKeyPress(event)">
                        <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
            
            <!-- Search Tab -->
            <div id="search" class="tab-content hidden">
                <div class="form-group">
                    <label for="searchInput">Search Documents:</label>
                    <input type="text" id="searchInput" placeholder="Enter your search query..." onkeypress="handleSearchKeyPress(event)">
                </div>
                <button class="btn btn-primary" onclick="searchDocuments()">Search</button>
                <div id="searchResults" class="results"></div>
            </div>
            
            <!-- Upload Tab -->
            <div id="upload" class="tab-content hidden">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <h3>📄 Upload Documents</h3>
                    <p>Click here to select files or drag and drop</p>
                    <p><small>Supported: TXT, PDF, DOCX</small></p>
                    <input type="file" id="fileInput" multiple accept=".txt,.pdf,.docx" style="display:none" onchange="uploadFiles()">
                </div>
                <div id="uploadResults"></div>
            </div>
            
            <!-- Statistics Tab -->
            <div id="stats" class="tab-content hidden">
                <div class="stats-grid" id="statsGrid">
                    <div class="stat-card">
                        <div class="loading"></div>
                        <p>Loading statistics...</p>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="loadStats()" style="margin-top: 20px;">Refresh Stats</button>
            </div>
        </div>
    </div>

    <script>
        let isLoading = false;

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.remove('hidden');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load stats when stats tab is shown
            if (tabName === 'stats') {
                loadStats();
            }
        }

        function handleChatKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function handleSearchKeyPress(event) {
            if (event.key === 'Enter') {
                searchDocuments();
            }
        }

        async function sendMessage() {
            if (isLoading) return;
            
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Add user message
            addMessage(question, 'user');
            input.value = '';
            
            // Add loading message
            const loadingId = addMessage('Thinking...', 'bot loading');
            
            isLoading = true;
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question, max_tokens: 300})
                });
                
                const data = await response.json();
                
                // Remove loading message
                document.getElementById(loadingId).remove();
                
                if (response.ok) {
                    let botMessage = data.answer;
                    if (data.sources && data.sources.length > 0) {
                        botMessage += '<div class="sources"><strong>Sources:</strong> ' + data.sources.join(', ') + '</div>';
                    }
                    addMessage(botMessage, 'bot');
                } else {
                    addMessage('Sorry, I encountered an error: ' + data.detail, 'bot error');
                }
            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessage('Sorry, I encountered a network error. Please try again.', 'bot error');
            }
            
            isLoading = false;
        }

        function addMessage(content, type) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            const messageId = 'msg_' + Date.now();
            messageDiv.id = messageId;
            messageDiv.className = 'message ' + type;
            messageDiv.innerHTML = content;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
            return messageId;
        }

        async function searchDocuments() {
            const input = document.getElementById('searchInput');
            const query = input.value.trim();
            
            if (!query) return;
            
            const results = document.getElementById('searchResults');
            results.innerHTML = '<div class="loading"></div> Searching...';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, top_k: 5})
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displaySearchResults(data.results);
                } else {
                    results.innerHTML = '<div class="message error">Search failed: ' + data.detail + '</div>';
                }
            } catch (error) {
                results.innerHTML = '<div class="message error">Network error occurred during search.</div>';
            }
        }

        function displaySearchResults(results) {
            const container = document.getElementById('searchResults');
            
            if (results.length === 0) {
                container.innerHTML = '<div class="message">No results found.</div>';
                return;
            }
            
            let html = '<h3>Search Results (' + results.length + ' found)</h3>';
            
            results.forEach((result, index) => {
                html += `
                    <div class="result-item">
                        <div class="result-header">
                            <strong>${result.source}</strong>
                            <span class="result-score">${(result.score * 100).toFixed(1)}% match</span>
                        </div>
                        <div>${result.content}</div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        async function uploadFiles() {
            const input = document.getElementById('fileInput');
            const files = input.files;
            
            if (files.length === 0) return;
            
            const results = document.getElementById('uploadResults');
            results.innerHTML = '<div class="loading"></div> Uploading and processing files...';
            
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    results.innerHTML = `
                        <div class="message bot">
                            <strong>✅ Upload Successful!</strong><br>
                            ${data.message}<br>
                            Files processed: ${data.files_processed}<br>
                            Chunks added: ${data.chunks_added}
                        </div>
                    `;
                    input.value = ''; // Clear the input
                } else {
                    results.innerHTML = '<div class="message error">Upload failed: ' + data.detail + '</div>';
                }
            } catch (error) {
                results.innerHTML = '<div class="message error">Network error during upload.</div>';
            }
        }

        async function loadStats() {
            const container = document.getElementById('statsGrid');
            container.innerHTML = '<div class="stat-card"><div class="loading"></div><p>Loading...</p></div>';
            
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (response.ok) {
                    displayStats(data);
                } else {
                    container.innerHTML = '<div class="message error">Failed to load statistics.</div>';
                }
            } catch (error) {
                container.innerHTML = '<div class="message error">Network error occurred.</div>';
            }
        }

        function displayStats(stats) {
            const container = document.getElementById('statsGrid');
            
            let html = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total_documents}</div>
                    <p>Total Documents</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.total_vectors}</div>
                    <p>Vector Embeddings</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.unique_sources}</div>
                    <p>Unique Sources</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.embedding_model.split('/').pop()}</div>
                    <p>Embedding Model</p>
                </div>
            `;
            
            if (stats.sources && stats.sources.length > 0) {
                html += '<div class="stat-card" style="grid-column: 1/-1;"><h4>Sources:</h4><ul>';
                stats.sources.forEach(source => {
                    html += '<li>' + source + '</li>';
                });
                html += '</ul></div>';
            }
            
            container.innerHTML = html;
        }

        // Load stats on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
        });
    </script>
</body>
</html>
    """

# API Endpoints
@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question using RAG"""
    try:
        relevant_docs = vector_store.search(request.question, top_k=3)
        
        if not relevant_docs:
            raise HTTPException(
                status_code=404, 
                detail="No relevant documents found to answer your question."
            )
        
        answer = rag_pipeline.generate_answer(
            request.question, 
            relevant_docs, 
            max_tokens=request.max_tokens
        )
        
        sources = list(set([
            Path(doc.metadata.get("source", "Unknown")).name 
            for doc, _ in relevant_docs
        ]))
        
        return {
            "answer": answer,
            "sources": sources,
            "relevant_docs_count": len(relevant_docs)
        }
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
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
        
        return {
            "results": formatted_results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        files_processed = 0
        total_chunks = 0
        
        for file in files:
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in doc_processor.supported_extensions:
                continue
            
            with NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                text = doc_processor.extract_text(tmp_path)
                chunks = doc_processor.split_text(text, chunk_size=1000, chunk_overlap=200)
                
                metadata = [{"source": file.filename, "chunk_id": i} for i in range(len(chunks))]
                vector_store.add_documents(chunks, metadata)
                
                files_processed += 1
                total_chunks += len(chunks)
                
            finally:
                os.unlink(tmp_path)
        
        return {
            "message": f"Successfully processed {files_processed} files",
            "files_processed": files_processed,
            "chunks_added": total_chunks
        }
        
    except Exception as e:
        logger.error(f"Error in upload_documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RAG Bot Simple Web Interface...")
    print("🌐 Access the web interface at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
