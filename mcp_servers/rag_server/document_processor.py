import os
from typing import List, Optional
from pathlib import Path
import logging

import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process different document types and extract text"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.pdf', '.docx'}
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return self._extract_from_txt(file_path)
        elif extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from .pdf file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            raise
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from .docx file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX {file_path}: {e}")
            raise
    
    def split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks for vector storage"""
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        if len(words) <= chunk_size:
            return [text]
        
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            
            # Break if we've reached the end
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def get_document_info(self, file_path: str) -> dict:
        """Get basic information about a document"""
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix,
            "modified": file_path.stat().st_mtime,
            "supported": file_path.suffix.lower() in self.supported_extensions
        }
