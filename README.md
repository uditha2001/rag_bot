# 🤖 RAG Bot - Intelligent Document Q&A System

A powerful Retrieval-Augmented Generation (RAG) chatbot that can answer questions about your documents using state-of-the-art AI models. Built with FastAPI, React, and Hugging Face Transformers.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HuggingFace](https://img.shields.io/badge/🤗-Hugging%20Face-yellow)](https://huggingface.co/)

## ✨ Features

- 📚 **Document Processing**: Supports TXT, PDF, and DOCX files
- 🔍 **Smart Search**: FAISS-powered vector similarity search
- 🧠 **Intelligent Responses**: Uses Hugging Face models for text generation
- 🌐 **Modern Web UI**: React-based interface with real-time chat
- 🔄 **MCP Protocol**: Model Context Protocol support for advanced integrations
- 🎯 **Hybrid Mode**: Handles both document-specific and general knowledge questions
- 📊 **System Statistics**: Monitor document count and system status
- 🔒 **Secure Configuration**: Environment-based API key management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for React UI)
- Hugging Face API Token ([Get one here](https://huggingface.co/settings/tokens))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/rag-bot.git
   cd rag-bot
   ```

2. **Set up Python environment**

   ```bash
   python -m venv virtualenv

   # On Windows:
   virtualenv\\Scripts\\activate

   # On Linux/Mac:
   source virtualenv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Hugging Face token:

   ```env
   HF_TOKEN=your-hugging-face-token-here
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8000
   DEBUG=True
   ```

4. **Run the application**

   **Option A: React Web UI (Recommended)**

   ```bash
   # Terminal 1: Start backend
   python web_server.py

   # Terminal 2: Start React UI
   cd web_ui
   npm install
   npm start
   ```

   Access at: http://localhost:3000

   **Option B: Simple Web Interface**

   ```bash
   python simple_web_app.py
   ```

   Access at: http://localhost:8000

## 📖 Usage

### Adding Documents

1. Use the web interface to upload TXT, PDF, or DOCX files
2. Documents are automatically processed and indexed
3. Start asking questions about your content!

### Example Questions

**Document-based questions:**

- "What is machine learning?"
- "Explain the types of neural networks"
- "How does the training process work?"

**General knowledge questions:**

- "What is Python programming?"
- "Tell me about artificial intelligence"
- "How do computers work?"

### REST API Usage

The system provides a REST API for programmatic access:

```python
import requests

# Ask a question
response = requests.post("http://localhost:8000/ask",
    json={"question": "What is machine learning?"})
print(response.json()["answer"])

# Upload a document
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/upload",
        files={"file": f})

# Search documents
response = requests.post("http://localhost:8000/search",
    json={"query": "neural networks", "top_k": 5})
print(response.json()["results"])
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │  RAG Pipeline   │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│  (AI Engine)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Document      │    │   Vector Store  │
                       │   Processor     │    │   (FAISS)       │
                       └─────────────────┘    └─────────────────┘
```

### Core Components

- **Document Processor**: Handles PDF, DOCX, and TXT files with intelligent chunking
- **Vector Store**: FAISS-based similarity search with persistence
- **RAG Pipeline**: Combines retrieval with Hugging Face generation models
- **Web Interface**: Modern React UI with real-time chat capabilities
- **MCP Server**: Model Context Protocol implementation for tool integration

## 🔧 Configuration

Key configuration options in `.env`:

```bash
# Required: Get from https://huggingface.co/settings/tokens
HF_TOKEN=your-hugging-face-token

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Development Settings
DEBUG=True
LOG_LEVEL=INFO
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_rag_system.py
```

Test specific components:

```bash
# Test document processing
python -c "from mcp_servers.rag_server.document_processor import DocumentProcessor; print('✅ Document processor working')"

# Test vector store
python -c "from mcp_servers.rag_server.vector_store import VectorStore; print('✅ Vector store working')"
```

## 📁 Project Structure

```
rag-bot/
├── 📄 README.md                 # Project documentation
├── 🔧 config.py                 # Configuration management
├── 📦 requirements.txt          # Python dependencies
├── 🌐 web_server.py             # FastAPI backend
├── 🕸️ simple_web_app.py        # Self-contained web interface
├── 🔍 test_rag_system.py        # Comprehensive test suite
├── 📚 data/                     # Sample documents
│   ├── ai_basics.txt
│   ├── machine_learning.txt
│   └── rag_explanation.txt
├── 🖥️ web_ui/                   # React frontend
│   ├── 📦 package.json
│   ├── 🎨 src/components/       # React components
│   │   ├── ChatInterface.js
│   │   ├── SearchInterface.js
│   │   ├── DocumentUpload.js
│   │   └── SystemStats.js
│   └── 🎯 public/
├── 🔌 mcp_servers/              # MCP Protocol implementation
│   ├── 📡 main.py
│   └── 🤖 rag_server/
│       ├── 📄 document_processor.py
│       ├── 🗃️ vector_store.py
│       ├── 🧠 rag_pipeline.py
│       └── 🖥️ server.py
├── 🔐 .env.example             # Environment template
└── 🔐 .env                     # Your environment variables (not in git)
```

## 🌟 Advanced Features

### MCP Protocol Support

Run as an MCP server for integration with other tools:

```bash
python mcp_servers/rag_server/server.py
```

### Custom Models

Modify `config.py` to use different Hugging Face models:

```python
# In config.py
DEFAULT_GENERATION_MODEL = "microsoft/DialoGPT-medium"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### Batch Document Processing

Process multiple documents programmatically:

```python
from mcp_servers.rag_server.document_processor import DocumentProcessor
from mcp_servers.rag_server.vector_store import VectorStore

processor = DocumentProcessor()
vector_store = VectorStore()

# Process all documents in a directory
import os
for filename in os.listdir("documents/"):
    if filename.endswith(('.txt', '.pdf', '.docx')):
        docs = processor.process_file(f"documents/{filename}")
        vector_store.add_documents(docs)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 pytest

# Run code formatting
black .

# Run linting
flake8 .

# Run tests
pytest
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Hugging Face Models](https://huggingface.co/models)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [FAISS Documentation](https://faiss.ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 🆘 Troubleshooting

### Common Issues

**1. "HF_TOKEN is required" Error**

- Make sure you've created `.env` file from `.env.example`
- Add your valid Hugging Face token
- Verify token is active at https://huggingface.co/settings/tokens

**2. "Port already in use" Error**

- Check if another process is using port 8000 or 3000
- Kill the process or change the port in configuration

**3. React UI not connecting to backend**

- Ensure both frontend (port 3000) and backend (port 8000) are running
- Check CORS settings in `web_server.py`

**4. Document upload fails**

- Verify the file format is supported (TXT, PDF, DOCX)
- Check file size limits
- Ensure proper permissions on upload directory

### Getting Help

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/rag-bot/issues) page
2. Review the configuration in `.env`
3. Ensure all dependencies are installed correctly
4. Verify your Hugging Face token is valid
5. Check the logs for error messages

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for providing excellent models and APIs
- [Facebook AI Research](https://ai.facebook.com/) for FAISS vector search
- [FastAPI](https://fastapi.tiangolo.com/) team for the amazing web framework
- [React](https://reactjs.org/) team for the frontend framework
- [LangChain](https://langchain.com/) for RAG framework inspiration
- The open-source community for all the amazing tools and libraries

---

## ⭐ Star this repo if you found it helpful!

Made with ❤️ for the AI community
