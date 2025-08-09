#!/usr/bin/env python3
"""
Minimal RSS Test

Absolute minimal test to identify the exact import/API issue.
"""

import sys
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_step_by_step():
    """Test each step individually to identify the problem."""
    
    print("🧪 MINIMAL RSS API TEST")
    print("=" * 40)
    
    # Step 1: Basic import
    print("1. Testing basic import...")
    try:
        import mcp_servers.rss_aggregator
        print("   ✅ Basic package import works")
    except Exception as e:
        print(f"   ❌ Basic import failed: {e}")
        return
    
    # Step 2: Check what's available
    print("\n2. Checking available items...")
    try:
        items = dir(mcp_servers.rss_aggregator)
        available = [item for item in items if not item.startswith('_')]
        print(f"   Available items: {available}")
    except Exception as e:
        print(f"   ❌ Failed to list items: {e}")
        return
    
    # Step 3: Test specific imports
    print("\n3. Testing specific function imports...")
    
    functions_to_test = [
        'initialize_sources',
        'fetch_all_sources', 
        'BatchFetchRequest',
        'get_cached_articles'
    ]
    
    working_imports = []
    
    for func_name in functions_to_test:
        try:
            func = getattr(mcp_servers.rss_aggregator, func_name)
            print(f"   ✅ {func_name}: {type(func)}")
            working_imports.append(func_name)
        except AttributeError:
            print(f"   ❌ {func_name}: Not found")
        except Exception as e:
            print(f"   ❌ {func_name}: Error - {e}")
    
    if not working_imports:
        print("   ❌ No functions found!")
        return
    
    # Step 4: Try to import the working functions
    print(f"\n4. Testing import of working functions: {working_imports}")
    try:
        if 'initialize_sources' in working_imports:
            from mcp_servers.rss_aggregator import initialize_sources
            print("   ✅ initialize_sources imported")
            
        if 'BatchFetchRequest' in working_imports:
            from mcp_servers.rss_aggregator import BatchFetchRequest  
            print("   ✅ BatchFetchRequest imported")
            
        if 'fetch_all_sources' in working_imports:
            from mcp_servers.rss_aggregator import fetch_all_sources
            print("   ✅ fetch_all_sources imported")
            
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return
    
    print("\n5. Testing if functions are callable...")
    
    # Test if we can call initialize_sources
    if 'initialize_sources' in working_imports:
        try:
            # Just check if it's callable, don't actually call it yet
            if callable(initialize_sources):
                print("   ✅ initialize_sources is callable")
            else:
                print("   ❌ initialize_sources is not callable")
        except Exception as e:
            print(f"   ❌ initialize_sources test failed: {e}")
    
    # Test BatchFetchRequest instantiation
    if 'BatchFetchRequest' in working_imports:
        try:
            request = BatchFetchRequest()
            print("   ✅ BatchFetchRequest can be instantiated")
            print(f"   Request type: {type(request)}")
        except Exception as e:
            print(f"   ❌ BatchFetchRequest instantiation failed: {e}")
    
    print("\n🎯 MINIMAL TEST COMPLETE")
    print("If all steps passed, the API should work!")

if __name__ == "__main__":
    test_step_by_step()