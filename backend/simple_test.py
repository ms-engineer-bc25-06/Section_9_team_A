#!/usr/bin/env python3
"""
シンプルな動作確認テスト（標準ライブラリのみ）
"""

import urllib.request
import urllib.parse
import json
import sys


def test_server_basic():
    """サーバーの基本動作確認"""
    print("🔍 1. サーバー基本動作確認")
    
    try:
        with urllib.request.urlopen('http://localhost:8000/') as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ サーバー起動成功: {data}")
                return True
            else:
                print(f"❌ サーバーエラー: Status {response.status}")
                return False
    except Exception as e:
        print(f"❌ サーバー接続エラー: {e}")
        print("💡 サーバーが起動していない可能性があります")
        return False


def test_admin_endpoint():
    """管理者エンドポイントの認証確認"""
    print("\n🔍 2. 管理者エンドポイント認証確認")
    
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v1/admin/check-admin') as response:
            print(f"⚠️  予期しないアクセス成功: Status {response.status}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✅ 認証が必要（正常な動作）")
        else:
            print(f"⚠️  予期しないエラー: Status {e.code}")
    except Exception as e:
        print(f"❌ テストエラー: {e}")


def test_health_endpoint():
    """ヘルスチェックエンドポイント"""
    print("\n🔍 3. ヘルスチェックエンドポイント")
    
    try:
        with urllib.request.urlopen('http://localhost:8000/health') as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ ヘルスチェック成功: {data}")
            else:
                print(f"❌ ヘルスチェックエラー: Status {response.status}")
    except Exception as e:
        print(f"❌ ヘルスチェックエラー: {e}")


def main():
    """メインテスト実行"""
    print("🚀 シンプル動作確認テスト開始\n")
    
    # 1. サーバー基本動作確認
    server_ok = test_server_basic()
    
    if not server_ok:
        print("\n❌ サーバーが起動していません")
        print("\n📋 サーバー起動手順:")
        print("1. 新しいターミナルを開く")
        print("2. cd backend")
        print("3. 以下のコマンドを実行:")
        print('$env:DATABASE_URL="postgresql+asyncpg://bridge_user:bridge_password@localhost:5432/bridge_line_db"')
        print('$env:INITIAL_ADMIN_FIREBASE_UID="g7lzX9SnUUeBpRAae9CjynV0CX43"')
        print('$env:INITIAL_ADMIN_EMAIL="admin@example.com"')
        print('$env:INITIAL_ADMIN_DISPLAY_NAME="管理者1"')
        print("python -m uvicorn app.main:app --reload")
        return
    
    # 2. 管理者エンドポイント認証確認
    test_admin_endpoint()
    
    # 3. ヘルスチェックエンドポイント
    test_health_endpoint()
    
    print("\n🎉 基本テスト完了！")
    print("\n📋 次のステップ（フロントエンドテスト）:")
    print("1. フロントエンドを起動")
    print("2. Firebase認証でログイン")
    print("3. 管理者ユーザー（admin@example.com）でログイン")
    print("4. 管理者画面にアクセス可能か確認")
    print("5. 一般ユーザーでログイン")
    print("6. 管理者画面アクセスが拒否されるか確認")


if __name__ == "__main__":
    main()
