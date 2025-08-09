# RSS Article Fetching Setup Guide

This guide will help you transform your AI News Automation System from demo mode to live mode with real articles from RSS sources.

## 🔧 Quick Setup (5 minutes)

### Step 1: Initialize RSS Sources in Database

```bash
# Initialize RSS sources from configuration
cd /path/to/News-Automation-System
python scripts/initialize_sources.py --init

# Verify sources were added
python scripts/initialize_sources.py --show
```

### Step 2: Test RSS Feed Connectivity

```bash
# Test RSS feeds without database operations (safe test)
python scripts/test_rss_fetch.py
```

### Step 3: Fetch Real Articles

```bash
# Fetch articles from all sources and save to database
python scripts/populate_articles.py

# Or fetch from just a few sources first (recommended for testing)
python scripts/populate_articles.py --max-sources 3
```

### Step 4: Verify Articles in Database

```bash
# Check that articles were saved
python scripts/cli_integration.py status
```

## 📋 Detailed Commands

### RSS Source Management

```bash
# Show current RSS sources in database
python scripts/initialize_sources.py --show

# Re-initialize sources from config (updates existing)
python scripts/initialize_sources.py --init
```

### Article Fetching

```bash
# Test RSS connectivity only (no database changes)
python scripts/test_rss_fetch.py

# Fetch articles from all active sources
python scripts/populate_articles.py

# Fetch from limited number of sources
python scripts/populate_articles.py --max-sources 5

# Test a single specific source
python scripts/populate_articles.py --test-source "OpenAI Blog"

# Dry run mode (test without saving)
python scripts/cli_integration.py rss fetch-articles --test-run
```

### System Status and Monitoring

```bash
# Show RSS system status and statistics
python scripts/cli_integration.py rss status

# Test all RSS feeds
python scripts/cli_integration.py rss test-feeds

# Show configured sources
python scripts/cli_integration.py rss show-sources
```

## 🔍 Troubleshooting

### Problem: "RSSSourceConfig object not found"

**Solution**: The RSS aggregator uses `FeedFetchRequest` objects, not `RSSSourceConfig`. The populate script now handles this correctly.

### Problem: Database connection errors

**Solution**: 
1. Check your `.env` file has correct database credentials
2. Verify Supabase project is running
3. Test connection: `python -c "from config.settings import get_settings; print(get_settings().database)"`

### Problem: RSS feeds not accessible

**Solution**:
1. Test individual feeds: `python scripts/cli_integration.py rss test-source --source-name "OpenAI Blog"`
2. Check internet connectivity
3. Some feeds may have changed URLs - update `config/sources.json`

### Problem: Import errors

**Solution**:
```bash
# Make sure you're in the project root directory
cd /Users/terrybyrd/Library/CloudStorage/Dropbox/AIAgents/News-Automation-System

# Install missing dependencies
pip install feedparser newspaper3k aiohttp beautifulsoup4

# Activate virtual environment if using one
source venv_linux/bin/activate  # or your venv path
```

## 📊 Expected Results

After successful setup:

- **Database**: 13 RSS sources initialized
- **Articles**: 200-500+ real articles from AI/tech sources
- **Sources working**: 8-12 out of 13 feeds (some may be temporarily down)
- **Content**: Real articles from OpenAI, Google AI, TechCrunch, etc.

## 🎯 Integration with Existing CLI

The RSS commands integrate with your existing CLI:

```bash
# Your existing CLI
python cli.py sources  # Shows sources (currently mock data)

# New RSS CLI commands  
python scripts/cli_integration.py rss status        # Real database status
python scripts/cli_integration.py rss fetch-articles # Fetch real articles
python scripts/cli_integration.py rss test-feeds    # Test connectivity
```

## 🔄 Automation and Scheduling

Once working, you can automate article fetching:

```bash
# Add to crontab for hourly updates
0 * * * * cd /path/to/News-Automation-System && python scripts/populate_articles.py --max-sources 13

# Or run via your coordination agent
python -c "
import asyncio
from agents.coordination.agent import coordinate_request
from agents.coordination.models import CoordinationRequest, Task, TaskType

async def schedule_rss():
    task = Task(
        task_type=TaskType.NEWS_DISCOVERY,
        name='Hourly RSS Fetch',
        parameters={'max_articles': 150}
    )
    request = CoordinationRequest(
        request_type='single_task',
        task=task
    )
    result = await coordinate_request(request)
    print(result)

asyncio.run(schedule_rss())
"
```

## 🧪 Testing Everything Works

```bash
# Complete test sequence
echo "1. Testing RSS connectivity..."
python scripts/test_rss_fetch.py

echo "2. Initializing sources..."
python scripts/initialize_sources.py --init

echo "3. Fetching sample articles..."
python scripts/populate_articles.py --max-sources 3

echo "4. Checking status..."
python scripts/cli_integration.py rss status

echo "✅ Setup complete! Check database for real articles."
```

## 📚 Next Steps

Once you have real articles flowing:

1. **Test Content Analysis**: Run articles through the Content Analysis Agent
2. **Generate Reports**: Create reports with real data using Report Generation Agent  
3. **Set Up Alerts**: Configure breaking news alerts with real articles
4. **Schedule Automation**: Set up regular fetching via coordination agent or cron

## 🐛 Common Issues and Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Import errors | `ModuleNotFoundError` | Run from project root, check PYTHONPATH |
| Database connection | `Connection refused` | Check .env file, Supabase status |
| Feed timeouts | `TimeoutError` | Some feeds are slow, this is normal |
| Duplicate articles | "Already exists" warnings | Expected behavior, duplicates are skipped |
| Empty results | 0 articles fetched | Check feed URLs in config/sources.json |

The scripts include comprehensive error handling and fallback mechanisms, so most issues will be reported clearly with suggestions for resolution.