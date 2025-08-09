#!/usr/bin/env python3
"""
Debug Import Issues

Check what's actually available in the MCP RSS aggregator.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def debug_rss_aggregator():
    """Debug what's actually available in RSS aggregator."""
    print("🔍 Debugging RSS Aggregator Imports...")
    print("=" * 50)
    
    try:
        print("1. Testing basic import...")
        import mcp_servers.rss_aggregator as rss_mod
        print("✅ Basic import successful")
        
        print("\n2. Available functions and classes:")
        available = [name for name in dir(rss_mod) if not name.startswith('_')]
        for item in sorted(available):
            obj = getattr(rss_mod, item)
            if callable(obj):
                print(f"  📦 Function: {item}")
            elif isinstance(obj, type):
                print(f"  🏗️  Class: {item}")
            else:
                print(f"  📄 Other: {item}")
        
        print(f"\n3. Total available items: {len(available)}")
        
        # Test specific imports mentioned by user
        print("\n4. Testing user-mentioned functions:")
        
        test_imports = [
            ('fetch_rss_feed', 'function'),
            ('FeedFetchRequest', 'class'),
            ('initialize_sources', 'function'),
            ('fetch_all_sources', 'function'), 
            ('BatchFetchRequest', 'class'),
            ('get_cached_articles', 'function')
        ]
        
        for name, item_type in test_imports:
            try:
                obj = getattr(rss_mod, name)
                print(f"  ✅ {name} ({item_type}): Available")
                if item_type == 'class':
                    # Show class constructor signature
                    try:
                        import inspect
                        sig = inspect.signature(obj.__init__)
                        print(f"     Constructor: {name}{sig}")
                    except:
                        pass
                elif item_type == 'function':
                    # Show function signature
                    try:
                        import inspect
                        sig = inspect.signature(obj)
                        print(f"     Signature: {name}{sig}")
                    except:
                        pass
            except AttributeError:
                print(f"  ❌ {name} ({item_type}): NOT AVAILABLE")
        
        print("\n5. Testing actual working approach (from user):")
        
        # Test the approach user said works
        try:
            print("   Testing: from mcp_servers.rss_aggregator import initialize_sources")
            from mcp_servers.rss_aggregator import initialize_sources
            print("   ✅ initialize_sources import successful")
        except ImportError as e:
            print(f"   ❌ initialize_sources import failed: {e}")
        
        try:
            print("   Testing: from mcp_servers.rss_aggregator import BatchFetchRequest")
            from mcp_servers.rss_aggregator import BatchFetchRequest
            print("   ✅ BatchFetchRequest import successful")
        except ImportError as e:
            print(f"   ❌ BatchFetchRequest import failed: {e}")
        
    except ImportError as e:
        print(f"❌ Failed to import RSS aggregator: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection."""
    print("\n🗄️ Testing Database Connection...")
    print("=" * 50)
    
    try:
        from config.settings import get_settings
        from database.models import NewsSource, Article
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        print("✅ Settings loaded")
        
        # Create database URL
        db_url = (
            f"postgresql://{settings.database.user}:"
            f"{settings.database.password}@"
            f"{settings.database.host}:"
            f"{settings.database.port}/"
            f"{settings.database.name}"
        )
        
        print("✅ Database URL created")
        
        # Test connection
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Count sources
            source_count = session.query(NewsSource).count()
            article_count = session.query(Article).count()
            active_sources = session.query(NewsSource).filter(NewsSource.active == True).count()
            
            print(f"✅ Database connection successful")
            print(f"   Total sources: {source_count}")
            print(f"   Active sources: {active_sources}")
            print(f"   Total articles: {article_count}")
            
            # Show a few sources
            sources = session.query(NewsSource).filter(NewsSource.active == True).limit(3).all()
            print(f"\n   Sample active sources:")
            for source in sources:
                print(f"   - {source.name}: {source.rss_feed_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main debug function."""
    print("🚀 AI News Automation System - Debug Tool")
    print("=" * 50)
    
    # Test RSS aggregator
    rss_ok = debug_rss_aggregator()
    
    # Test database
    db_ok = test_database_connection()
    
    print("\n📋 SUMMARY")
    print("=" * 50)
    print(f"RSS Aggregator: {'✅ Working' if rss_ok else '❌ Issues'}")
    print(f"Database: {'✅ Working' if db_ok else '❌ Issues'}")
    
    if rss_ok and db_ok:
        print("\n🎉 Both systems operational - ready to create working fetch script!")
    else:
        print("\n⚠️ Issues found - need to resolve before proceeding")

if __name__ == "__main__":
    main()