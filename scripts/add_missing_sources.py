#!/usr/bin/env python3
"""
Add missing RSS sources to the database
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.settings import get_settings
from database.models import NewsSource

def add_missing_sources():
    """Add VentureBeat AI, Google AI Research, and Hugging Face Blog to database."""
    
    settings = get_settings()
    db_url = settings.database_url.get_secret_value()
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    
    # Define missing sources
    missing_sources = [
        {
            "name": "VentureBeat AI",
            "url": "https://venturebeat.com/ai/",
            "rss_feed_url": "https://feeds.feedburner.com/venturebeat/SZYF",
            "active": True,
            "tier": 2,
            "category": "Industry News"
        },
        {
            "name": "Google AI Research",
            "url": "https://research.google/blog/",
            "rss_feed_url": "https://research.google/blog/rss/",
            "active": True,
            "tier": 1,
            "category": "Industry Research"
        },
        {
            "name": "Hugging Face Blog",
            "url": "https://huggingface.co/blog",
            "rss_feed_url": "https://huggingface.co/blog/feed.xml",
            "active": True,
            "tier": 1,
            "category": "Industry Research"
        }
    ]
    
    with Session() as session:
        added_count = 0
        
        for source_data in missing_sources:
            # Check if source already exists
            existing = session.query(NewsSource).filter_by(name=source_data["name"]).first()
            
            if existing:
                print(f"✓ Source already exists: {source_data['name']}")
                # Update RSS URL if different
                if existing.rss_feed_url != source_data["rss_feed_url"]:
                    existing.rss_feed_url = source_data["rss_feed_url"]
                    existing.updated_at = datetime.now(timezone.utc)
                    print(f"  Updated RSS URL to: {source_data['rss_feed_url']}")
            else:
                # Add new source
                new_source = NewsSource(
                    name=source_data["name"],
                    url=source_data["url"],
                    rss_feed_url=source_data["rss_feed_url"],
                    active=source_data["active"],
                    tier=source_data["tier"],
                    category=source_data["category"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(new_source)
                added_count += 1
                print(f"✅ Added new source: {source_data['name']}")
        
        session.commit()
        
        # Count total sources
        total_sources = session.query(NewsSource).count()
        active_sources = session.query(NewsSource).filter_by(active=True).count()
        
        print(f"\n📊 Database Status:")
        print(f"  Total sources: {total_sources}")
        print(f"  Active sources: {active_sources}")
        print(f"  New sources added: {added_count}")

if __name__ == "__main__":
    print("🔧 Adding missing RSS sources to database...")
    add_missing_sources()
    print("\n✅ Done! Now run the RSS fetcher again to get articles from all sources.")