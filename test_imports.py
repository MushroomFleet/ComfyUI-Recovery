#!/usr/bin/env python3
"""
Test script to verify all modules can be imported correctly.
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all modules."""
    
    print("Testing module imports:")
    
    # List of modules to test
    modules = [
        "settings",
        "downloader",
        "extractor",
        "symlink_manager",
        "node_installer"
    ]
    
    success = True
    
    # Try importing each module
    for module_name in modules:
        try:
            print(f"  Importing {module_name}...", end="")
            module = __import__(module_name)
            print(" SUCCESS")
            
            # Print some information about the module
            module_classes = [name for name in dir(module) if name[0].isupper() and not name.startswith("__")]
            if module_classes:
                print(f"    Found classes: {', '.join(module_classes)}")
            
        except Exception as e:
            print(f" FAILED: {type(e).__name__}: {e}")
            success = False
    
    # Final result
    print("\nTest result:", "PASSED" if success else "FAILED")
    return success

if __name__ == "__main__":
    test_imports()
