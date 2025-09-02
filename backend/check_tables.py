#!/usr/bin/env python3
"""
データベースのテーブル一覧を確認するスクリプト
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check_tables():
    """データベースのテーブル一覧を確認"""
    try:
        async with engine.begin() as conn:
            # テーブル一覧を取得
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            )
            tables = result.fetchall()
            
            print("存在するテーブル:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # organization_membersテーブルの詳細を確認
            print("\norganization_membersテーブルの詳細:")
            try:
                result = await conn.execute(
                    text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'organization_members' ORDER BY ordinal_position")
                )
                columns = result.fetchall()
                if columns:
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
                else:
                    print("  organization_membersテーブルは存在しません")
            except Exception as e:
                print(f"  テーブル詳細確認エラー: {e}")
                
    except Exception as e:
        print(f"データベース接続エラー: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
