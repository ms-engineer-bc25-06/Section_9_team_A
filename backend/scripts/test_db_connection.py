#!/usr/bin/env python3
"""
データベース接続テストスクリプト
"""

import asyncio
import sys
import os
from sqlalchemy import text

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import test_database_connection, get_database_url
from app.config import settings
import structlog

logger = structlog.get_logger()


async def main():
    """メイン関数"""
    logger.info("データベース接続テストを開始します")

    # 環境情報の表示
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {get_database_url()}")

    if settings.TEST_DATABASE_URL:
        logger.info(f"Test Database URL: {settings.TEST_DATABASE_URL}")

    # データベース接続テスト
    success = await test_database_connection()

    if success:
        logger.info("✅ データベース接続テストが成功しました")
        return 0
    else:
        logger.error("❌ データベース接続テストが失敗しました")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
