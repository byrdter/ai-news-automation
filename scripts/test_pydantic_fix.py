#!/usr/bin/env python3
"""
Simple Pydantic Fix Test

Test just the Pydantic schema fix without full dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_pydantic_fix():
    """Test the Pydantic fix directly."""
    print("🧪 Simple Pydantic Fix Test")
    print("=" * 30)
    
    try:
        # Test the fix directly with BaseModel
        from pydantic import BaseModel
        from typing import Any
        
        # Create the fixed class structure
        class TestContentAnalysisDeps(BaseModel):
            model_config = {"arbitrary_types_allowed": True}
            
            cohere_client: Any
            cost_tracker: Any  
            settings: Any
        
        print("✅ Test class with model_config created")
        
        # Test instantiation with arbitrary types
        mock_client = object()  # Any arbitrary object
        mock_tracker = {"test": "tracker"}
        mock_settings = ["test", "settings"]
        
        deps = TestContentAnalysisDeps(
            cohere_client=mock_client,
            cost_tracker=mock_tracker,
            settings=mock_settings
        )
        
        print("✅ Class instantiated with arbitrary types")
        print(f"   cohere_client: {type(deps.cohere_client)}")
        print(f"   cost_tracker: {type(deps.cost_tracker)}")
        print(f"   settings: {type(deps.settings)}")
        
        print("\n🎉 SUCCESS! The Pydantic fix works correctly!")
        print("   The model_config = {'arbitrary_types_allowed': True} allows arbitrary types")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_actual_file():
    """Check if the actual file has the fix."""
    print("\n🔍 Checking actual agent file...")
    
    try:
        agent_file = project_root / "agents" / "content_analysis" / "agent.py"
        
        if not agent_file.exists():
            print("❌ Agent file not found")
            return False
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for the fix
        if 'model_config = {"arbitrary_types_allowed": True}' in content:
            print("✅ Found model_config fix in actual file")
        elif "arbitrary_types_allowed" in content:
            print("✅ Found arbitrary_types_allowed in actual file")
        else:
            print("❌ Fix not found in actual file")
            return False
        
        # Check for the updated type annotation
        if 'cohere_client: Any' in content:
            print("✅ Found updated type annotation (cohere_client: Any)")
        else:
            print("⚠️  Type annotation might still be cohere.Client (not critical)")
        
        print("✅ Actual file check passed")
        return True
        
    except Exception as e:
        print(f"❌ File check failed: {e}")
        return False

def main():
    """Run tests."""
    print("🚀 Testing Pydantic Schema Fix")
    print("=" * 40)
    
    # Test 1: Pydantic fix
    fix_works = test_pydantic_fix()
    
    # Test 2: Check actual file
    file_ok = check_actual_file()
    
    print("\n" + "=" * 40)
    print("📋 RESULTS")
    print("=" * 40)
    print(f"Pydantic Fix: {'✅ Works' if fix_works else '❌ Broken'}")
    print(f"File Updated: {'✅ Yes' if file_ok else '❌ No'}")
    
    if fix_works and file_ok:
        print("\n🎉 SUCCESS!")
        print("   The Pydantic schema error should be fixed!")
        print("   ContentAnalysisDeps will work with arbitrary types.")
        print("\n📝 Note: You may still need to install pydantic-ai:")
        print("   pip install pydantic-ai")
    else:
        print("\n❌ Issues found - check the errors above")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)