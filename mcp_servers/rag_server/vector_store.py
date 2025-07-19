import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import logging
from pathlib import Path
import pickle
import json

from sentence_transformers import SentenceTransformer
import faiss
from langchain.schema import Document

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document embeddings using FAISS"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", index_path: str = "vector_index"):
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.documents: List[Document] = []
        self.embeddings: List[np.ndarray] = []
        
        # Paths for persistence
        self.index_path = Path(index_path)
        self.index_path.mkdir(exist_ok=True)
        self.index_file = self.index_path / "faiss_index.bin"
        self.docs_file = self.index_path / "documents.pkl"
        self.metadata_file = self.index_path / "metadata.json"
        
        # Load existing index if available
        self._load_index()
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store"""
        try:
            # Create Document objects
            new_docs = [Document(page_content=text, metadata=metadata) 
                       for text, metadata in zip(texts, metadatas)]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store documents and embeddings
            self.documents.extend(new_docs)
            self.embeddings.extend(embeddings)
            
            logger.info(f"Added {len(texts)} documents to vector store")
            
            # Save index
            self._save_index()
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1:  # Valid index
                    results.append((self.documents[idx], float(score)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        sources = set()
        for doc in self.documents:
            if "source" in doc.metadata:
                sources.add(Path(doc.metadata["source"]).name)
        
        return {
            "total_documents": len(self.documents),
            "total_vectors": self.index.ntotal,
            "embedding_dimension": self.dimension,
            "embedding_model": self.embedding_model_name,
            "unique_sources": len(sources),
            "sources": list(sources)
        }
    
    def clear(self) -> None:
        """Clear all documents and reset index"""
        self.index.reset()
        self.documents.clear()
        self.embeddings.clear()
        
        # Remove saved files
        if self.index_file.exists():
            self.index_file.unlink()
        if self.docs_file.exists():
            self.docs_file.unlink()
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        
        logger.info("Vector store cleared")
    
    def _save_index(self) -> None:
        """Save the index and documents to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save documents
            with open(self.docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save metadata
            metadata = {
                "embedding_model": self.embedding_model_name,
                "dimension": self.dimension,
                "document_count": len(self.documents)
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("Vector store saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _load_index(self) -> None:
        """Load existing index and documents from disk"""
        try:
            if not all([self.index_file.exists(), self.docs_file.exists(), self.metadata_file.exists()]):
                logger.info("No existing index found, starting fresh")
                return
            
            # Load metadata first
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Verify compatibility
            if metadata["embedding_model"] != self.embedding_model_name:
                logger.warning("Embedding model mismatch, starting fresh")
                return
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load documents
            with open(self.docs_file, 'rb') as f:
                self.documents = pickle.load(f)
            
            logger.info(f"Loaded existing index with {len(self.documents)} documents")
            
        except Exception as e:
            logger.warning(f"Error loading existing index: {e}, starting fresh")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents.clear()
