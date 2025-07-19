#!/usr/bin/env python3
"""
Setup script for RAG Bot
Helps users get started quickly
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_node_version():
    """Check if Node.js is available"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Node.js not found. React UI will not be available.")
    print("   Install Node.js from: https://nodejs.org/")
    return False

def setup_environment():
    """Set up Python virtual environment"""
    print("\n📦 Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("virtualenv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "virtualenv"])
    
    # Determine the correct activation script
    if os.name == 'nt':  # Windows
        python_exe = os.path.join("virtualenv", "Scripts", "python.exe")
        pip_exe = os.path.join("virtualenv", "Scripts", "pip.exe")
    else:  # Unix-like
        python_exe = os.path.join("virtualenv", "bin", "python")
        pip_exe = os.path.join("virtualenv", "bin", "pip")
    
    # Install requirements
    print("Installing Python dependencies...")
    result = subprocess.run([pip_exe, "install", "-r", "requirements.txt"])
    
    if result.returncode == 0:
        print("✅ Python dependencies installed successfully")
        return python_exe
    else:
        print("❌ Failed to install Python dependencies")
        return None

def setup_config():
    """Set up configuration file"""
    print("\n🔧 Setting up configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env and add your Hugging Face token!")
        print("   Get token from: https://huggingface.co/settings/tokens")
        return False
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ No .env.example file found")
        return False

def setup_react():
    """Set up React UI"""
    if not check_node_version():
        return False
    
    print("\n⚛️  Setting up React UI...")
    
    os.chdir("web_ui")
    try:
        result = subprocess.run(["npm", "install"])
        if result.returncode == 0:
            print("✅ React dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install React dependencies")
            return False
    except Exception as e:
        print(f"❌ Error setting up React: {e}")
        return False
    finally:
        os.chdir("..")

def test_setup(python_exe):
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        # Test config import
        result = subprocess.run([
            python_exe, "-c", 
            "from config import Config; print('✅ Configuration system working')"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Configuration test failed:", result.stderr)
            return False
        
        # Test core imports
        result = subprocess.run([
            python_exe, "-c",
            "from mcp_servers.rag_server.vector_store import VectorStore; print('✅ Core modules working')"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Core module test failed:", result.stderr)
            return False
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*50)
    print("🎉 Setup Complete! Next Steps:")
    print("="*50)
    
    print("\n1. 🔑 Configure your Hugging Face token:")
    print("   - Edit .env file")
    print("   - Add: HF_TOKEN=your-token-here")
    print("   - Get token: https://huggingface.co/settings/tokens")
    
    print("\n2. 🚀 Run the application:")
    print("   Option A - React UI:")
    print("     Terminal 1: python web_server.py")
    print("     Terminal 2: cd web_ui && npm start")
    print("     Access: http://localhost:3000")
    
    print("\n   Option B - Simple Web:")
    print("     python simple_web_app.py")
    print("     Access: http://localhost:8000")
    
    print("\n3. 📚 Add documents:")
    print("   - Use the web interface to upload files")
    print("   - Supports: TXT, PDF, DOCX")
    
    print("\n4. 💬 Start chatting:")
    print("   - Ask questions about your documents")
    print("   - Try general knowledge questions too!")
    
    print("\n📖 For more help, see README.md")

def main():
    """Main setup function"""
    print("🤖 RAG Bot Setup Script")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    has_node = check_node_version()
    
    # Setup environment
    python_exe = setup_environment()
    if not python_exe:
        print("❌ Failed to set up Python environment")
        sys.exit(1)
    
    # Setup configuration
    setup_config()
    
    # Setup React if available
    if has_node:
        setup_react()
    
    # Test setup
    if not test_setup(python_exe):
        print("❌ Setup validation failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
