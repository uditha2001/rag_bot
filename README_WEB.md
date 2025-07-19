# RAG Bot - Web Application

## 🌟 Complete React UI + FastAPI Backend

Your RAG Bot now has a beautiful, modern web interface! This includes:

### ✨ **Features**

#### 🎨 **React Frontend**

- **Modern Chat Interface** - Real-time messaging with typing indicators
- **Document Search** - Semantic search with highlighted results
- **File Upload** - Drag & drop support for TXT, PDF, DOCX files
- **System Statistics** - Real-time stats and document management
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Beautiful UI** - Built with Tailwind CSS and Lucide icons

#### 🚀 **FastAPI Backend**

- **REST API** - Clean API endpoints for all functionality
- **CORS Support** - Ready for production deployment
- **File Processing** - Automatic document processing pipeline
- **Error Handling** - Robust error handling and logging
- **Health Checks** - Connection monitoring

### 📁 **Project Structure**

```
d:\aiCourse\Rag-Bot\
├── web_ui/                    # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ChatInterface.js
│   │   │   ├── SearchInterface.js
│   │   │   ├── DocumentUpload.js
│   │   │   └── SystemStats.js
│   │   ├── App.js            # Main App component
│   │   ├── api.js            # API client
│   │   └── index.css         # Styles
│   ├── public/               # Static files
│   └── package.json          # Dependencies
├── web_server.py             # FastAPI backend
├── start_web_app.bat         # Windows startup script
├── start_web_app.sh          # Linux/Mac startup script
└── README_WEB.md             # This file
```

## 🚀 **How to Run**

### **Option 1: Automatic Startup (Recommended)**

#### Windows:

```bash
# Double-click or run:
start_web_app.bat
```

#### Linux/Mac:

```bash
chmod +x start_web_app.sh
./start_web_app.sh
```

### **Option 2: Manual Startup**

#### 1. Start Backend Server

```bash
# In the project root
python web_server.py
```

#### 2. Start React Frontend

```bash
# In a new terminal
cd web_ui
npm install  # First time only
npm start
```

### **Option 3: Production Build**

```bash
# Build React for production
cd web_ui
npm run build

# The FastAPI server will serve the built React app
python web_server.py
```

## 🌐 **Access URLs**

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 **API Endpoints**

| Method | Endpoint      | Description         |
| ------ | ------------- | ------------------- |
| GET    | `/`           | Health check        |
| POST   | `/api/ask`    | Ask a question      |
| POST   | `/api/search` | Search documents    |
| GET    | `/api/stats`  | Get system stats    |
| POST   | `/api/upload` | Upload documents    |
| DELETE | `/api/clear`  | Clear all documents |

## 🎯 **Features Overview**

### 💬 **Chat Interface**

- Real-time chat with your documents
- Source attribution for answers
- Typing indicators and message timestamps
- Mobile-responsive design

### 🔍 **Search Interface**

- Semantic search through documents
- Highlighted search terms
- Similarity scores
- Search tips and suggestions

### 📄 **Document Upload**

- Drag & drop file upload
- Progress indicators
- Batch file processing
- Supported formats: TXT, PDF, DOCX

### 📊 **System Statistics**

- Document count and statistics
- Vector store information
- Source file listing
- Clear all documents functionality

## 🛠 **Configuration**

### **Environment Variables**

```bash
# Optional: Set custom API URL for frontend
REACT_APP_API_URL=http://your-backend-url:8000
```

### **Hugging Face Token**

Update the token in `web_server.py`:

```python
HF_TOKEN = "your-hugging-face-token-here"
```

## 🎨 **UI Screenshots**

### Chat Interface

- Clean, modern chat design
- Real-time messaging
- Source attribution
- Mobile responsive

### Search Interface

- Semantic search results
- Highlighted matching text
- Similarity scores
- Clean result cards

### Upload Interface

- Drag & drop support
- File validation
- Progress indicators
- Batch processing

### Statistics Dashboard

- System metrics
- Document overview
- Management controls
- Real-time updates

## 🔧 **Development**

### **Frontend Development**

```bash
cd web_ui
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
```

### **Backend Development**

```bash
# Auto-reload during development
uvicorn web_server:app --reload --host 0.0.0.0 --port 8000
```

### **Customization**

- **Styling**: Edit `web_ui/src/index.css` and Tailwind classes
- **Components**: Modify files in `web_ui/src/components/`
- **API**: Update endpoints in `web_server.py`
- **Theme**: Customize colors in `web_ui/tailwind.config.js`

## 📱 **Mobile Support**

The web app is fully responsive and works great on:

- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ Touch interfaces

## 🚀 **Deployment**

### **Development**

```bash
# Both frontend and backend on localhost
./start_web_app.sh
```

### **Production**

```bash
# Build React for production
cd web_ui && npm run build

# Run FastAPI server (serves both API and React app)
python web_server.py
```

### **Docker** (Optional)

```dockerfile
# You can create a Docker setup for easy deployment
FROM node:18 AS frontend
WORKDIR /app/web_ui
COPY web_ui/package*.json ./
RUN npm install
COPY web_ui/ ./
RUN npm run build

FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
COPY --from=frontend /app/web_ui/build ./web_ui/build
EXPOSE 8000
CMD ["python", "web_server.py"]
```

## 🎉 **Success!**

Your RAG Bot now has a complete web interface! You can:

✅ **Chat with your documents** through a beautiful interface  
✅ **Upload new documents** with drag & drop  
✅ **Search semantically** through your knowledge base  
✅ **Monitor system stats** in real-time  
✅ **Access from any device** with responsive design  
✅ **Deploy anywhere** with the production build

The system is production-ready and can be deployed to any web server or cloud platform!

## 🆘 **Troubleshooting**

### Backend Won't Start

- Check if port 8000 is available
- Verify Python dependencies are installed
- Check the console for error messages

### Frontend Won't Start

- Ensure Node.js is installed
- Run `npm install` in the web_ui directory
- Check if port 3000 is available

### API Connection Failed

- Make sure backend is running on http://localhost:8000
- Check CORS settings in web_server.py
- Verify firewall settings

### File Upload Issues

- Check file size limits
- Verify supported file formats
- Ensure proper file permissions

---

**🎊 Congratulations! Your RAG Bot is now a full-featured web application!** 🎊
