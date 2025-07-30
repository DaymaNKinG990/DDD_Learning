#!/usr/bin/env python3
"""Database migration script for marketplace services."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
from src.shared.infrastructure.config import settings
from src.shared.infrastructure.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations using Alembic."""
    try:
        logger.info("Starting database migration...")
        
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Set database URL in config
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database.async_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False


def create_initial_migration():
    """Create initial migration if none exists."""
    try:
        logger.info("Creating initial migration...")
        
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Set database URL in config
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database.async_url)
        
        # Create initial migration
        command.revision(alembic_cfg, message="Initial migration", autogenerate=True)
        
        logger.info("Initial migration created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create initial migration: {e}")
        return False


def check_migrations():
    """Check if migrations are needed."""
    try:
        logger.info("Checking database migration status...")
        
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Set database URL in config
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database.async_url)
        
        # Check current revision
        command.current(alembic_cfg)
        
        logger.info("Migration check completed!")
        return True
        
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration script")
    parser.add_argument(
        "--action",
        choices=["migrate", "create", "check"],
        default="migrate",
        help="Action to perform (default: migrate)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Number of retries for migration (default: 5)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=10,
        help="Delay between retries in seconds (default: 10)"
    )
    
    args = parser.parse_args()
    
    success = False
    
    for attempt in range(args.retries):
        try:
            if args.action == "migrate":
                success = run_migrations()
            elif args.action == "create":
                success = create_initial_migration()
            elif args.action == "check":
                success = check_migrations()
            
            if success:
                break
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < args.retries - 1:
                logger.info(f"Retrying in {args.delay} seconds...")
                asyncio.sleep(args.delay)
    
    if not success:
        logger.error("All migration attempts failed!")
        sys.exit(1)
    else:
        logger.info("Migration completed successfully!")
        sys.exit(0) 