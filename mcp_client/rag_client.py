import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# MCP client imports
from mcp import ClientSession
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class RAGClient:
    """Client for interacting with the RAG MCP server"""
    
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session: ClientSession = None
        
    async def connect(self):
        """Connect to the RAG server"""
        try:
            # Start the server process
            server_params = {
                "command": "python",
                "args": [self.server_script_path]
            }
            
            self.session = await stdio_client(server_params)
            await self.session.initialize()
            
            logger.info("Connected to RAG server")
            
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.session:
            await self.session.close()
    
    async def load_documents(self, file_paths: List[str]) -> str:
        """Load documents into the RAG system"""
        try:
            result = await self.session.call_tool(
                "load_documents",
                {"file_paths": file_paths}
            )
            return result.content[0].text if result.content else "No response"
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return f"Error: {str(e)}"
    
    async def search_documents(self, query: str, top_k: int = 5) -> str:
        """Search for relevant documents"""
        try:
            result = await self.session.call_tool(
                "search_documents",
                {"query": query, "top_k": top_k}
            )
            return result.content[0].text if result.content else "No results found"
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return f"Error: {str(e)}"
    
    async def ask_question(self, question: str, max_tokens: int = 512) -> str:
        """Ask a question using RAG"""
        try:
            result = await self.session.call_tool(
                "ask_question",
                {"question": question, "max_tokens": max_tokens}
            )
            return result.content[0].text if result.content else "No answer generated"
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return f"Error: {str(e)}"
    
    async def get_summary(self) -> str:
        """Get summary of the document store"""
        try:
            result = await self.session.call_tool("get_document_summary", {})
            return result.content[0].text if result.content else "No summary available"
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return f"Error: {str(e)}"
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        try:
            resources = await self.session.list_resources()
            return [{"uri": str(r.uri), "name": r.name, "description": r.description} 
                   for r in resources.resources]
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []

# Interactive CLI for testing
class RAGChatInterface:
    """Interactive chat interface for the RAG system"""
    
    def __init__(self, client: RAGClient):
        self.client = client
        
    async def run(self):
        """Run the interactive chat interface"""
        print("🤖 RAG Bot - Interactive Chat Interface")
        print("Commands:")
        print("  /load <file_path> - Load a document")
        print("  /search <query> - Search documents")
        print("  /summary - Get document summary")
        print("  /help - Show this help")
        print("  /quit - Exit")
        print("  Or just ask any question!\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['/quit', '/exit']:
                    break
                elif user_input.startswith('/load '):
                    file_path = user_input[6:].strip()
                    result = await self.client.load_documents([file_path])
                    print(f"Bot: {result}")
                elif user_input.startswith('/search '):
                    query = user_input[8:].strip()
                    result = await self.client.search_documents(query)
                    print(f"Bot: {result}")
                elif user_input == '/summary':
                    result = await self.client.get_summary()
                    print(f"Bot: {result}")
                elif user_input == '/help':
                    print("Commands:")
                    print("  /load <file_path> - Load a document")
                    print("  /search <query> - Search documents")
                    print("  /summary - Get document summary")
                    print("  /help - Show this help")
                    print("  /quit - Exit")
                    print("  Or just ask any question!")
                else:
                    # Regular question
                    result = await self.client.ask_question(user_input)
                    print(f"Bot: {result}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye! 👋")

async def main():
    """Main function to run the client"""
    # Path to the RAG server script
    server_script = Path(__file__).parent / "rag_server" / "server.py"
    
    client = RAGClient(str(server_script))
    
    try:
        await client.connect()
        
        # Create and run the chat interface
        chat = RAGChatInterface(client)
        await chat.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the client
    asyncio.run(main())
