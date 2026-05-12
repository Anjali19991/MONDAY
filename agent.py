"""JARVIS-like File Management Agent using Open Source LLM (Ollama)"""
import json
import requests
from typing import Dict, Any, Optional
from file_manager import FileManager
import config
from logger_util import log_step, log_success, log_error, log_file_operation


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
        log_step("Processing query", f"'{user_query}'")
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Try to extract intent and execute file operations
        log_step("Detecting intent", "Checking for file operations...")
        response = self._execute_with_intent(user_query)
        
        if response:
            log_success(f"Intent detected and executed")
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response
        
        log_step("No file operation detected", "Using LLM for response...")
        
        # Fallback to LLM if no file operation detected
        system_prompt = self._get_system_prompt()
        
        # Build a very simple prompt
        user_msg = user_query
        
        full_prompt = f"""{system_prompt}

User: {user_msg}
Assistant: """
        
        try:
            log_step("Calling LLM", f"Model: {self.model}")
            agent_response = self.llm_client.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False
            ).strip()
            
            log_success("LLM response received")
            
            # Clean up response - remove any system instructions that leaked
            agent_response = agent_response.split("User:")[0].strip()
            agent_response = agent_response.split("System:")[0].strip()
            
            # Truncate very long responses
            if len(agent_response) > 300:
                agent_response = agent_response[:300].rsplit(' ', 1)[0] + "..."
            
            # Remove any remaining instruction text
            lines = agent_response.split('\n')
            if lines:
                agent_response = lines[0]  # Just take first line
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            return agent_response
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            log_error(error_msg)
            if config.DEBUG:
                import traceback
                traceback.print_exc()
            return error_msg
    
    def _execute_with_intent(self, query: str) -> Optional[str]:
        """
        Try to detect user intent and execute file operations directly
        
        Args:
            query: User query
            
        Returns:
            Response if operation executed, None otherwise
        """
        query_lower = query.lower().strip()
        
        # Ignore simple greetings and general chat - don't try to extract intent
        greetings = ["hi", "hello", "hey", "how are you", "what's up", "help", "?"]
        if any(query_lower == greeting or query_lower.startswith(greeting + " ") for greeting in greetings):
            return None  # Let LLM handle greetings
        
        # List directory
        if any(word in query_lower for word in ["list", "show", "files in", "directory", "folder", "contents", "what's in"]):
            if any(keyword in query_lower for keyword in ["c:\\", "d:\\", "e:\\", "/users", "/home", "downloads", "documents", "desktop", "project"]):
                path = self._extract_path(query)
                if path:
                    log_step("Listing directory", path)
                    files = self.file_manager.list_directory(path)
                    log_file_operation("Listed", path, len(files))
                    return self._format_file_list(files, f"📁 Files in {path}")
        
        # Get file info
        if any(word in query_lower for word in ["info", "details", "properties", "about", "tell me about"]):
            if any(char in query for char in ["\\", "/"]) or any(ext in query_lower for ext in [".txt", ".pdf", ".doc", ".exe", ".py", ".json"]):
                path = self._extract_path(query)
                if path:
                    log_step("Getting file info", path)
                    info = self.file_manager.get_file_info(path)
                    log_success(f"Retrieved info for {path}")
                    return self._format_file_info(info)
        
        # Search files
        if any(word in query_lower for word in ["search", "find", "locate", "look for"]):
            if "*." in query or any(ext in query_lower for ext in [".pdf", ".txt", ".doc", ".exe", ".py"]):
                directory, pattern = self._extract_search_params(query)
                if directory and pattern:
                    log_step("Searching files", f"Pattern: {pattern} in {directory}")
                    files = self.file_manager.search_files(directory, pattern)
                    log_file_operation("Search", pattern, len(files))
                    return self._format_file_list(files, f"🔍 Search results for '{pattern}'")
        
        # Large files
        if any(word in query_lower for word in ["large", "big", "biggest", "size", "storage", "disk space"]):
            if "file" in query_lower or "folder" in query_lower or any(char in query for char in ["\\", "/"]):
                directory = self._extract_path(query)
                if directory:
                    log_step("Finding large files", directory)
                    files = self.file_manager.get_large_files(directory)
                    log_file_operation("Found large files", directory, len(files))
                    return self._format_file_list(files, f"📦 Largest files in {directory}")
        
        # Recent files / today's files
        if any(word in query_lower for word in ["recent", "modified", "changed", "updated", "latest", "new", "today", "generated", "created"]):
            directory = self._extract_path(query)
            # If no path found, use current directory
            if not directory:
                directory = "C:\\Users\\darkp"
            
            log_step("Finding recent files", directory)
            files = self.file_manager.get_recent_files(directory, hours=24)
            log_file_operation("Found recent", directory, len(files))
            if files and not any("error" in f for f in files):
                return self._format_file_list(files, f"⏰ Files created/modified today in {directory}")
        
        return None
    
    def _extract_path(self, query: str) -> Optional[str]:
        """Extract file path from query"""
        import re
        # Look for paths like C:\Users\... or /path/to/file
        paths = re.findall(r'[A-Z]:\\[^"<>|]*|/[^"<>|]*', query)
        if paths:
            path = paths[0].strip().rstrip('/')
            if path:
                return path
        
        # Check for common directory names with context
        query_lower = query.lower()
        common_dirs = {
            "downloads": "C:\\Users\\darkp\\Downloads",
            "documents": "C:\\Users\\darkp\\Documents",
            "desktop": "C:\\Users\\darkp\\Desktop",
            "projects": "c:\\Users\\darkp\\Downloads\\projects\\MONDAY",
            "project": "c:\\Users\\darkp\\Downloads\\projects\\MONDAY",
            "monday": "c:\\Users\\darkp\\Downloads\\projects\\MONDAY",
            "home": "C:\\Users\\darkp",
            "user": "C:\\Users\\darkp"
        }
        
        for keyword, path in common_dirs.items():
            if keyword in query_lower:
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
        
        output = f"\n{title}\n" + "=" * 60 + "\n"
        
        for i, file in enumerate(files[:30], 1):  # Show up to 30 files
            if "error" in file:
                continue
            
            name = file.get("name", "Unknown")
            file_type = file.get("type", "unknown")
            size_mb = file.get("size_mb", 0)
            modified = file.get("modified", "Unknown")
            
            if file_type == "directory":
                icon = "📁"
                size_str = "-"
            else:
                icon = "📄"
                size_str = f"{size_mb}MB" if size_mb > 0 else "0B"
            
            output += f"{i:2d}. {icon} {name:<40} {size_str:>8}  ({modified})\n"
        
        if len(files) > 30:
            output += f"\n... and {len(files) - 30} more files\n"
        
        output += "\n"
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
        return """You are JARVIS, a file management assistant.
Keep responses SHORT (1-2 sentences max).
For chats: respond naturally.
For file queries: show actual files only."""
    
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
