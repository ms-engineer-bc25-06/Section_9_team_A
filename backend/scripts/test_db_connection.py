#!/usr/bin/env python3
"""
Database connection test script
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import test_database_connection, get_database_url
from app.config import settings
import structlog

logger = structlog.get_logger()


async def main():
    """Main function"""
    logger.info("Starting database connection test")

    # Display environment information
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {get_database_url()}")

    if settings.TEST_DATABASE_URL:
        logger.info(f"Test Database URL: {settings.TEST_DATABASE_URL}")

    # Test database connection
    success = await test_database_connection()

    if success:
        logger.info("Database connection test successful")
        return 0
    else:
        logger.error("Database connection test failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
