#!/usr/bin/env python3
"""
Initialize RSS Sources in Database

Reads sources.json and populates the news_sources table.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from config.settings import get_settings
from database.models import NewsSource, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sources_config() -> list:
    """Load RSS sources from sources.json."""
    config_path = project_root / "config" / "sources.json"
    
    if not config_path.exists():
        logger.error(f"Sources config file not found: {config_path}")
        return []
    
    try:
        with open(config_path, 'r') as f:
            sources = json.load(f)
        
        logger.info(f"Loaded {len(sources)} sources from config")
        return sources
    
    except Exception as e:
        logger.error(f"Failed to load sources config: {e}")
        return []


def setup_database():
    """Setup database connection."""
    try:
        settings = get_settings()
        
        # Create database URL
        db_url = (
            f"postgresql://{settings.database.user}:"
            f"{settings.database.password}@"
            f"{settings.database.host}:"
            f"{settings.database.port}/"
            f"{settings.database.name}"
        )
        
        logger.info("Connecting to database...")
        
        # Create engine and session factory
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        logger.info("Database connection successful")
        return engine, Session
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None, None


def initialize_sources():
    """Initialize RSS sources in database."""
    # Load configuration
    sources_config = load_sources_config()
    if not sources_config:
        logger.error("No sources configuration found")
        return False
    
    # Setup database
    engine, Session = setup_database()
    if not engine:
        logger.error("Database setup failed")
        return False
    
    try:
        with Session() as session:
            # Check existing sources
            existing_sources = {source.name: source for source in session.query(NewsSource).all()}
            logger.info(f"Found {len(existing_sources)} existing sources in database")
            
            added_count = 0
            updated_count = 0
            
            for source_config in sources_config:
                name = source_config['name']
                url = source_config['url']  # This is actually the RSS feed URL
                
                if name in existing_sources:
                    # Update existing source
                    source = existing_sources[name]
                    source.rss_feed_url = url
                    source.url = url.replace('/rss.xml', '').replace('/feed/', '').replace('/atom.xml', '')  # Try to get base URL
                    source.category = source_config.get('category', 'General')
                    source.tier = source_config.get('priority', 2)
                    source.active = source_config.get('enabled', True)
                    source.updated_at = datetime.now(timezone.utc)
                    updated_count += 1
                    logger.info(f"Updated: {name}")
                else:
                    # Create new source
                    # Try to derive base URL from RSS feed URL
                    base_url = url
                    if '/rss.xml' in url:
                        base_url = url.replace('/rss.xml', '')
                    elif '/feed/' in url:
                        base_url = url.replace('/feed/', '').rstrip('/')
                    elif '/atom.xml' in url:
                        base_url = url.replace('/atom.xml', '')
                    elif '/feed.xml' in url:
                        base_url = url.replace('/feed.xml', '')
                    
                    source = NewsSource(
                        name=name,
                        url=base_url,
                        rss_feed_url=url,
                        category=source_config.get('category', 'General'),
                        tier=source_config.get('priority', 2),
                        active=source_config.get('enabled', True),
                        fetch_interval=3600,  # 1 hour default
                        max_articles_per_fetch=50,
                        consecutive_failures=0,
                        total_articles_fetched=0
                    )
                    
                    session.add(source)
                    added_count += 1
                    logger.info(f"Added: {name}")
            
            # Commit changes
            session.commit()
            
            logger.info(f"Source initialization completed!")
            logger.info(f"Added: {added_count} sources")
            logger.info(f"Updated: {updated_count} sources")
            logger.info(f"Total active sources: {len([s for s in sources_config if s.get('enabled', True)])}")
            
            return True
    
    except Exception as e:
        logger.error(f"Failed to initialize sources: {e}")
        return False


def show_database_sources():
    """Show current sources in database."""
    engine, Session = setup_database()
    if not engine:
        return
    
    try:
        with Session() as session:
            sources = session.query(NewsSource).order_by(NewsSource.tier, NewsSource.name).all()
            
            print("\n" + "="*80)
            print("CURRENT RSS SOURCES IN DATABASE")
            print("="*80)
            print(f"{'Name':<25} {'Tier':<5} {'Active':<7} {'Category':<15} {'Articles':<10}")
            print("-"*80)
            
            for source in sources:
                active = "✅" if source.active else "❌"
                articles = source.total_articles_fetched or 0
                category = (source.category or "General")[:14]
                
                print(f"{source.name[:24]:<25} {source.tier:<5} {active:<7} {category:<15} {articles:<10}")
            
            print("-"*80)
            print(f"Total sources: {len(sources)}")
            print(f"Active sources: {sum(1 for s in sources if s.active)}")
            print(f"Total articles: {sum(s.total_articles_fetched or 0 for s in sources)}")
    
    except Exception as e:
        logger.error(f"Failed to show sources: {e}")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize RSS sources in database')
    parser.add_argument('--show', action='store_true', help='Show current sources in database')
    parser.add_argument('--init', action='store_true', help='Initialize sources from config')
    
    args = parser.parse_args()
    
    if args.show:
        show_database_sources()
    elif args.init:
        success = initialize_sources()
        if success:
            print("✅ RSS sources initialized successfully!")
            show_database_sources()
        else:
            print("❌ RSS source initialization failed!")
    else:
        print("Use --init to initialize sources or --show to display current sources")


if __name__ == "__main__":
    main()