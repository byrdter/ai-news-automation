#!/usr/bin/env python3
"""
Remove Stanford HAI from sources (no RSS feed available)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.settings import get_settings
from database.models import NewsSource

def remove_stanford_hai():
    """Remove Stanford HAI source since they don't have an RSS feed."""
    
    settings = get_settings()
    db_url = settings.database_url.get_secret_value()
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        # Find Stanford HAI source
        stanford_hai = session.query(NewsSource).filter_by(name="Stanford HAI").first()
        
        if stanford_hai:
            session.delete(stanford_hai)
            session.commit()
            print("✅ Removed Stanford HAI from sources (no RSS feed available)")
        else:
            print("ℹ️  Stanford HAI not found in database")
        
        # Count remaining sources
        total_sources = session.query(NewsSource).count()
        active_sources = session.query(NewsSource).filter_by(active=True).count()
        
        print(f"\n📊 Database Status:")
        print(f"  Total sources: {total_sources}")
        print(f"  Active sources: {active_sources}")

if __name__ == "__main__":
    print("🔧 Removing Stanford HAI (no RSS feed)...")
    remove_stanford_hai()
    print("\n✅ Done! Stanford HAI removed since they don't provide an RSS feed.")