"""
Configuration management for RAG Bot
Loads environment variables and provides default values
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class Config:
    """Configuration class for RAG Bot"""
    
    # Hugging Face Configuration
    HF_TOKEN = os.getenv('HF_TOKEN')
    
    # Server Configuration
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))
    
    # Development Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    INDEX_PATH = os.path.join(os.path.dirname(__file__), 'simple_rag_index')
    
    # Model Configuration
    DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_GENERATION_MODEL = "microsoft/DialoGPT-medium"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is required. Please set it in .env file or environment variables. "
                "Get your token from: https://huggingface.co/settings/tokens"
            )
        
        if cls.HF_TOKEN == "your-hugging-face-token-here":
            raise ValueError(
                "Please set your actual Hugging Face token in .env file. "
                "Get your token from: https://huggingface.co/settings/tokens"
            )
    
    @classmethod
    def get_YOUR_HF_TOKEN_HERE(cls):
        """Get HF token with validation"""
        cls.validate()
        return cls.HF_TOKEN

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
