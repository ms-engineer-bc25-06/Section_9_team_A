#!/usr/bin/env python3
"""データベースの現在の状態を確認するスクリプト"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# データベース接続設定
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/bridgeline")

def check_database_status():
    """データベースの状態を確認"""
    try:
        # エンジンの作成
        engine = create_engine(DATABASE_URL)
        
        # 接続テスト
        with engine.connect() as connection:
            print("✅ データベース接続成功")
            
            # テーブル一覧の取得
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📋 既存テーブル: {tables}")
            
            # alembic_versionテーブルの確認
            if 'alembic_version' in tables:
                result = connection.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"🔧 現在のマイグレーションバージョン: {version}")
            else:
                print("⚠️  alembic_versionテーブルが存在しません")
            
            # 特定のテーブルの詳細確認
            for table_name in ['organizations', 'organization_members', 'payments', 'subscriptions']:
                if table_name in tables:
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    print(f"📊 {table_name}テーブルのカラム: {columns}")
                else:
                    print(f"❌ {table_name}テーブルは存在しません")
                    
    except SQLAlchemyError as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 データベース状態確認中...")
    success = check_database_status()
    if success:
        print("✅ データベース状態確認完了")
    else:
        print("❌ データベース状態確認失敗")
        sys.exit(1)
