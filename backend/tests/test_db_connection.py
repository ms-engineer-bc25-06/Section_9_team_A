#!/usr/bin/env python3
"""
DB接続テストスクリプト
"""

import sys
import os
import asyncio
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_db_connection():
    """DB接続のテスト"""
    print("=== DB接続テスト ===")
    
    try:
        from app.core.database import get_db
        from app.models.user import User
        from sqlalchemy import select
        
        print("✅ データベースモジュールのインポート成功")
        
        # DB接続テスト
        async for db in get_db():
            try:
                # 簡単なクエリを実行
                result = await db.execute(select(User).limit(1))
                users = result.scalars().all()
                print(f"✅ DB接続成功！ユーザー数: {len(users)}")
                await db.close()
                return True
            except Exception as e:
                print(f"❌ DB接続失敗: {e}")
                await db.close()
                return False
                
    except Exception as e:
        print(f"❌ データベースモジュールのインポート失敗: {e}")
        return False

async def test_auth_service_db():
    """認証サービスのDB操作テスト"""
    print("\n=== 認証サービスDB操作テスト ===")
    
    try:
        from app.services.auth_service import AuthService
        from app.core.database import get_db
        
        print("✅ 認証サービスのインポート成功")
        
        # AuthServiceのインスタンス作成テスト
        async for db in get_db():
            try:
                auth_service = AuthService(db)
                print("✅ AuthServiceインスタンス作成成功")
                await db.close()
                return True
            except Exception as e:
                print(f"❌ AuthServiceインスタンス作成失敗: {e}")
                await db.close()
                return False
                
    except Exception as e:
        print(f"❌ 認証サービスのインポート失敗: {e}")
        return False

async def main():
    """メイン実行関数"""
    print("🚀 DB接続テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now()}")
    
    tests = [
        ("DB接続", test_db_connection),
        ("認証サービスDB操作", test_auth_service_db),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name}テスト成功")
            else:
                print(f"❌ {test_name}テスト失敗")
        except Exception as e:
            print(f"❌ {test_name}テストでエラー: {e}")
    
    print(f"\n📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのDBテストが成功しました！")
    else:
        print("⚠️ 一部のDBテストが失敗しました。")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
