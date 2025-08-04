#!/usr/bin/env python3
"""Database initialization script for marketplace services."""

# Python imports
import asyncio
import logging
import sys
from pathlib import Path

# Local imports
from src.shared.infrastructure.logging import setup_logging
from src.shared.infrastructure.database import init_db, close_db


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def initialize_database() -> bool:
    """
    Initialize database tables.
    
    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database tables
        await init_db()
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


async def check_database() -> bool:
    """
    Check if database is accessible.
    
    Returns:
        bool: True if database is accessible, False otherwise.
    """
    try:
        logger.info("Checking database connection...")
        
        # Try to initialize database (this will fail if connection is not available)
        await init_db()
        
        logger.info("Database connection check completed!")
        return True
        
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--action",
        choices=["init", "check"],
        default="init",
        help="Action to perform (default: init)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Number of retries for initialization (default: 5)"
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
            if args.action == "init":
                success = asyncio.run(initialize_database())
            elif args.action == "check":
                success = asyncio.run(check_database())
            
            if success:
                break
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < args.retries - 1:
                logger.info(f"Retrying in {args.delay} seconds...")
                asyncio.sleep(args.delay)
    
    # Clean up database connections
    try:
        asyncio.run(close_db())
    except Exception as e:
        logger.warning(f"Failed to close database connections: {e}")
    
    if not success:
        logger.error("All initialization attempts failed!")
        sys.exit(1)
    else:
        logger.info("Database initialization completed successfully!")
        sys.exit(0) 