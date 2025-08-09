"""
Database Setup Script for AI News Automation System
Location: scripts/setup_database.py

Sets up Supabase database with:
- pgvector extension for semantic search
- All database tables and indexes
- Default news sources
- Initial system configuration
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base, create_default_news_sources
from config.settings import Settings

async def setup_database():
    """
    Complete database setup process:
    1. Connect to Supabase database
    2. Install pgvector extension
    3. Create all tables with proper indexes
    4. Insert default news sources
    5. Validate setup
    """
    
    print("🚀 Starting AI News Automation System database setup...")
    
    try:
        # Load configuration
        settings = Settings()
        print(f"📊 Environment: {settings.environment}")
        print(f"🔗 Database URL: {settings.database_url.get_secret_value()[:50]}...")
        
        # Create database engine
        engine = create_engine(
            settings.database_url.get_secret_value(),
            echo=settings.environment == "development",  # SQL logging in dev
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Validate connections
            pool_recycle=3600    # Recycle connections every hour
        )
        
        print("✅ Database engine created")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            print(f"📋 PostgreSQL Version: {result[0][:100]}...")
        
        print("✅ Database connection verified")
        
        # Install pgvector extension (required for semantic search)
        print("🔧 Installing pgvector extension...")
        try:
            with engine.connect() as conn:
                # Check if pgvector is already installed
                result = conn.execute(
                    text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                ).fetchone()
                
                if not result[0]:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    print("✅ pgvector extension installed")
                else:
                    print("✅ pgvector extension already installed")
                    
        except Exception as e:
            print(f"⚠️  pgvector installation failed: {e}")
            print("🔍 Please ensure your Supabase project has pgvector enabled")
            print("   You can enable it from the Supabase Dashboard -> SQL Editor:")
            print("   CREATE EXTENSION IF NOT EXISTS vector;")
            raise
        
        # Create all tables
        print("🏗️  Creating database tables...")
        Base.metadata.create_all(engine)
        print("✅ All database tables created successfully")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    ORDER BY tablename
                """)
            ).fetchall()
            
            print(f"📋 Created {len(result)} tables:")
            for table in result:
                print(f"   • {table[0]}")
        
        # Create session for data operations
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Insert default news sources
            print("📰 Creating default news sources...")
            create_default_news_sources(session)
            
            # Verify news sources
            from database.models import NewsSource
            source_count = session.query(NewsSource).count()
            print(f"✅ {source_count} news sources configured")
            
            # Display sources by tier
            for tier in [1, 2, 3]:
                tier_sources = session.query(NewsSource).filter_by(tier=tier).all()
                print(f"   Tier {tier}: {len(tier_sources)} sources")
                for source in tier_sources:
                    print(f"     • {source.name} ({source.category})")
            
            print("✅ Default news sources created successfully")
            
            # Validate database setup
            print("🔍 Validating database setup...")
            
            # Test vector operations
            try:
                with engine.connect() as conn:
                    # Test vector operations work
                    test_vector = '[' + ','.join(['0.1'] * 768) + ']'
                    conn.execute(
                        text(f"SELECT '{test_vector}'::vector <-> '{test_vector}'::vector")
                    ).fetchone()
                    print("✅ Vector operations working correctly")
            except Exception as e:
                print(f"❌ Vector operations test failed: {e}")
                raise
            
            # Test indexes
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT schemaname, tablename, indexname 
                        FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND indexname LIKE '%idx_%'
                        ORDER BY tablename, indexname
                    """)
                ).fetchall()
                
                print(f"✅ {len(result)} custom indexes created:")
                current_table = None
                for index in result:
                    if index[1] != current_table:
                        current_table = index[1]
                        print(f"   {current_table}:")
                    print(f"     • {index[2]}")
            
            print("🎉 Database setup completed successfully!")
            print("\n📋 Setup Summary:")
            print(f"   • Environment: {settings.environment}")
            print(f"   • Tables created: {len(result)} (from previous query)")
            print(f"   • News sources: {source_count}")
            print(f"   • pgvector: Enabled")
            print(f"   • Indexes: {len(result)} custom indexes")
            
            print("\n🚀 Next Steps:")
            print("   1. Configure your .env file with actual API keys")
            print("   2. Run: python scripts/migrate_database.py (if needed)")
            print("   3. Start MCP servers: python -m mcp_servers.rss_aggregator.server")
            print("   4. Test system: python cli.py test --database")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your DATABASE_URL in .env")
        print("   2. Ensure your Supabase project is running")
        print("   3. Check that pgvector extension is available")
        print("   4. Verify database permissions")
        raise
    
    finally:
        if 'engine' in locals():
            engine.dispose()

async def verify_database():
    """
    Verify database setup and configuration
    """
    settings = Settings()
    engine = create_engine(settings.database_url.get_secret_value())
    
    print("🔍 Verifying database setup...")
    
    try:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Import models for testing
        from database.models import NewsSource, Article, Report, SystemMetrics
        
        # Test each table
        tables_to_test = [
            (NewsSource, "news_sources"),
            (Article, "articles"),
            (Report, "reports"),
            (SystemMetrics, "system_metrics")
        ]
        
        for model_class, table_name in tables_to_test:
            count = session.query(model_class).count()
            print(f"✅ {table_name}: {count} records")
        
        # Test vector operations if we have articles with embeddings
        article_with_embedding = session.query(Article).filter(
            Article.content_embedding.is_not(None)
        ).first()
        
        if article_with_embedding:
            print("✅ Vector embeddings: Present")
        else:
            print("⚠️  Vector embeddings: No articles with embeddings yet")
        
        print("✅ Database verification completed")
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        raise
    
    finally:
        session.close()
        engine.dispose()

def main():
    """Main function to run database setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI News System Database Setup")
    parser.add_argument(
        "--verify", 
        action="store_true", 
        help="Verify existing database setup"
    )
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset database (WARNING: destroys all data)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        confirm = input("⚠️  This will destroy all data. Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("❌ Reset cancelled")
            return
        
        print("🗑️  Resetting database...")
        settings = Settings()
        engine = create_engine(settings.database_url.get_secret_value())
        Base.metadata.drop_all(engine)
        print("✅ Database reset completed")
        engine.dispose()
    
    if args.verify:
        asyncio.run(verify_database())
    else:
        asyncio.run(setup_database())

if __name__ == "__main__":
    main()