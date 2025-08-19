#!/usr/bin/env python3
"""
Migration status check script
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine
from app.core.config import settings
import structlog

logger = structlog.get_logger()


async def check_migration_status():
    """Check migration status"""
    try:
        async with engine.begin() as conn:
            # Check if alembic_version table exists
            result = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """)
            )
            alembic_exists = result.fetchone()

            if not alembic_exists[0]:
                logger.warning("alembic_version table does not exist")
                return False

            # Get current migration version
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()

            if current_version:
                logger.info(f"Current migration version: {current_version[0]}")
            else:
                logger.warning("Migration version not set")

            # Check table existence
            tables = [
                "users",
                "teams",
                "team_members",
                "voice_sessions",
                "transcriptions",
                "analyses",
                "subscriptions",
                "billings",
                "invitations",
                "audit_logs",
                "chat_rooms",
                "chat_messages",
                "chat_room_participants",
            ]

            existing_tables = []
            missing_tables = []

            for table in tables:
                result = await conn.execute(
                    text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """)
                )
                exists = result.fetchone()

                if exists[0]:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)

            logger.info(f"Existing tables: {existing_tables}")
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")

            return True

    except Exception as e:
        logger.error(f"Migration status check error: {e}")
        return False


async def main():
    """Main function"""
    logger.info("Starting migration status check")

    success = await check_migration_status()

    if success:
        logger.info("Migration status check completed successfully")
        return 0
    else:
        logger.error("Migration status check failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
