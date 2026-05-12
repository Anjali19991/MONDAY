"""File management utilities for JARVIS agent"""
import os
import pathlib
from datetime import datetime
from typing import List, Dict, Any, Optional


class FileManager:
    """Handles all file system operations and metadata retrieval"""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
    
    def list_directory(self, path: str) -> List[Dict[str, Any]]:
        """
        List all files and directories in a given path
        
        Args:
            path: Directory path to list
            
        Returns:
            List of file/directory information dicts
        """
        try:
            path_obj = pathlib.Path(path)
            if not path_obj.exists():
                return []
            
            items = []
            for item in sorted(path_obj.iterdir()):
                items.append(self._get_item_info(item))
            return items
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            path_obj = pathlib.Path(file_path)
            if not path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            return self._get_item_info(path_obj, detailed=True)
        except Exception as e:
            return {"error": str(e)}
    
    def search_files(self, directory: str, pattern: str) -> List[Dict[str, Any]]:
        """
        Search for files matching a pattern
        
        Args:
            directory: Root directory to search in
            pattern: File name pattern (supports wildcards)
            
        Returns:
            List of matching files
        """
        try:
            path_obj = pathlib.Path(directory)
            if not path_obj.exists():
                return []
            
            import fnmatch
            matches = []
            max_depth = 3  # Limit search depth
            
            def search_recursive(current_path, depth):
                if depth > max_depth or len(matches) > 100:  # Limit results
                    return
                try:
                    for item in current_path.iterdir():
                        if len(matches) > 100:
                            break
                        try:
                            if item.is_file() and fnmatch.fnmatch(item.name, pattern):
                                matches.append(self._get_item_info(item))
                            elif item.is_dir() and depth < max_depth:
                                search_recursive(item, depth + 1)
                        except (PermissionError, OSError):
                            continue
                except (PermissionError, OSError):
                    pass
            
            search_recursive(path_obj, 0)
            return matches[:100]  # Return max 100 results
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_large_files(self, directory: str, min_size_mb: float = 10) -> List[Dict[str, Any]]:
        """
        Find large files in a directory
        
        Args:
            directory: Root directory to search in
            min_size_mb: Minimum file size in megabytes
            
        Returns:
            List of large files sorted by size
        """
        try:
            path_obj = pathlib.Path(directory)
            if not path_obj.exists():
                return []
            
            min_bytes = min_size_mb * 1024 * 1024
            large_files = []
            max_depth = 2  # Limit search depth
            
            def search_recursive(current_path, depth):
                if depth > max_depth or len(large_files) > 50:  # Limit to 50 files
                    return
                try:
                    for item in current_path.iterdir():
                        if len(large_files) > 50:
                            break
                        try:
                            if item.is_file():
                                if item.stat().st_size > min_bytes:
                                    large_files.append(self._get_item_info(item, detailed=True))
                            elif item.is_dir() and depth < max_depth:
                                search_recursive(item, depth + 1)
                        except (PermissionError, OSError):
                            continue
                except (PermissionError, OSError):
                    pass
            
            search_recursive(path_obj, 0)
            
            # Sort by size descending
            large_files.sort(key=lambda x: x.get("size_mb", 0), reverse=True)
            return large_files[:50]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_recent_files(self, directory: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Find recently modified files
        
        Args:
            directory: Root directory to search in
            hours: Look for files modified in the last N hours
            
        Returns:
            List of recently modified files
        """
        try:
            path_obj = pathlib.Path(directory)
            if not path_obj.exists():
                return []
            
            from time import time
            current_time = time()
            cutoff_time = current_time - (hours * 3600)
            
            recent_files = []
            max_depth = 2  # Limit search depth
            
            def search_recursive(current_path, depth):
                if depth > max_depth or len(recent_files) > 50:  # Limit to 50 files
                    return
                try:
                    for item in current_path.iterdir():
                        if len(recent_files) > 50:
                            break
                        try:
                            if item.is_file() and item.stat().st_mtime > cutoff_time:
                                recent_files.append(self._get_item_info(item, detailed=True))
                            elif item.is_dir() and depth < max_depth:
                                search_recursive(item, depth + 1)
                        except (PermissionError, OSError):
                            continue
                except (PermissionError, OSError):
                    pass
            
            search_recursive(path_obj, 0)
            
            # Sort by modification time descending
            recent_files.sort(key=lambda x: x.get("modified_timestamp", 0), reverse=True)
            return recent_files[:50]
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_item_info(self, path: pathlib.Path, detailed: bool = False) -> Dict[str, Any]:
        """
        Get information about a file or directory
        
        Args:
            path: pathlib.Path object
            detailed: Include additional metadata
            
        Returns:
            Dictionary with item information
        """
        try:
            stat = path.stat()
            is_dir = path.is_dir()
            
            info = {
                "name": path.name,
                "path": str(path),
                "type": "directory" if is_dir else "file",
                "size_bytes": stat.st_size if not is_dir else 0,
            }
            
            if detailed or path.is_file():
                info["size_mb"] = round(stat.st_size / (1024 * 1024), 2)
                info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                info["modified_timestamp"] = stat.st_mtime
                info["created"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                info["extension"] = path.suffix if not is_dir else ""
            
            return info
        except Exception as e:
            return {"error": str(e), "path": str(path)}
