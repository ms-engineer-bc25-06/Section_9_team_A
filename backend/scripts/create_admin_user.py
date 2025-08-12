"""
admin@example.com 管理者ユーザーを作成するスクリプト
"""

import asyncio
from datetime import datetime
from app.core.database import async_session
from sqlalchemy import text
from app.integrations.firebase_client import set_admin_claim


async def create_admin_user():
    """admin@example.com 管理者ユーザーを作成"""
    
    print("🚀 admin@example.com 管理者ユーザーを作成します")
    
    firebase_uid = "admin_real_firebase_uid_12345"  # 実際のFirebase UIDに置き換え
    email = "admin@example.com"
    display_name = "システム管理者"
    
    try:
        async with async_session() as db:
            # 既存ユーザーチェック
            result = await db.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": email}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"⚠️  {email} は既に存在します (ID: {existing_user[0]})")
                
                # 管理者フラグを確認・更新
                await db.execute(
                    text("UPDATE users SET is_admin = true WHERE email = :email"),
                    {"email": email}
                )
                await db.commit()
                print(f"✅ {email} を管理者に更新しました")
            else:
                # 新規ユーザー作成
                await db.execute(text("""
                    INSERT INTO users (
                        firebase_uid, email, username, display_name,
                        is_active, is_admin, created_at, updated_at
                    ) VALUES (
                        :firebase_uid, :email, :username, :display_name,
                        true, true, :now, :now
                    )
                """), {
                    "firebase_uid": firebase_uid,
                    "email": email,
                    "username": "admin",
                    "display_name": display_name,
                    "now": datetime.utcnow()
                })
                
                await db.commit()
                print(f"✅ {email} を新規作成しました")
            
            # 管理者ロールを確認・割り当て
            # ロールIDを取得
            role_result = await db.execute(
                text("SELECT id FROM roles WHERE name = 'admin'")
            )
            admin_role = role_result.fetchone()
            
            if admin_role:
                admin_role_id = admin_role[0]
                
                # ユーザーIDを取得
                user_result = await db.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": email}
                )
                user = user_result.fetchone()
                user_id = user[0]
                
                # ロール割り当てチェック
                role_check = await db.execute(text("""
                    SELECT id FROM user_roles 
                    WHERE user_id = :user_id AND role_id = :role_id
                """), {"user_id": user_id, "role_id": admin_role_id})
                
                if not role_check.fetchone():
                    # 新規ロール割り当て
                    await db.execute(text("""
                        INSERT INTO user_roles (user_id, role_id, is_active, assigned_by, assigned_at)
                        VALUES (:user_id, :role_id, true, :user_id, :now)
                    """), {
                        "user_id": user_id,
                        "role_id": admin_role_id,
                        "now": datetime.utcnow()
                    })
                    await db.commit()
                    print("✅ 管理者ロールを割り当てました")
                else:
                    print("✅ 管理者ロールは既に割り当て済みです")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    print(f"""
🎉 admin@example.com の設定完了！

📋 次のステップ:
1. Firebase Authentication で admin@example.com のユーザーを作成
   - Firebase Console → Authentication → Users → Add user
   - Email: admin@example.com
   - パスワード: 任意（6文字以上）

2. Firebase UID を確認して、以下のコマンドで Firebase Custom Claims を設定:
   python -c "from app.integrations.firebase_client import set_admin_claim; set_admin_claim('実際のFirebaseUID', True)"

3. フロントエンドで admin@example.com でログインテスト
    """)
    
    return True


async def main():
    """メイン実行"""
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())