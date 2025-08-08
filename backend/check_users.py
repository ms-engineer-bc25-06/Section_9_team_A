#!/usr/bin/env python3
"""
データベース内のユーザー状態確認スクリプト
"""

import asyncio
from app.core.database import async_session
from sqlalchemy import text
from app.core.firebase_client import get_user_claims, is_admin_user


async def check_users():
    """データベース内のユーザーとFirebase設定を確認"""
    
    print("🔍 データベース内のユーザー確認\n")
    
    try:
        async with async_session() as db:
            # 全ユーザーを取得
            result = await db.execute(text("""
                SELECT firebase_uid, email, display_name, is_admin, created_at 
                FROM users 
                ORDER BY created_at
            """))
            users = result.fetchall()
            
            if not users:
                print("❌ データベースにユーザーが存在しません")
                return
            
            print("=== データベース内のユーザー一覧 ===")
            for i, user in enumerate(users, 1):
                firebase_uid, email, display_name, is_admin, created_at = user
                
                print(f"\n{i}. ユーザー情報:")
                print(f"   Firebase UID: {firebase_uid}")
                print(f"   Email: {email}")
                print(f"   Display Name: {display_name}")
                print(f"   DB管理者フラグ: {is_admin}")
                print(f"   作成日時: {created_at}")
                
                # Firebase Custom Claimsも確認
                try:
                    claims = get_user_claims(firebase_uid)
                    firebase_admin = claims.get('admin', False) if claims else False
                    print(f"   Firebase管理者フラグ: {firebase_admin}")
                    
                    # 整合性チェック
                    if is_admin == firebase_admin:
                        print("   ✅ DB と Firebase の設定が一致")
                    else:
                        print("   ⚠️  DB と Firebase の設定が不一致")
                        
                except Exception as e:
                    print(f"   ❌ Firebase確認エラー: {e}")
            
            print(f"\n=== 合計ユーザー数: {len(users)} ===")
            
    except Exception as e:
        print(f"❌ データベース確認エラー: {e}")


async def main():
    """メイン実行"""
    await check_users()
    
    print("\n📋 問題解決のヒント:")
    print("1. 'admin@example.com' でログインできない場合:")
    print("   → Firebase Authentication でこのメールアドレスのユーザーを作成")
    print("2. '管理者ではありません' エラーの場合:")
    print("   → DB の is_admin フラグまたは Firebase Custom Claims を確認")
    print("3. ユーザーが見つからない場合:")
    print("   → まず Firebase でユーザー登録してからログイン")


if __name__ == "__main__":
    asyncio.run(main())
