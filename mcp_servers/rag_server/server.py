import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
import mcp.server.stdio
import mcp.types as types

from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .rag_pipeline import RAGPipeline
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGServer:
    def __init__(self, hf_token: str, documents_path: str = "data"):
        self.hf_token = hf_token
        self.documents_path = Path(documents_path)
        self.documents_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.rag_pipeline = RAGPipeline(hf_token)
        
        # MCP Server
        self.server = Server("rag-server")
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available document resources"""
            resources = []
            
            # List all processed documents
            for doc_file in self.documents_path.glob("**/*"):
                if doc_file.is_file() and doc_file.suffix in ['.txt', '.pdf', '.docx']:
                    resources.append(
                        Resource(
                            uri=AnyUrl(f"file://{doc_file.absolute()}"),
                            name=doc_file.name,
                            description=f"Document: {doc_file.name}",
                            mimeType="text/plain" if doc_file.suffix == '.txt' else "application/octet-stream"
                        )
                    )
            
            return resources
        
        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read a document resource"""
            try:
                file_path = Path(str(uri).replace("file://", ""))
                if file_path.exists():
                    return self.doc_processor.extract_text(str(file_path))
                else:
                    raise FileNotFoundError(f"Document not found: {file_path}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available RAG tools"""
            return [
                Tool(
                    name="load_documents",
                    description="Load and process documents into the vector store",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to process"
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                Tool(
                    name="search_documents",
                    description="Search for relevant documents using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="ask_question",
                    description="Ask a question about the loaded documents using RAG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Question to ask about the documents"
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximum tokens in response",
                                "default": 512
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="get_document_summary",
                    description="Get a summary of all loaded documents",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "load_documents":
                    return await self._load_documents(arguments.get("file_paths", []))
                elif name == "search_documents":
                    return await self._search_documents(
                        arguments.get("query", ""),
                        arguments.get("top_k", 5)
                    )
                elif name == "ask_question":
                    return await self._ask_question(
                        arguments.get("question", ""),
                        arguments.get("max_tokens", 512)
                    )
                elif name == "get_document_summary":
                    return await self._get_document_summary()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _load_documents(self, file_paths: List[str]) -> list[types.TextContent]:
        """Load documents into vector store"""
        results = []
        loaded_count = 0
        
        for file_path in file_paths:
            try:
                # Process document
                text = self.doc_processor.extract_text(file_path)
                chunks = self.doc_processor.split_text(text)
                
                # Add to vector store
                self.vector_store.add_documents(chunks, [{"source": file_path}] * len(chunks))
                loaded_count += 1
                
                results.append(f"✅ Loaded: {Path(file_path).name} ({len(chunks)} chunks)")
                
            except Exception as e:
                results.append(f"❌ Failed to load {file_path}: {str(e)}")
        
        summary = f"\n\nSummary: {loaded_count}/{len(file_paths)} documents loaded successfully."
        return [types.TextContent(type="text", text="\n".join(results) + summary)]
    
    async def _search_documents(self, query: str, top_k: int) -> list[types.TextContent]:
        """Search documents using vector similarity"""
        try:
            results = self.vector_store.search(query, top_k)
            
            if not results:
                return [types.TextContent(type="text", text="No documents found matching your query.")]
            
            formatted_results = []
            for i, (doc, score) in enumerate(results, 1):
                source = doc.metadata.get("source", "Unknown")
                formatted_results.append(
                    f"**Result {i}** (Score: {score:.3f})\n"
                    f"Source: {Path(source).name}\n"
                    f"Content: {doc.page_content[:300]}...\n"
                )
            
            return [types.TextContent(type="text", text="\n".join(formatted_results))]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Search error: {str(e)}")]
    
    async def _ask_question(self, question: str, max_tokens: int) -> list[types.TextContent]:
        """Answer question using RAG pipeline"""
        try:
            # Get relevant documents
            relevant_docs = self.vector_store.search(question, top_k=3)
            
            if not relevant_docs:
                return [types.TextContent(type="text", text="No relevant documents found to answer your question.")]
            
            # Generate answer using RAG
            answer = self.rag_pipeline.generate_answer(question, relevant_docs, max_tokens)
            
            # Format response with sources
            sources = list(set([Path(doc.metadata.get("source", "Unknown")).name 
                              for doc, _ in relevant_docs]))
            
            response = f"**Answer:** {answer}\n\n**Sources:** {', '.join(sources)}"
            return [types.TextContent(type="text", text=response)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error generating answer: {str(e)}")]
    
    async def _get_document_summary(self) -> list[types.TextContent]:
        """Get summary of loaded documents"""
        try:
            stats = self.vector_store.get_stats()
            return [types.TextContent(type="text", text=f"Vector Store Statistics:\n{json.dumps(stats, indent=2)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error getting summary: {str(e)}")]

async def main():
    """Run the RAG server"""
    # Use configuration
    HF_TOKEN = Config.get_hf_token()
    
    rag_server = RAGServer(HF_TOKEN)
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await rag_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rag-server",
                server_version="1.0.0",
                capabilities=rag_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
