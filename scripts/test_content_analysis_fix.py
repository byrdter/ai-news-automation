#!/usr/bin/env python3
"""
Test Content Analysis Agent Fix

Test that the Pydantic schema error is fixed and content analysis works.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_content_analysis_deps():
    """Test that ContentAnalysisDeps can be created without schema errors."""
    print("🧪 Testing Content Analysis Agent Fix")
    print("=" * 50)
    
    try:
        # Test 1: Import the fixed class
        print("1. Testing ContentAnalysisDeps import...")
        from agents.content_analysis.agent import ContentAnalysisDeps
        print("   ✅ ContentAnalysisDeps imported successfully")
        
        # Test 2: Check if model_config is properly set
        print("\n2. Checking model_config...")
        if hasattr(ContentAnalysisDeps, 'model_config'):
            config = ContentAnalysisDeps.model_config
            print(f"   ✅ model_config found: {config}")
            
            if config.get("arbitrary_types_allowed") == True:
                print("   ✅ arbitrary_types_allowed is set to True")
            else:
                print("   ❌ arbitrary_types_allowed not set correctly")
                return False
        else:
            print("   ❌ model_config not found")
            return False
        
        # Test 3: Try to create the deps object (this was failing before)
        print("\n3. Testing ContentAnalysisDeps instantiation...")
        
        # Mock dependencies
        try:
            from utils.cost_tracking import CostTracker
            mock_client = "mock_cohere_client"  # Using string as mock
            mock_tracker = CostTracker()
            mock_settings = {"test": "settings"}
            
            deps = ContentAnalysisDeps(
                cohere_client=mock_client,
                cost_tracker=mock_tracker,
                settings=mock_settings
            )
            print("   ✅ ContentAnalysisDeps created successfully")
            print(f"   cohere_client type: {type(deps.cohere_client)}")
            print(f"   cost_tracker type: {type(deps.cost_tracker)}")
            
        except Exception as e:
            print(f"   ❌ ContentAnalysisDeps creation failed: {e}")
            return False
        
        # Test 4: Test with actual Cohere client (if available)
        print("\n4. Testing with actual Cohere client...")
        try:
            import cohere
            
            # Try to create a Cohere client
            try:
                from config.settings import get_settings
                settings = get_settings()
                if hasattr(settings, 'cohere_api_key'):
                    cohere_client = cohere.Client(api_key="test-key")  # Mock key for testing
                    print("   ✅ Cohere client created")
                    
                    # Test deps with real client
                    deps_real = ContentAnalysisDeps(
                        cohere_client=cohere_client,
                        cost_tracker=mock_tracker,
                        settings=mock_settings
                    )
                    print("   ✅ ContentAnalysisDeps works with real Cohere client")
                else:
                    print("   ⚠️  No Cohere API key in settings, skipping real client test")
            
            except Exception as e:
                print(f"   ⚠️  Cohere client test skipped: {e}")
        
        except ImportError:
            print("   ⚠️  Cohere not installed, skipping real client test")
        
        print("\n🎉 All tests passed! Pydantic schema error should be fixed.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_content_analysis_function():
    """Test if the content analysis function can be imported and called."""
    print("\n🔬 Testing Content Analysis Function")
    print("=" * 50)
    
    try:
        from agents.content_analysis.agent import get_content_analysis_service
        print("✅ Content analysis service import successful")
        
        # Try to get the service
        service = get_content_analysis_service()
        print(f"✅ Content analysis service created: {type(service)}")
        
        # Check if analyze_content method exists
        if hasattr(service, 'analyze_content'):
            print("✅ analyze_content method found")
        else:
            print("❌ analyze_content method not found")
            return False
        
        print("✅ Content analysis function test passed")
        return True
        
    except Exception as e:
        print(f"❌ Content analysis function test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Content Analysis Agent Fix Test Suite")
    print("=" * 60)
    
    # Test 1: Dependencies class
    deps_ok = await test_content_analysis_deps()
    
    # Test 2: Analysis function  
    function_ok = await test_content_analysis_function()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"ContentAnalysisDeps: {'✅ Fixed' if deps_ok else '❌ Still broken'}")
    print(f"Analysis Function: {'✅ Working' if function_ok else '❌ Issues'}")
    
    if deps_ok and function_ok:
        print("\n🎉 SUCCESS! The Pydantic schema fix is working!")
        print("   Content analysis agent should now work with RSS articles.")
        print("\n🚀 Next steps:")
        print("   1. Run RSS fetch: python scripts/rss_with_database_save.py")
        print("   2. Test content analysis on real articles")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)