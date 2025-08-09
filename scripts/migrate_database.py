#!/usr/bin/env python3
"""
Database migration script using Alembic.

Handles schema changes and data migrations for the News Automation System.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from config.settings import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_alembic():
    """Initialize Alembic for migrations."""
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", get_settings().database_url.get_secret_value())
    return alembic_cfg


def create_migration(message: str):
    """Create a new migration."""
    cfg = init_alembic()
    command.revision(cfg, autogenerate=True, message=message)
    print(f"Migration created: {message}")


def run_migrations():
    """Run pending migrations."""
    cfg = init_alembic()
    command.upgrade(cfg, "head")
    print("Migrations completed successfully")


def rollback_migration():
    """Rollback the last migration."""
    cfg = init_alembic()
    command.downgrade(cfg, "-1")
    print("Rolled back one migration")


def show_history():
    """Show migration history."""
    cfg = init_alembic()
    command.history(cfg)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Tool")
    parser.add_argument("action", choices=["upgrade", "downgrade", "history", "create"])
    parser.add_argument("-m", "--message", help="Migration message (for create)")
    
    args = parser.parse_args()
    
    if args.action == "upgrade":
        run_migrations()
    elif args.action == "downgrade":
        rollback_migration()
    elif args.action == "history":
        show_history()
    elif args.action == "create":
        if not args.message:
            print("Error: Message required for creating migration")
            sys.exit(1)
        create_migration(args.message)