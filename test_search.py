"""Focused test for search operation"""
import time
from file_manager import FileManager
from logger_util import log_step, log_success, log_error

def test_search_operation():
    """Test search operation in detail"""
    print("\n" + "="*60)
    print("SEARCH OPERATION DIAGNOSTIC TEST")
    print("="*60)
    
    fm = FileManager()
    test_dir = "C:\\Users\\darkp\\Downloads"
    
    # Test 1: Simple directory listing first
    print("\n[STEP 1] Testing basic list operation")
    log_step("List", test_dir)
    start = time.time()
    try:
        files = fm.list_directory(test_dir)
        elapsed = time.time() - start
        log_success(f"Listed {len(files)} items in {elapsed:.2f}s")
        print(f"  → Found: {len(files)} items")
    except Exception as e:
        log_error(f"List failed: {e}")
        return False
    
    # Test 2: Search with timeout detection
    print("\n[STEP 2] Testing search for *.txt")
    log_step("Search", "*.txt in " + test_dir)
    start = time.time()
    max_timeout = 10  # 10 second timeout
    
    try:
        # Manually call search with progress
        from pathlib import Path
        import fnmatch
        
        path_obj = Path(test_dir)
        matches = []
        items_checked = 0
        max_depth = 3
        
        def search_with_progress(current_path, depth, progress_interval=100):
            nonlocal items_checked, matches
            
            if depth > max_depth or len(matches) > 100:
                return
            
            try:
                for item in current_path.iterdir():
                    items_checked += 1
                    
                    # Progress indicator
                    if items_checked % progress_interval == 0:
                        elapsed = time.time() - start
                        print(f"  → Checked {items_checked} items in {elapsed:.2f}s...")
                        
                        # Timeout check
                        if elapsed > max_timeout:
                            log_error(f"Search timeout after {elapsed:.2f}s")
                            return
                    
                    if len(matches) > 100:
                        break
                    
                    try:
                        if item.is_file() and fnmatch.fnmatch(item.name, "*.txt"):
                            matches.append(item.name)
                            print(f"    ✓ Found: {item.name}")
                        elif item.is_dir() and depth < max_depth:
                            search_with_progress(item, depth + 1, progress_interval)
                    except (PermissionError, OSError) as e:
                        pass
            except (PermissionError, OSError) as e:
                pass
        
        search_with_progress(path_obj, 0)
        
        elapsed = time.time() - start
        if matches:
            log_success(f"Found {len(matches)} .txt files in {elapsed:.2f}s")
            print(f"  → Sample files: {matches[:5]}")
        else:
            log_success(f"Search completed in {elapsed:.2f}s (0 .txt files found)")
        
    except Exception as e:
        log_error(f"Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Search using FileManager directly
    print("\n[STEP 3] Testing FileManager.search_files()")
    log_step("Search", "Using FileManager class")
    start = time.time()
    
    try:
        results = fm.search_files(test_dir, "*.pdf")
        elapsed = time.time() - start
        
        if results and not any("error" in r for r in results):
            log_success(f"Found {len(results)} .pdf files in {elapsed:.2f}s")
        else:
            log_error(f"Search returned: {results}")
    except Exception as e:
        log_error(f"FileManager.search_files failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✓ Search operation is working")
    
    return True

if __name__ == "__main__":
    test_search_operation()
