"""
管理者・一般ユーザーの動作確認テストスクリプト
"""

import asyncio
import aiohttp
import json


async def test_server_health():
    """サーバーの基本動作確認"""
    print("🔍 1. サーバー基本動作確認")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ サーバー起動成功: {data}")
                    return True
                else:
                    print(f"❌ サーバーエラー: Status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ サーバー接続エラー: {e}")
        return False


async def test_bootstrap_admin():
    """初期管理者作成テスト"""
    print("\n🔍 2. 初期管理者作成テスト")
    
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                "firebase_uid": "g7lzX9SnUUeBpRAae9CjynV0CX43",
                "email": "admin@example.com",
                "display_name": "管理者1"
            }
            
            async with session.post(
                'http://localhost:8000/api/v1/admin/bootstrap-admin',
                json=data
            ) as response:
                result = await response.text()
                
                if response.status == 200:
                    print("✅ 管理者作成成功（または既存確認）")
                    print(f"レスポンス: {result}")
                elif response.status == 400:
                    print("✅ 既に管理者が存在（正常な動作）")
                    print(f"レスポンス: {result}")
                else:
                    print(f"❌ 管理者作成エラー: Status {response.status}")
                    print(f"レスポンス: {result}")
                    
    except Exception as e:
        print(f"❌ 管理者作成テストエラー: {e}")


async def test_admin_check():
    """管理者権限チェックテスト（認証なし）"""
    print("\n🔍 3. 管理者権限チェックテスト")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/api/v1/admin/check-admin') as response:
                result = await response.text()
                
                if response.status == 401:
                    print("✅ 認証が必要（正常な動作）")
                    print(f"レスポンス: {result}")
                else:
                    print(f"⚠️  予期しないステータス: {response.status}")
                    print(f"レスポンス: {result}")
                    
    except Exception as e:
        print(f"❌ 管理者権限チェックエラー: {e}")


async def test_admin_users_list():
    """管理者一覧取得テスト（認証なし）"""
    print("\n🔍 4. 管理者一覧取得テスト")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/api/v1/admin/admin-users') as response:
                result = await response.text()
                
                if response.status == 401:
                    print("✅ 認証が必要（正常な動作）")
                    print(f"レスポンス: {result}")
                else:
                    print(f"⚠️  予期しないステータス: {response.status}")
                    print(f"レスポンス: {result}")
                    
    except Exception as e:
        print(f"❌ 管理者一覧取得エラー: {e}")


async def main():
    """メインテスト実行"""
    print("🚀 管理者・一般ユーザー動作確認テスト開始\n")
    
    # 1. サーバー基本動作確認
    server_ok = await test_server_health()
    if not server_ok:
        print("❌ サーバーが起動していません。先にサーバーを起動してください。")
        return
    
    # 2. 初期管理者作成テスト
    await test_bootstrap_admin()
    
    # 3. 管理者権限チェックテスト
    await test_admin_check()
    
    # 4. 管理者一覧取得テスト
    await test_admin_users_list()
    
    print("\n🎉 基本テスト完了！")
    print("\n📋 次のステップ:")
    print("1. フロントエンドでFirebase認証を行う")
    print("2. 管理者ユーザーでログイン")
    print("3. 管理者画面にアクセス")
    print("4. 一般ユーザーでログイン")
    print("5. 管理者画面アクセスが拒否されることを確認")


if __name__ == "__main__":
    asyncio.run(main())