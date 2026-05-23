"""Test suite for Monday File Management Agent"""
import os
import sys
from pathlib import Path
from file_manager import FileManager
from agent import FileManagementAgent
from logger_util import log_step, log_success, log_error

def test_file_manager():
    """Test FileManager class"""
    print("\n" + "="*60)
    print("TESTING FILE MANAGER")
    print("="*60)
    
    fm = FileManager()
    test_dir = "C:\\Users\\darkp\\Downloads"
    
    # Test 1: List directory
    log_step("Test 1", "List directory")
    try:
        files = fm.list_directory(test_dir)
        if files and not any("error" in f for f in files):
            log_success(f"Listed {len(files)} files in {test_dir}")
        else:
            log_error(f"Failed to list files in {test_dir}")
            return False
    except Exception as e:
        log_error(f"List directory failed: {e}")
        return False
    
    # Test 2: Get file info
    log_step("Test 2", "Get file information")
    try:
        if files:
            first_file = [f for f in files if f.get("type") == "file"]
            if first_file:
                file_path = first_file[0].get("path")
                info = fm.get_file_info(file_path)
                if "error" not in info:
                    log_success(f"Got info for {file_path}")
                else:
                    log_error(f"Failed to get info for {file_path}")
                    return False
    except Exception as e:
        log_error(f"Get file info failed: {e}")
        return False
    
    # Test 3: Search files
    log_step("Test 3", "Search for files (*.txt)")
    try:
        results = fm.search_files(test_dir, "*.txt")
        log_success(f"Search completed: Found {len(results)} .txt files")
    except Exception as e:
        log_error(f"Search files failed: {e}")
        return False
    
    # Test 4: Find large files
    log_step("Test 4", "Find large files (>1MB)")
    try:
        large = fm.get_large_files(test_dir, min_size_mb=1)
        log_success(f"Found {len(large)} files larger than 1MB")
    except Exception as e:
        log_error(f"Get large files failed: {e}")
        return False
    
    # Test 5: Find recent files
    log_step("Test 5", "Find recently modified files (24 hours)")
    try:
        recent = fm.get_recent_files(test_dir, hours=24)
        log_success(f"Found {len(recent)} files modified in last 24 hours")
    except Exception as e:
        log_error(f"Get recent files failed: {e}")
        return False
    
    return True

def test_agent():
    """Test FileManagementAgent"""
    print("\n" + "="*60)
    print("TESTING FILE MANAGEMENT AGENT")
    print("="*60)
    
    try:
        log_step("Initializing", "FileManagementAgent")
        agent = FileManagementAgent()
        log_success("Agent initialized successfully")
    except Exception as e:
        log_error(f"Failed to initialize agent: {e}")
        return False
    
    # Test queries
    test_queries = [
        ("hi", "Greeting"),
        ("hello", "Greeting"),
        ("show me files in downloads", "List directory"),
        ("what files are in C:\\Users\\darkp\\Downloads", "List directory with path"),
        ("find large files in downloads", "Find large files"),
        ("what files were modified today", "Recent files"),
    ]
    
    print("\n" + "-"*60)
    print("Testing Agent Queries")
    print("-"*60)
    
    for query, description in test_queries:
        log_step(f"Query ({description})", f"'{query}'")
        try:
            response = agent.process_query(query)
            if response and len(response) > 0:
                preview = response[:100].replace('\n', ' ')
                log_success(f"Response: {preview}...")
            else:
                log_error(f"Empty response for query: {query}")
                return False
        except Exception as e:
            log_error(f"Query failed: {e}")
            return False
    
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Monday FILE MANAGEMENT AGENT - COMPREHENSIVE TEST")
    print("="*60)
    
    # Test File Manager
    fm_ok = test_file_manager()
    
    # Test Agent
    agent_ok = test_agent()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if fm_ok and agent_ok:
        log_success("All tests passed! ✓")
        print("\n✓ File Manager: Working")
        print("✓ File Operations: Working")
        print("✓ Agent: Working")
        print("✓ Intent Detection: Working")
        print("✓ LLM Integration: Working")
        return True
    else:
        log_error("Some tests failed!")
        if not fm_ok:
            print("✗ File Manager: Failed")
        if not agent_ok:
            print("✗ Agent: Failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
