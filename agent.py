"""JARVIS-like File Management Agent using Open Source LLM (Ollama)"""
import json
import requests
from typing import Dict, Any, Optional
from file_manager import FileManager
import config


class OllamaClient:
    """Client for Ollama API (open source LLM)"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models_url = f"{base_url}/api/tags"
        self.generate_url = f"{base_url}/api/generate"
    
    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(self.models_url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, model: str, prompt: str, stream: bool = False) -> str:
        """Generate response from Ollama model"""
        try:
            response = requests.post(
                self.generate_url,
                json={"model": model, "prompt": prompt, "stream": stream},
                timeout=300
            )
            response.raise_for_status()
            
            if stream:
                result = ""
                for line in response.iter_lines():
                    if line:
                        result += json.loads(line).get("response", "")
                return result
            else:
                return response.json().get("response", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running. Download from https://ollama.ai"
            )
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")


class FileManagementAgent:
    """JARVIS-like agent for handling file-related queries"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.llm_client = None
        self.model = config.AGENT_MODEL
        self.conversation_history = []
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM client (Ollama)"""
        if config.LLM_PROVIDER == "ollama":
            self.llm_client = OllamaClient(config.OLLAMA_API_URL)
            
            # Check connection
            if not self.llm_client.check_connection():
                raise ConnectionError(
                    f"Cannot connect to Ollama at {config.OLLAMA_API_URL}\n"
                    "Make sure Ollama is installed and running:\n"
                    "1. Download from https://ollama.ai\n"
                    "2. Run: ollama run llama2\n"
                    "   (or: ollama run mistral, ollama run neural-chat, etc.)"
                )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
    
    def process_query(self, user_query: str) -> str:
        """
        Process a user query and return a response
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Response from the agent
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Build prompt with conversation history
        system_prompt = self._get_system_prompt()
        
        # Format conversation history as context
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history[-6:]  # Keep last 6 messages for context
        ])
        
        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{history_text}

ASSISTANT:"""
        
        try:
            agent_response = self.llm_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False
            ).strip()
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            return agent_response
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            if config.DEBUG:
                print(f"DEBUG: {error_msg}")
            return error_msg
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt for the agent"""
        return """You are JARVIS, an intelligent file management assistant similar to Iron Man's AI. 
You are helpful, professional, and knowledgeable about file systems.

Your capabilities include:
1. List files and directories in any path
2. Get detailed file information (size, modification date, creation date, etc.)
3. Search for files by name or pattern
4. Find large files in a directory
5. Find recently modified files
6. Provide analysis about file system structure and organization

When a user asks about files, you should:
- Understand their intent
- Use your file management capabilities to gather information
- Present the results in a clear, organized manner
- Provide helpful insights and recommendations

Always be polite and efficient, like a professional assistant would be."""
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
    
    def execute_file_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific file operation
        
        Args:
            operation: Name of the operation (list, search, get_info, large_files, recent_files)
            **kwargs: Arguments for the operation
            
        Returns:
            Result of the file operation
        """
        operations = {
            "list": self.file_manager.list_directory,
            "search": self.file_manager.search_files,
            "get_info": self.file_manager.get_file_info,
            "large_files": self.file_manager.get_large_files,
            "recent_files": self.file_manager.get_recent_files,
        }
        
        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}
        
        try:
            result = operations[operation](**kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
