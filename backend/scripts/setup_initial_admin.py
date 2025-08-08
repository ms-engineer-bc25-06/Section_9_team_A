"""
初期管理者設定スクリプト
システム初回起動時に最初の管理者を設定する
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # scripts/の親ディレクトリ（backend/）
sys.path.append(backend_dir)

async def setup_initial_admin():
    """初期管理者を設定"""
    try:
        from app.core.database import get_db
        from app.models.user import User
        from app.models.role import Role, UserRole
        from app.services.role_service import RoleService
        from app.core.firebase_client import set_admin_claim
        from sqlalchemy import select
        
        print("🚀 初期管理者設定ツール")
        print("=" * 50)
        
        # 管理者情報を入力
        email = input("管理者のメールアドレス: ").strip()
        firebase_uid = input("Firebase UID: ").strip()
        display_name = input("表示名: ").strip()
        
        if not email or not firebase_uid:
            print("❌ メールアドレスとFirebase UIDは必須です")
            return False
        
        async for db in get_db():
            try:
                # 1. デフォルトロールを作成
                role_service = RoleService(db)
                await role_service.create_default_roles()
                print("✅ デフォルトロールを作成しました")
                
                # 2. ユーザーを作成または取得
                result = await db.execute(
                    select(User).where(User.firebase_uid == firebase_uid)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    # 新規ユーザー作成
                    user = User(
                        firebase_uid=firebase_uid,
                        email=email,
                        display_name=display_name,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                    print(f"✅ 新規ユーザーを作成しました: {email}")
                else:
                    print(f"✅ 既存ユーザーを使用: {email}")
                
                # 3. 管理者ロールを割り当て
                success = await role_service.assign_role_to_user(
                    user_id=user.id,
                    role_name="admin",
                    assigned_by=user.id,  # 自己割り当て
                    expires_at=None  # 永続
                )
                
                if success:
                    print("✅ 管理者ロールを割り当てました")
                else:
                    print("❌ 管理者ロールの割り当てに失敗しました")
                    return False
                
                # 4. Firebase Custom Claimsを設定
                firebase_success = set_admin_claim(firebase_uid, True)
                if firebase_success:
                    print("✅ Firebase Custom Claimsを設定しました")
                else:
                    print("⚠️ Firebase Custom Claimsの設定に失敗しました")
                
                # 5. 確認
                print("\n📊 設定結果:")
                print(f"  ユーザーID: {user.id}")
                print(f"  メール: {user.email}")
                print(f"  Firebase UID: {user.firebase_uid}")
                print(f"  表示名: {user.display_name}")
                print(f"  管理者権限: ✅")
                
                return True
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                await db.rollback()
                return False
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def check_admin_status():
    """管理者状況を確認"""
    try:
        from app.core.database import get_db
        from app.models.user import User
        from app.models.role import Role, UserRole
        from sqlalchemy import select, and_
        
        print("🔍 管理者状況確認")
        print("=" * 30)
        
        async for db in get_db():
            try:
                # 管理者ロールを持つユーザーを確認
                result = await db.execute(
                    select(User, UserRole, Role).join(UserRole).join(Role).where(
                        and_(
                            UserRole.is_active == True,
                            Role.name == "admin",
                            Role.is_active == True
                        )
                    )
                )
                admin_users = result.all()
                
                print(f"📊 管理者ユーザー数: {len(admin_users)}")
                
                for user, user_role, role in admin_users:
                    print(f"  ユーザーID: {user.id}")
                    print(f"  メール: {user.email}")
                    print(f"  Firebase UID: {user.firebase_uid}")
                    print(f"  表示名: {user.display_name}")
                    print(f"  ロール割り当て日: {user_role.assigned_at}")
                    print(f"  有効期限: {user_role.expires_at or '永続'}")
                    print("  ---")
                
                if not admin_users:
                    print("⚠️ 管理者ユーザーが見つかりません")
                    print("初期管理者設定を実行してください")
                
            except Exception as e:
                print(f"❌ 確認エラー: {e}")
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ エラー: {e}")

async def main():
    """メイン実行関数"""
    print("🚀 初期管理者設定ツール")
    print("1. 初期管理者を設定")
    print("2. 管理者状況を確認")
    
    choice = input("選択してください (1/2): ").strip()
    
    if choice == "1":
        confirm = input("初期管理者を設定しますか？ (y/N): ").strip().lower()
        if confirm == "y":
            success = await setup_initial_admin()
            if success:
                print("\n🎉 初期管理者設定が完了しました！")
                print("これで管理者としてログインできます")
            else:
                print("\n❌ 初期管理者設定に失敗しました")
        else:
            print("設定をキャンセルしました")
    
    elif choice == "2":
        await check_admin_status()
    
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    asyncio.run(main())
