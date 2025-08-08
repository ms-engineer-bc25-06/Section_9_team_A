#!/usr/bin/env python3
"""
マイグレーション状態確認スクリプト
"""

import asyncio
import sys
import os
from sqlalchemy import text

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine
from app.config import settings
import structlog

logger = structlog.get_logger()


async def check_migration_status():
    """マイグレーションの状態を確認"""
    try:
        async with engine.begin() as conn:
            # alembic_versionテーブルの存在確認
            result = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """)
            )
            alembic_exists = await result.fetchone()

            if not alembic_exists[0]:
                logger.warning("alembic_versionテーブルが存在しません")
                return False

            # 現在のマイグレーションバージョンを取得
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = await result.fetchone()

            if current_version:
                logger.info(f"現在のマイグレーションバージョン: {current_version[0]}")
            else:
                logger.warning("マイグレーションバージョンが設定されていません")

            # テーブルの存在確認
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
                exists = await result.fetchone()

                if exists[0]:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)

            logger.info(f"存在するテーブル: {existing_tables}")
            if missing_tables:
                logger.warning(f"存在しないテーブル: {missing_tables}")

            return True

    except Exception as e:
        logger.error(f"マイグレーション状態確認エラー: {e}")
        return False


async def main():
    """メイン関数"""
    logger.info("マイグレーション状態確認を開始します")

    success = await check_migration_status()

    if success:
        logger.info("✅ マイグレーション状態確認が完了しました")
        return 0
    else:
        logger.error("❌ マイグレーション状態確認で問題が発生しました")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
