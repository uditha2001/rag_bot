#!/usr/bin/env python3
"""
Comprehensive test script for the RAG Bot system
Tests all components and functionality
"""

import asyncio
import sys
import logging
from pathlib import Path
from config import Config
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_servers.rag_server.document_processor import DocumentProcessor
from mcp_servers.rag_server.vector_store import VectorStore
from mcp_servers.rag_server.rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGSystemTester:
    """Comprehensive tester for the RAG system"""
    
    def __init__(self, YOUR_HF_TOKEN_HERE: str):
        self.YOUR_HF_TOKEN_HERE = YOUR_HF_TOKEN_HERE
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all tests sequentially"""
        print("🚀 Starting RAG System Comprehensive Tests\n")
        
        tests = [
            ("Document Processor", self.test_document_processor),
            ("Vector Store", self.test_vector_store),
            ("RAG Pipeline", self.test_rag_pipeline),
            ("Integration Test", self.test_integration),
        ]
        
        for test_name, test_func in tests:
            print(f"📋 Testing {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = {"status": "PASS" if result else "FAIL", "error": None}
                print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}\n")
            except Exception as e:
                self.test_results[test_name] = {"status": "ERROR", "error": str(e)}
                print(f"❌ {test_name}: ERROR - {str(e)}\n")
                logger.error(f"Error in {test_name}: {traceback.format_exc()}")
        
        self.print_summary()
    
    def test_document_processor(self) -> bool:
        """Test document processing functionality"""
        try:
            processor = DocumentProcessor()
            
            # Test 1: Check supported extensions
            assert processor.supported_extensions == {'.txt', '.pdf', '.docx'}, "Supported extensions mismatch"
            print("  ✓ Supported extensions correct")
            
            # Test 2: Extract text from test document
            test_file = Path("data/ai_basics.txt")
            if test_file.exists():
                text = processor.extract_text(str(test_file))
                assert len(text) > 100, "Extracted text too short"
                assert "Artificial Intelligence" in text, "Expected content not found"
                print(f"  ✓ Text extraction successful ({len(text)} characters)")
            else:
                print("  ⚠ Test file not found, skipping text extraction test")
            
            # Test 3: Text splitting
            sample_text = "This is a test. " * 100  # Create long text
            chunks = processor.split_text(sample_text, chunk_size=50, chunk_overlap=10)
            assert len(chunks) > 1, "Text splitting failed"
            print(f"  ✓ Text splitting successful ({len(chunks)} chunks)")
            
            # Test 4: Document info
            if test_file.exists():
                info = processor.get_document_info(str(test_file))
                assert info["supported"], "Document should be supported"
                assert info["name"] == "ai_basics.txt", "Wrong file name"
                print("  ✓ Document info extraction successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Document processor test failed: {e}")
            return False
    
    def test_vector_store(self) -> bool:
        """Test vector store functionality"""
        try:
            # Create vector store with temporary index
            vector_store = VectorStore(index_path="test_vector_index")
            
            # Test 1: Empty store stats
            stats = vector_store.get_stats()
            assert stats["total_documents"] == 0, "New store should be empty"
            print("  ✓ Empty store initialization correct")
            
            # Test 2: Add documents
            test_texts = [
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks with multiple layers.",
                "RAG combines retrieval with generation for better answers."
            ]
            test_metadata = [{"source": f"test_doc_{i}.txt"} for i in range(len(test_texts))]
            
            vector_store.add_documents(test_texts, test_metadata)
            
            stats = vector_store.get_stats()
            assert stats["total_documents"] == 3, f"Expected 3 documents, got {stats['total_documents']}"
            print(f"  ✓ Document addition successful ({stats['total_documents']} documents)")
            
            # Test 3: Search functionality
            results = vector_store.search("machine learning", top_k=2)
            assert len(results) >= 1, "Search should return results"
            assert results[0][1] > 0.5, "Top result should have good similarity score"
            print(f"  ✓ Search functionality working ({len(results)} results)")
            
            # Test 4: Clear store
            vector_store.clear()
            stats = vector_store.get_stats()
            assert stats["total_documents"] == 0, "Store should be empty after clear"
            print("  ✓ Store clearing successful")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Vector store test failed: {e}")
            return False
    
    def test_rag_pipeline(self) -> bool:
        """Test RAG pipeline functionality"""
        try:
            pipeline = RAGPipeline(self.YOUR_HF_TOKEN_HERE)
            
            # Test 1: Model connection
            connection_test = pipeline.test_model_connection()
            if not connection_test:
                print("  ⚠ Model connection test failed, but continuing...")
            else:
                print("  ✓ Model connection successful")
            
            # Test 2: Answer generation with mock documents
            from langchain.schema import Document
            
            mock_docs = [
                (Document(page_content="Machine learning is a method of data analysis that automates analytical model building.", 
                         metadata={"source": "ml_doc.txt"}), 0.9),
                (Document(page_content="Supervised learning uses labeled training data to learn a mapping from inputs to outputs.", 
                         metadata={"source": "supervised_doc.txt"}), 0.8)
            ]
            
            question = "What is machine learning?"
            answer = pipeline.generate_answer(question, mock_docs, max_tokens=100)
            
            assert len(answer) > 10, "Answer should be substantial"
            assert not answer.startswith("Error"), "Answer should not be an error message"
            print(f"  ✓ Answer generation successful (length: {len(answer)})")
            
            return True
            
        except Exception as e:
            print(f"  ❌ RAG pipeline test failed: {e}")
            return False
    
    def test_integration(self) -> bool:
        """Test full integration of all components"""
        try:
            # Initialize all components
            processor = DocumentProcessor()
            vector_store = VectorStore(index_path="integration_test_index")
            pipeline = RAGPipeline(self.YOUR_HF_TOKEN_HERE)
            
            # Load test documents
            data_dir = Path("data")
            if not data_dir.exists():
                print("  ⚠ Data directory not found, skipping integration test")
                return True
            
            loaded_docs = 0
            for file_path in data_dir.glob("*.txt"):
                try:
                    # Process document
                    text = processor.extract_text(str(file_path))
                    chunks = processor.split_text(text, chunk_size=500, chunk_overlap=100)
                    
                    # Add to vector store
                    metadata = [{"source": str(file_path)}] * len(chunks)
                    vector_store.add_documents(chunks, metadata)
                    loaded_docs += 1
                    
                except Exception as e:
                    print(f"  ⚠ Failed to process {file_path}: {e}")
            
            print(f"  ✓ Loaded {loaded_docs} documents")
            
            # Test search and retrieval
            test_query = "What is artificial intelligence?"
            search_results = vector_store.search(test_query, top_k=3)
            
            if search_results:
                print(f"  ✓ Search returned {len(search_results)} results")
                
                # Generate answer
                answer = pipeline.generate_answer(test_query, search_results, max_tokens=200)
                print(f"  ✓ Generated answer: {answer[:100]}...")
                
                # Clean up
                vector_store.clear()
                return True
            else:
                print("  ⚠ No search results found")
                return False
            
        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result["status"] == "ERROR")
        
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_emoji} {test_name}: {result['status']}")
            if result["error"]:
                print(f"    Error: {result['error']}")
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! RAG system is ready to use.")
        else:
            print(f"\n⚠ {failed_tests + error_tests} test(s) failed. Please check the issues above.")

def main():
    """Main function to run all tests"""
    # Configuration
    HF_TOKEN = Config.get_YOUR_HF_TOKEN_HERE()
    
    if not HF_TOKEN or HF_TOKEN == "your-token-here":
        print("❌ Please set a valid Hugging Face token in the script")
        return
    
    tester = RAGSystemTester(HF_TOKEN)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
