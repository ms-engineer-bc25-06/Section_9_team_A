"""
基本的な認証機能テストスクリプト
"""

import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_firebase_client():
    """Firebaseクライアントのテスト"""
    print("=== Firebaseクライアントテスト ===")
    
    try:
        from app.core.firebase_client import verify_firebase_token
        print("✅ Firebaseクライアントのインポート成功")
        return True
    except Exception as e:
        print(f"❌ Firebaseクライアントのインポート失敗: {e}")
        return False

def test_auth_service():
    """認証サービスのテスト"""
    print("\n=== 認証サービステスト ===")
    
    try:
        from app.services.auth_service import AuthService
        print("✅ 認証サービスのインポート成功")
        return True
    except Exception as e:
        print(f"❌ 認証サービスのインポート失敗: {e}")
        return False

def test_auth_api():
    """認証APIのテスト"""
    print("\n=== 認証APIテスト ===")
    
    try:
        from app.api.v1.auth import router
        print("✅ 認証APIのインポート成功")
        return True
    except Exception as e:
        print(f"❌ 認証APIのインポート失敗: {e}")
        return False

def test_user_model():
    """ユーザーモデルのテスト"""
    print("\n=== ユーザーモデルテスト ===")
    
    try:
        from app.models.user import User
        print("✅ ユーザーモデルのインポート成功")
        
        # モデルの属性確認
        user_attrs = dir(User)
        required_attrs = ['id', 'email', 'firebase_uid', 'is_active', 'is_admin', 'last_login_at', 'last_logout_at']
        
        missing_attrs = []
        for attr in required_attrs:
            if attr not in user_attrs:
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"❌ 不足している属性: {missing_attrs}")
            return False
        else:
            print("✅ 必要な属性がすべて存在")
            return True
            
    except Exception as e:
        print(f"❌ ユーザーモデルのインポート失敗: {e}")
        return False

def test_jwt_functions():
    """JWT関数のテスト"""
    print("\n=== JWT関数テスト ===")
    
    try:
        from app.core.auth import create_access_token, create_refresh_token, verify_token, verify_refresh_token
        print("✅ JWT関数のインポート成功")
        
        # テスト用データ
        test_data = {"sub": "test@example.com"}
        
        # アクセストークン作成テスト
        access_token = create_access_token(test_data)
        print(f"✅ アクセストークン作成成功: {access_token[:20]}...")
        
        # リフレッシュトークン作成テスト
        refresh_token = create_refresh_token(test_data)
        print(f"✅ リフレッシュトークン作成成功: {refresh_token[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT関数のテスト失敗: {e}")
        return False

def test_schemas():
    """スキーマのテスト"""
    print("\n=== スキーマテスト ===")
    
    try:
        from app.schemas.auth import Token, FirebaseAuthRequest, RefreshTokenRequest
        from app.schemas.user import UserMeResponse
        print("✅ スキーマのインポート成功")
        return True
    except Exception as e:
        print(f"❌ スキーマのインポート失敗: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🚀 基本的な認証機能テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now()}")
    
    tests = [
        ("Firebaseクライアント", test_firebase_client),
        ("認証サービス", test_auth_service),
        ("認証API", test_auth_api),
        ("ユーザーモデル", test_user_model),
        ("JWT関数", test_jwt_functions),
        ("スキーマ", test_schemas),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}テスト成功")
            else:
                print(f"❌ {test_name}テスト失敗")
        except Exception as e:
            print(f"❌ {test_name}テストでエラー: {e}")
    
    print(f"\n📊 テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
    else:
        print("⚠️ 一部のテストが失敗しました。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
