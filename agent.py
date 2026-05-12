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
                    "2. Run: ollama run tinyllama\n"
                    "   (lightweight model, ~1.1GB, recommended)\n"
                    "   Or other models: ollama run gemma:2b, orca-mini, etc."
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
        
        # Try to extract intent and execute file operations
        response = self._execute_with_intent(user_query)
        if response:
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response
        
        # Fallback to LLM if no file operation detected
        system_prompt = self._get_system_prompt()
        
        # Format conversation history as context
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history[-6:]
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
    
    def _execute_with_intent(self, query: str) -> Optional[str]:
        """
        Try to detect user intent and execute file operations directly
        
        Args:
            query: User query
            
        Returns:
            Response if operation executed, None otherwise
        """
        query_lower = query.lower()
        
        # List directory
        if any(word in query_lower for word in ["list", "show", "files in", "directory", "folder", "contents"]):
            # Extract path from query
            path = self._extract_path(query)
            if path:
                files = self.file_manager.list_directory(path)
                return self._format_file_list(files, f"Files in {path}")
        
        # Get file info
        if any(word in query_lower for word in ["info", "details", "properties", "about"]) and ("file" in query_lower or "\\" in query or "/" in query):
            path = self._extract_path(query)
            if path:
                info = self.file_manager.get_file_info(path)
                return self._format_file_info(info)
        
        # Search files
        if any(word in query_lower for word in ["search", "find", "locate", "*.pdf", "*.txt", "*.doc"]):
            directory, pattern = self._extract_search_params(query)
            if directory and pattern:
                files = self.file_manager.search_files(directory, pattern)
                return self._format_file_list(files, f"Search results for '{pattern}' in {directory}")
        
        # Large files
        if any(word in query_lower for word in ["large", "big", "biggest", "size"]) and "file" in query_lower:
            directory = self._extract_path(query)
            if directory:
                files = self.file_manager.get_large_files(directory)
                return self._format_file_list(files, f"Large files in {directory}")
        
        # Recent files
        if any(word in query_lower for word in ["recent", "modified", "changed", "updated", "hours", "24"]):
            directory = self._extract_path(query)
            if directory:
                files = self.file_manager.get_recent_files(directory)
                return self._format_file_list(files, f"Recently modified files in {directory}")
        
        return None
    
    def _extract_path(self, query: str) -> Optional[str]:
        """Extract file path from query"""
        import re
        # Look for paths like C:\Users\... or /path/to/file
        paths = re.findall(r'[A-Z]:\\[^"<>|]+|/[^"<>|]+', query)
        if paths:
            return paths[0].strip()
        
        # Check for common directory names
        common_dirs = {
            "downloads": "C:\\Users\\darkp\\Downloads",
            "documents": "C:\\Users\\darkp\\Documents",
            "desktop": "C:\\Users\\darkp\\Desktop",
            "project": "c:\\Users\\darkp\\Downloads\\projects\\MONDAY"
        }
        for keyword, path in common_dirs.items():
            if keyword in query.lower():
                return path
        
        return None
    
    def _extract_search_params(self, query: str) -> tuple:
        """Extract directory and search pattern from query"""
        import re
        
        # Look for pattern like *.pdf
        patterns = re.findall(r'\*\.\w+', query)
        pattern = patterns[0] if patterns else None
        
        directory = self._extract_path(query)
        if not directory:
            directory = "c:\\Users\\darkp"  # Default
        
        return directory, pattern
    
    def _format_file_list(self, files: list, title: str) -> str:
        """Format file list for display"""
        if not files or (len(files) == 1 and "error" in files[0]):
            error = files[0].get("error", "No files found") if files else "No files found"
            return f"⚠️ {error}"
        
        output = f"📁 {title}\n" + "=" * 50 + "\n"
        
        for i, file in enumerate(files[:20], 1):  # Limit to 20 files
            name = file.get("name", "Unknown")
            file_type = file.get("type", "unknown")
            size_mb = file.get("size_mb", 0)
            modified = file.get("modified", "Unknown")
            
            size_str = f"{size_mb}MB" if size_mb > 0 else "DIR"
            output += f"{i}. [{file_type}] {name} ({size_str}) - Modified: {modified}\n"
        
        if len(files) > 20:
            output += f"\n... and {len(files) - 20} more files"
        
        return output
    
    def _format_file_info(self, info: dict) -> str:
        """Format file information for display"""
        if "error" in info:
            return f"⚠️ {info['error']}"
        
        output = f"📄 File Information\n" + "=" * 50 + "\n"
        output += f"Name: {info.get('name', 'Unknown')}\n"
        output += f"Type: {info.get('type', 'Unknown')}\n"
        output += f"Path: {info.get('path', 'Unknown')}\n"
        output += f"Size: {info.get('size_mb', 0)}MB\n"
        output += f"Modified: {info.get('modified', 'Unknown')}\n"
        output += f"Created: {info.get('created', 'Unknown')}\n"
        
        return output
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt for the agent"""
        return """You are JARVIS, an intelligent file management assistant similar to Iron Man's AI. 
You are helpful, professional, and knowledgeable about file systems.

IMPORTANT INSTRUCTIONS:
- When a user asks about files/directories, FIRST list what files exist
- Provide ACTUAL file data, not generic instructions
- Be concise and direct - no long explanations unless asked
- Format output clearly with file names, sizes, and dates

Your capabilities:
1. List files and directories in any path
2. Get detailed file information (size, modification date, creation date)
3. Search for files by name or pattern
4. Find large files in a directory
5. Find recently modified files
6. Provide analysis about file system

When responding:
- If user asks about a directory: Show actual files/folders with details
- If user asks to search: Show actual matching files
- If user asks about file info: Show actual metadata
- Be specific with real data, not hypothetical examples"""
    
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
