"""
Initial Database Schema Migration
Location: database/migrations/001_initial_schema.py

Creates the complete initial schema for AI News Automation System:
- All tables with proper relationships
- Indexes for performance
- pgvector extension for semantic search
- Default constraints and validation
"""

from datetime import datetime
from sqlalchemy import text
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create all tables and indexes for initial schema"""
    
    # Ensure pgvector extension is installed
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create news_sources table
    op.create_table('news_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('rss_feed_url', sa.String(length=1000)),
        sa.Column('tier', sa.Integer(), nullable=False, default=2),
        sa.Column('category', sa.String(length=100)),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('fetch_interval', sa.Integer(), default=3600),
        sa.Column('max_articles_per_fetch', sa.Integer(), default=50),
        sa.Column('last_fetched_at', sa.DateTime(timezone=True)),
        sa.Column('last_successful_fetch_at', sa.DateTime(timezone=True)),
        sa.Column('consecutive_failures', sa.Integer(), default=0),
        sa.Column('total_articles_fetched', sa.Integer(), default=0),
        sa.Column('metadata_json', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('name'),
        sa.CheckConstraint('tier >= 1 AND tier <= 3', name='valid_tier'),
        sa.CheckConstraint('fetch_interval >= 60', name='min_fetch_interval'),
        sa.CheckConstraint('max_articles_per_fetch >= 1', name='min_articles_fetch')
    )
    
    # Create indexes for news_sources
    op.create_index('idx_news_sources_active_tier', 'news_sources', ['active', 'tier'])
    op.create_index('idx_news_sources_category', 'news_sources', ['category'])
    
    # Create articles table
    op.create_table('articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('content', sa.Text()),
        sa.Column('summary', sa.Text()),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('news_sources.id'), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True)),
        sa.Column('author', sa.String(length=255)),
        sa.Column('word_count', sa.Integer()),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('processing_stage', sa.String(length=50)),
        sa.Column('processing_errors', sa.JSON()),
        sa.Column('relevance_score', sa.Float(), default=0.0),
        sa.Column('sentiment_score', sa.Float(), default=0.0),
        sa.Column('quality_score', sa.Float(), default=0.0),
        sa.Column('urgency_score', sa.Float(), default=0.0),
        sa.Column('categories', postgresql.ARRAY(sa.String(100))),
        sa.Column('entities', sa.JSON()),
        sa.Column('keywords', postgresql.ARRAY(sa.String(100))),
        sa.Column('topics', postgresql.ARRAY(sa.String(100))),
        sa.Column('title_embedding', sa.dialects.postgresql.base.ischema_names['vector'](768)),
        sa.Column('content_embedding', sa.dialects.postgresql.base.ischema_names['vector'](768)),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('share_count', sa.Integer(), default=0),
        sa.Column('external_engagement', sa.JSON()),
        sa.Column('content_hash', sa.String(length=64)),
        sa.Column('duplicate_of_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id')),
        sa.Column('analysis_model', sa.String(length=100)),
        sa.Column('analysis_cost_usd', sa.Float(), default=0.0),
        sa.Column('analysis_timestamp', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('url')
    )
    
    # Create indexes for articles
    op.create_index('idx_articles_source_published', 'articles', ['source_id', 'published_at'])
    op.create_index('idx_articles_processed_relevance', 'articles', ['processed', 'relevance_score'])
    op.create_index('idx_articles_content_hash', 'articles', ['content_hash'])
    op.create_index('idx_articles_categories', 'articles', ['categories'], postgresql_using='gin')
    op.create_index('idx_articles_keywords', 'articles', ['keywords'], postgresql_using='gin')
    op.create_index('idx_articles_published_at', 'articles', ['published_at'])
    op.create_index('idx_articles_urgency_score', 'articles', ['urgency_score'])
    
    # Create vector indexes using HNSW
    op.execute("""
        CREATE INDEX idx_articles_title_embedding 
        ON articles USING hnsw (title_embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 64)
    """)
    
    op.execute("""
        CREATE INDEX idx_articles_content_embedding 
        ON articles USING hnsw (content_embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 64)
    """)
    
    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('executive_summary', sa.Text()),
        sa.Column('key_highlights', sa.JSON()),
        sa.Column('trend_analysis', sa.Text()),
        sa.Column('category_breakdown', sa.JSON()),
        sa.Column('full_content', sa.Text()),
        sa.Column('generation_model', sa.String(length=100)),
        sa.Column('generation_cost_usd', sa.Float(), default=0.0),
        sa.Column('generation_duration', sa.Float()),
        sa.Column('template_version', sa.String(length=50)),
        sa.Column('status', sa.String(length=50), default='draft'),
        sa.Column('delivery_status', sa.String(length=50)),
        sa.Column('delivery_attempts', sa.Integer(), default=0),
        sa.Column('delivered_at', sa.DateTime(timezone=True)),
        sa.Column('article_count', sa.Integer(), default=0),
        sa.Column('avg_relevance_score', sa.Float()),
        sa.Column('coverage_completeness', sa.Float()),
        sa.Column('recipients', postgresql.ARRAY(sa.String(255))),
        sa.Column('email_subject', sa.String(length=500)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('report_type', 'report_date', name='unique_report_per_date')
    )
    
    # Create indexes for reports
    op.create_index('idx_reports_type_date', 'reports', ['report_type', 'report_date'])
    op.create_index('idx_reports_status', 'reports', ['status'])
    
    # Create report_articles junction table
    op.create_table('report_articles',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reports.id'), primary_key=True),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id'), primary_key=True),
        sa.Column('section', sa.String(length=100)),
        sa.Column('importance_score', sa.Float(), default=0.5),
        sa.Column('summary_snippet', sa.Text()),
        sa.Column('position_in_section', sa.Integer())
    )
    
    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('alert_type', sa.String(length=50)),
        sa.Column('urgency_level', sa.String(length=20), default='medium'),
        sa.Column('urgency_score', sa.Float()),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id')),
        sa.Column('triggered_by_rules', sa.JSON()),
        sa.Column('trigger_keywords', postgresql.ARRAY(sa.String(100))),
        sa.Column('trigger_entities', sa.JSON()),
        sa.Column('delivery_status', sa.String(length=50), default='pending'),
        sa.Column('delivery_method', sa.String(length=50)),
        sa.Column('delivery_attempts', sa.Integer(), default=0),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
        sa.Column('delivered_at', sa.DateTime(timezone=True)),
        sa.Column('is_throttled', sa.Boolean(), default=False),
        sa.Column('similar_alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id')),
        sa.Column('alert_group', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now())
    )
    
    # Create indexes for alerts
    op.create_index('idx_alerts_urgency_sent', 'alerts', ['urgency_level', 'sent_at'])
    op.create_index('idx_alerts_delivery_status', 'alerts', ['delivery_status'])
    op.create_index('idx_alerts_article_id', 'alerts', ['article_id'])
    
    # Create source_statistics table
    op.create_table('source_statistics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('news_sources.id'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('articles_fetched', sa.Integer(), default=0),
        sa.Column('articles_processed', sa.Integer(), default=0),
        sa.Column('articles_relevant', sa.Integer(), default=0),
        sa.Column('articles_included_in_reports', sa.Integer(), default=0),
        sa.Column('avg_relevance_score', sa.Float()),
        sa.Column('avg_quality_score', sa.Float()),
        sa.Column('avg_word_count', sa.Float()),
        sa.Column('fetch_duration', sa.Float()),
        sa.Column('processing_duration', sa.Float()),
        sa.Column('error_count', sa.Integer(), default=0),
        sa.Column('error_types', sa.JSON()),
        sa.Column('processing_cost_usd', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('source_id', 'date', name='unique_source_date_stats')
    )
    
    # Create indexes for source_statistics
    op.create_index('idx_source_stats_date', 'source_statistics', ['date'])
    op.create_index('idx_source_stats_source_id', 'source_statistics', ['source_id'])
    
    # Create system_metrics table
    op.create_table('system_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('articles_processed_per_minute', sa.Integer(), default=0),
        sa.Column('avg_processing_time', sa.Float()),
        sa.Column('pipeline_success_rate', sa.Float()),
        sa.Column('agent_response_times', sa.JSON()),
        sa.Column('agent_success_rates', sa.JSON()),
        sa.Column('active_agents', sa.Integer(), default=0),
        sa.Column('llm_api_calls', sa.Integer(), default=0),
        sa.Column('total_tokens_used', sa.Integer(), default=0),
        sa.Column('tokens_by_model', sa.JSON()),
        sa.Column('estimated_cost_usd', sa.Float(), default=0.0),
        sa.Column('daily_cost_usd', sa.Float(), default=0.0),
        sa.Column('monthly_cost_usd', sa.Float(), default=0.0),
        sa.Column('mcp_server_status', sa.JSON()),
        sa.Column('database_connection_pool', sa.JSON()),
        sa.Column('error_rate', sa.Float(), default=0.0),
        sa.Column('cpu_usage_percent', sa.Float()),
        sa.Column('memory_usage_mb', sa.Float()),
        sa.Column('disk_usage_mb', sa.Float()),
        sa.Column('workflow_completion_times', sa.JSON()),
        sa.Column('workflow_success_rates', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now())
    )
    
    # Create indexes for system_metrics
    op.create_index('idx_system_metrics_timestamp', 'system_metrics', ['timestamp'])
    op.create_index('idx_system_metrics_cost', 'system_metrics', ['daily_cost_usd', 'monthly_cost_usd'])
    
    # Create cost_tracking table
    op.create_table('cost_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('operation_type', sa.String(length=100), nullable=False),
        sa.Column('agent_name', sa.String(length=100)),
        sa.Column('model_name', sa.String(length=100)),
        sa.Column('input_tokens', sa.Integer(), default=0),
        sa.Column('output_tokens', sa.Integer(), default=0),
        sa.Column('total_tokens', sa.Integer(), default=0),
        sa.Column('cost_per_token', sa.Float()),
        sa.Column('total_cost_usd', sa.Float(), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('articles.id')),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reports.id')),
        sa.Column('operation_metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now())
    )
    
    # Create indexes for cost_tracking
    op.create_index('idx_cost_tracking_date', 'cost_tracking', ['created_at'])
    op.create_index('idx_cost_tracking_agent', 'cost_tracking', ['agent_name'])
    op.create_index('idx_cost_tracking_model', 'cost_tracking', ['model_name'])

def downgrade():
    """Drop all tables and extensions"""
    
    # Drop all indexes first
    op.drop_index('idx_cost_tracking_model', table_name='cost_tracking')
    op.drop_index('idx_cost_tracking_agent', table_name='cost_tracking')
    op.drop_index('idx_cost_tracking_date', table_name='cost_tracking')
    
    op.drop_index('idx_system_metrics_cost', table_name='system_metrics')
    op.drop_index('idx_system_metrics_timestamp', table_name='system_metrics')
    
    op.drop_index('idx_source_stats_source_id', table_name='source_statistics')
    op.drop_index('idx_source_stats_date', table_name='source_statistics')
    
    op.drop_index('idx_alerts_article_id', table_name='alerts')
    op.drop_index('idx_alerts_delivery_status', table_name='alerts')
    op.drop_index('idx_alerts_urgency_sent', table_name='alerts')
    
    op.drop_index('idx_reports_status', table_name='reports')
    op.drop_index('idx_reports_type_date', table_name='reports')
    
    # Drop vector indexes
    op.execute("DROP INDEX IF EXISTS idx_articles_content_embedding")
    op.execute("DROP INDEX IF EXISTS idx_articles_title_embedding")
    
    op.drop_index('idx_articles_urgency_score', table_name='articles')
    op.drop_index('idx_articles_published_at', table_name='articles')
    op.drop_index('idx_articles_keywords', table_name='articles')
    op.drop_index('idx_articles_categories', table_name='articles')
    op.drop_index('idx_articles_content_hash', table_name='articles')
    op.drop_index('idx_articles_processed_relevance', table_name='articles')
    op.drop_index('idx_articles_source_published', table_name='articles')
    
    op.drop_index('idx_news_sources_category', table_name='news_sources')
    op.drop_index('idx_news_sources_active_tier', table_name='news_sources')
    
    # Drop all tables
    op.drop_table('cost_tracking')
    op.drop_table('system_metrics')
    op.drop_table('source_statistics')
    op.drop_table('alerts')
    op.drop_table('report_articles')
    op.drop_table('reports')
    op.drop_table('articles')
    op.drop_table('news_sources')
    
    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')