#!/usr/bin/env python3
"""
Dependency Checker and Installer

Checks if all required dependencies are installed and offers to install missing ones.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependency(package_name, import_name=None):
    """Check if a dependency is available."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def get_critical_dependencies():
    """Get list of critical dependencies for RSS + Database functionality."""
    return [
        ("pydantic", "pydantic"),
        ("pydantic-ai", "pydantic_ai"), 
        ("cohere", "cohere"),
        ("sqlalchemy", "sqlalchemy"),
        ("aiohttp", "aiohttp"),
        ("feedparser", "feedparser"),
        ("rich", "rich"),
        ("python-dotenv", "dotenv")
    ]

def check_all_dependencies():
    """Check all critical dependencies."""
    print("🔍 Checking Critical Dependencies")
    print("=" * 50)
    
    critical_deps = get_critical_dependencies()
    missing_deps = []
    working_deps = []
    
    for package, import_name in critical_deps:
        if check_dependency(package, import_name):
            print(f"✅ {package}: Available")
            working_deps.append(package)
        else:
            print(f"❌ {package}: MISSING")
            missing_deps.append(package)
    
    return working_deps, missing_deps

def install_dependencies(missing_deps):
    """Install missing dependencies."""
    if not missing_deps:
        print("✅ All dependencies are installed!")
        return True
    
    print(f"\n📦 Found {len(missing_deps)} missing dependencies:")
    for dep in missing_deps:
        print(f"   - {dep}")
    
    # Ask user if they want to install
    try:
        response = input(f"\nInstall missing dependencies? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            print("⚠️  Skipping dependency installation")
            return False
    except KeyboardInterrupt:
        print("\n⚠️  Installation cancelled")
        return False
    
    print("\n📥 Installing dependencies...")
    
    # Try to use requirements.txt first
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        try:
            print("Using requirements.txt for installation...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True, text=True)
            
            print("✅ Dependencies installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Requirements.txt installation failed: {e}")
            print(f"stderr: {e.stderr}")
            
            # Fall back to individual installation
            print("Trying individual package installation...")
    
    # Install individual packages
    success_count = 0
    for package in missing_deps:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True, text=True)
            
            print(f"✅ {package} installed")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    if success_count == len(missing_deps):
        print(f"\n✅ All {success_count} dependencies installed successfully!")
        return True
    else:
        print(f"\n⚠️  {success_count}/{len(missing_deps)} dependencies installed")
        return False

def test_critical_functionality():
    """Test that critical functionality works after dependency installation."""
    print("\n🧪 Testing Critical Functionality")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Pydantic with arbitrary types
    try:
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            model_config = {"arbitrary_types_allowed": True}
            test_field: object
        
        test_obj = TestModel(test_field="test")
        print("✅ Pydantic with arbitrary types: Working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Pydantic test failed: {e}")
    
    # Test 2: Content Analysis Deps
    try:
        from agents.content_analysis.agent import ContentAnalysisDeps
        print("✅ Content Analysis Deps import: Working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Content Analysis Deps import failed: {e}")
    
    # Test 3: RSS Aggregator
    try:
        from mcp_servers.rss_aggregator import initialize_sources, BatchFetchRequest
        print("✅ RSS Aggregator import: Working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ RSS Aggregator import failed: {e}")
    
    # Test 4: Database models
    try:
        from database.models import Article, NewsSource
        print("✅ Database models import: Working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
    
    print(f"\n📊 Functionality Tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def main():
    """Main dependency check and installation process."""
    print("🚀 AI News Automation System - Dependency Check")
    print("=" * 60)
    
    # Check dependencies
    working_deps, missing_deps = check_all_dependencies()
    
    print(f"\n📊 Summary:")
    print(f"   Working: {len(working_deps)}/{len(working_deps) + len(missing_deps)}")
    print(f"   Missing: {len(missing_deps)}")
    
    # Install missing dependencies if needed
    if missing_deps:
        success = install_dependencies(missing_deps)
        if not success:
            print("\n❌ Dependency installation incomplete")
            print("   Manual installation command:")
            print(f"   pip install -r {project_root}/requirements.txt")
            return False
    
    # Test functionality
    print("\n" + "="*60)
    functionality_ok = test_critical_functionality()
    
    # Final results
    print("\n" + "="*60)
    print("📋 FINAL RESULTS")
    print("="*60)
    
    if not missing_deps and functionality_ok:
        print("🎉 SUCCESS! All dependencies are working correctly!")
        print("\n🎯 System Status:")
        print("   ✅ Dependencies installed")
        print("   ✅ Pydantic schema fix working")
        print("   ✅ RSS system functional")
        print("   ✅ Database models accessible")
        print("\n🚀 Ready to run:")
        print("   python scripts/rss_with_database_save.py")
        return True
    else:
        print("❌ Issues remain:")
        if missing_deps:
            print("   - Missing dependencies need installation")
        if not functionality_ok:
            print("   - Some functionality tests failed")
        print("\n🛠️  Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Re-run this script to verify")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)