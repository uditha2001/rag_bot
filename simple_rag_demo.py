#!/usr/bin/env python3
"""
Simple RAG Bot Demo - Standalone version without MCP
This provides a simple interface to test the RAG functionality
"""

import sys
import logging
from pathlib import Path
from config import Config

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_servers.rag_server.document_processor import DocumentProcessor
from mcp_servers.rag_server.vector_store import VectorStore
from mcp_servers.rag_server.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRAGBot:
    """Simple RAG Bot for testing without MCP"""
    
    def __init__(self, YOUR_HF_TOKEN_HERE: str):
        self.YOUR_HF_TOKEN_HERE = YOUR_HF_TOKEN_HERE
        
        # Initialize components
        print("🔧 Initializing RAG components...")
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore(index_path="simple_rag_index")
        self.rag_pipeline = RAGPipeline(YOUR_HF_TOKEN_HERE)
        
        print("✅ RAG Bot initialized successfully!")
    
    def load_documents_from_directory(self, directory_path: str):
        """Load all supported documents from a directory"""
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return False
        
        loaded_count = 0
        total_chunks = 0
        
        print(f"📁 Loading documents from: {directory_path}")
        
        # Process all supported files
        for file_path in directory.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.doc_processor.supported_extensions:
                try:
                    print(f"  📄 Processing: {file_path.name}")
                    
                    # Extract text
                    text = self.doc_processor.extract_text(str(file_path))
                    
                    # Split into chunks
                    chunks = self.doc_processor.split_text(text, chunk_size=1000, chunk_overlap=200)
                    
                    # Add to vector store
                    metadata = [{"source": str(file_path), "chunk_id": i} for i in range(len(chunks))]
                    self.vector_store.add_documents(chunks, metadata)
                    
                    loaded_count += 1
                    total_chunks += len(chunks)
                    
                    print(f"    ✅ Loaded {len(chunks)} chunks")
                    
                except Exception as e:
                    print(f"    ❌ Failed to process {file_path.name}: {e}")
        
        print(f"\n📊 Summary: {loaded_count} documents loaded, {total_chunks} total chunks")
        return loaded_count > 0
    
    def search_documents(self, query: str, top_k: int = 5):
        """Search for relevant documents"""
        print(f"🔍 Searching for: '{query}'")
        
        results = self.vector_store.search(query, top_k)
        
        if not results:
            print("❌ No relevant documents found")
            return []
        
        print(f"📋 Found {len(results)} relevant documents:")
        for i, (doc, score) in enumerate(results, 1):
            source = Path(doc.metadata.get("source", "Unknown")).name
            print(f"  {i}. Source: {source} (Score: {score:.3f})")
            print(f"     Preview: {doc.page_content[:100]}...")
        
        return results
    
    def ask_question(self, question: str):
        """Ask a question and get an answer using RAG"""
        print(f"\n❓ Question: {question}")
        
        # Search for relevant documents
        relevant_docs = self.vector_store.search(question, top_k=3)
        
        if not relevant_docs:
            return "I don't have any relevant information to answer your question."
        
        # Generate answer
        print("🤖 Generating answer...")
        answer = self.rag_pipeline.generate_answer(question, relevant_docs, max_tokens=300)
        
        # Show sources
        sources = list(set([Path(doc.metadata.get("source", "Unknown")).name 
                          for doc, _ in relevant_docs]))
        
        print(f"\n💡 Answer: {answer}")
        print(f"\n📚 Sources: {', '.join(sources)}")
        
        return answer
    
    def get_stats(self):
        """Get system statistics"""
        stats = self.vector_store.get_stats()
        print("\n📊 System Statistics:")
        print(f"  📄 Total documents: {stats['total_documents']}")
        print(f"  🔢 Total vectors: {stats['total_vectors']}")
        print(f"  📐 Embedding dimension: {stats['embedding_dimension']}")
        print(f"  🏷️ Unique sources: {stats['unique_sources']}")
        if stats['sources']:
            print("  📁 Sources:")
            for source in stats['sources']:
                print(f"    - {source}")
        return stats
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n🎯 RAG Bot - Interactive Mode")
        print("Commands:")
        print("  /load <directory> - Load documents from directory")
        print("  /search <query> - Search documents")
        print("  /stats - Show system statistics")
        print("  /help - Show this help")
        print("  /quit - Exit")
        print("  Or just ask any question!")
        print("\nType your command or question:\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['/quit', '/exit', '/q']:
                    break
                    
                elif user_input.startswith('/load '):
                    directory = user_input[6:].strip()
                    self.load_documents_from_directory(directory)
                    
                elif user_input.startswith('/search '):
                    query = user_input[8:].strip()
                    self.search_documents(query)
                    
                elif user_input == '/stats':
                    self.get_stats()
                    
                elif user_input == '/help':
                    print("Commands:")
                    print("  /load <directory> - Load documents from directory")
                    print("  /search <query> - Search documents")
                    print("  /stats - Show system statistics")
                    print("  /help - Show this help")
                    print("  /quit - Exit")
                    print("  Or just ask any question!")
                    
                else:
                    # Regular question
                    self.ask_question(user_input)
                
                print()  # Add spacing
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Goodbye! Thanks for using RAG Bot!")

def main():
    """Main function"""
    # Configuration - Use environment variables
    HF_TOKEN = Config.get_YOUR_HF_TOKEN_HERE()
    
    print("🚀 Simple RAG Bot Demo")
    print("=" * 50)
    
    try:
        # Initialize bot
        bot = SimpleRAGBot(HF_TOKEN)
        
        # Auto-load documents from data directory if it exists
        data_dir = Path("data")
        if data_dir.exists():
            print(f"\n🔄 Auto-loading documents from '{data_dir}'...")
            if bot.load_documents_from_directory(str(data_dir)):
                bot.get_stats()
        
        # Run interactive mode
        bot.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error starting RAG Bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
