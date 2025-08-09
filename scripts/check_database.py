#!/usr/bin/env python3
"""
Database Article Checker

Quick script to check how many articles are in the database.
Use this before and after RSS fetch to verify articles are being saved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_database():
    """Check current database article count and show samples."""
    try:
        from config.settings import get_settings
        from database.models import NewsSource, Article
        from sqlalchemy import create_engine, desc
        from sqlalchemy.orm import sessionmaker
        
        settings = get_settings()
        
        # Create database connection using correct settings API
        db_url = settings.database_url.get_secret_value()
        
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        
        with Session() as session:
            # Count articles and sources
            total_articles = session.query(Article).count()
            total_sources = session.query(NewsSource).count()
            active_sources = session.query(NewsSource).filter(NewsSource.active == True).count()
            
            print("📊 DATABASE STATUS")
            print("=" * 40)
            print(f"Total RSS Sources: {total_sources}")
            print(f"Active RSS Sources: {active_sources}")
            print(f"Total Articles: {total_articles}")
            
            if total_articles > 0:
                # Show recent articles
                recent_articles = session.query(Article).order_by(desc(Article.created_at)).limit(5).all()
                
                print(f"\n📰 RECENT ARTICLES (Last 5):")
                print("-" * 60)
                for i, article in enumerate(recent_articles, 1):
                    source_name = article.source.name if article.source else "Unknown"
                    title = article.title[:50] + "..." if len(article.title) > 50 else article.title
                    print(f"{i}. {title}")
                    print(f"   Source: {source_name}")
                    print(f"   URL: {article.url}")
                    print(f"   Created: {article.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
                
                # Show articles by source
                print("📈 ARTICLES BY SOURCE:")
                print("-" * 30)
                from sqlalchemy import func
                source_counts = session.query(
                    NewsSource.name,
                    func.count(Article.id).label('count')
                ).join(Article).group_by(NewsSource.name).order_by(desc('count')).all()
                
                for source_name, count in source_counts:
                    print(f"  {source_name}: {count} articles")
            
            else:
                print(f"\n❌ NO ARTICLES IN DATABASE")
                print(f"Run: python scripts/rss_with_database_save.py")
        
        return total_articles
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return None

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check database article count')
    parser.add_argument('--watch', action='store_true', help='Watch mode - check every 5 seconds')
    
    args = parser.parse_args()
    
    if args.watch:
        import time
        print("👀 Watch mode - checking database every 5 seconds (Ctrl+C to stop)")
        try:
            while True:
                article_count = check_database()
                if article_count is not None:
                    print(f"\n⏰ {time.strftime('%H:%M:%S')} - Database has {article_count} articles")
                print("\n" + "="*50 + "\n")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Watch mode stopped")
    else:
        article_count = check_database()
        if article_count is not None:
            if article_count == 0:
                print(f"\n🎯 NEXT STEP: Run RSS fetch to populate database:")
                print(f"   python scripts/rss_with_database_save.py")
            else:
                print(f"\n✅ Database has {article_count} articles - RSS fetch is working!")

if __name__ == "__main__":
    main()