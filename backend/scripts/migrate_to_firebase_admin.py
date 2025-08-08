"""
DB管理からFirebase Custom Claimsへの移行スクリプト
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def migrate_db_admins_to_firebase():
    """DBの管理者ユーザーをFirebase Custom Claimsに移行"""
    try:
        from app.core.database import get_db
        from app.models.user import User
        from sqlalchemy import select
        from app.core.firebase_client import set_admin_claim
        
        print("🔄 DB管理者からFirebase Custom Claimsへの移行開始")
        
        async for db in get_db():
            try:
                # DBの管理者ユーザーを取得
                result = await db.execute(select(User).where(User.is_admin == True))
                db_admin_users = result.scalars().all()
                
                print(f"📊 移行対象管理者数: {len(db_admin_users)}")
                
                migrated_count = 0
                for user in db_admin_users:
                    if user.firebase_uid:
                        try:
                            # Firebase Custom Claimsに管理者権限を設定
                            success = set_admin_claim(user.firebase_uid, True)
                            if success:
                                migrated_count += 1
                                print(f"✅ 移行成功: {user.email} ({user.firebase_uid})")
                            else:
                                print(f"❌ 移行失敗: {user.email} ({user.firebase_uid})")
                        except Exception as e:
                            print(f"❌ 移行エラー: {user.email} - {e}")
                    else:
                        print(f"⚠️ Firebase UIDなし: {user.email}")
                
                print(f"\n📊 移行完了: {migrated_count}/{len(db_admin_users)} 成功")
                
            except Exception as e:
                print(f"❌ 移行処理エラー: {e}")
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ エラー: {e}")

async def verify_migration():
    """移行結果を確認"""
    try:
        from app.core.database import get_db
        from app.models.user import User
        from sqlalchemy import select
        from app.core.firebase_client import is_admin_user, get_user_claims
        
        print("\n🔍 移行結果確認")
        
        async for db in get_db():
            try:
                # DBの管理者ユーザーを取得
                result = await db.execute(select(User).where(User.is_admin == True))
                db_admin_users = result.scalars().all()
                
                print(f"📊 確認対象: {len(db_admin_users)} ユーザー")
                
                for user in db_admin_users:
                    if user.firebase_uid:
                        firebase_admin = is_admin_user(user.firebase_uid)
                        claims = get_user_claims(user.firebase_uid)
                        
                        status = "✅" if firebase_admin else "❌"
                        print(f"{status} {user.email}: DB={user.is_admin}, Firebase={firebase_admin}")
                        if claims:
                            print(f"   Claims: {claims}")
                    else:
                        print(f"⚠️ {user.email}: Firebase UIDなし")
                
            except Exception as e:
                print(f"❌ 確認エラー: {e}")
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ エラー: {e}")

async def main():
    """メイン実行関数"""
    print("🚀 Firebase管理者移行ツール")
    print("1. DB管理者をFirebase Custom Claimsに移行")
    print("2. 移行結果を確認")
    
    choice = input("選択してください (1/2): ").strip()
    
    if choice == "1":
        confirm = input("移行を実行しますか？ (y/N): ").strip().lower()
        if confirm == "y":
            await migrate_db_admins_to_firebase()
        else:
            print("移行をキャンセルしました")
    
    elif choice == "2":
        await verify_migration()
    
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    asyncio.run(main())
