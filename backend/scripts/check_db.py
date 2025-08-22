#!/usr/bin/env python3
"""
データベースの接続状態とテーブルの存在を確認するスクリプト
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import test_database_connection, get_database_url
from app.config import settings
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def check_database():
    """データベースの状態を確認"""
    print("🔍 データベース接続状態を確認中...")
    
    # データベースURLを表示
    db_url = get_database_url()
    print(f"📡 データベースURL: {db_url}")
    
    # 接続テスト
    try:
        connection_status = await test_database_connection()
        if connection_status:
            print("✅ データベース接続成功")
        else:
            print("❌ データベース接続失敗")
            return False
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return False
    
    # テーブルの存在確認
    try:
        from app.core.database import engine
        from app.models.base import Base
        
        async with engine.begin() as conn:
            # テーブル一覧を取得
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📋 存在するテーブル: {len(tables)}個")
            for table in sorted(tables):
                print(f"  - {table}")
            
            # usersテーブルの詳細確認
            if 'users' in tables:
                print("\n👥 usersテーブルの構造:")
                result = await conn.execute(
                    text("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
                )
                columns = result.fetchall()
                for col in columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f"DEFAULT {col[3]}" if col[3] else ""
                    print(f"  - {col[0]}: {col[1]} {nullable} {default}")
                
                # レコード数を確認
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"  - レコード数: {count}")
            else:
                print("❌ usersテーブルが存在しません")
                return False
                
    except Exception as e:
        print(f"❌ テーブル確認エラー: {e}")
        return False
    
    print("\n✅ データベースチェック完了")
    return True

async def main():
    """メイン関数"""
    print("🚀 Bridge Line データベース診断ツール")
    print("=" * 50)
    
    try:
        success = await check_database()
        if success:
            print("\n🎉 データベースは正常に動作しています")
            sys.exit(0)
        else:
            print("\n💥 データベースに問題があります")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
