"""
アプリケーション起動時の初期化処理
環境変数で管理者情報が設定されている場合、自動で初期管理者を作成
"""

import os
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import structlog

from app.core.database import async_session
from app.core.firebase_client import set_admin_claim

logger = structlog.get_logger()


async def initialize_admin_user():
    """
    環境変数から初期管理者を自動作成
    INITIAL_ADMIN_FIREBASE_UID と INITIAL_ADMIN_EMAIL が設定されている場合のみ実行
    """
    
    firebase_uid = os.getenv("INITIAL_ADMIN_FIREBASE_UID")
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    display_name = os.getenv("INITIAL_ADMIN_DISPLAY_NAME", "システム管理者")
    
    if not firebase_uid or not email:
        logger.info("ℹ️  初期管理者の環境変数が設定されていません。スキップします。")
        return
    
    logger.info(f"🚀 初期管理者の自動設定を開始: {email}")
    
    try:
        async with async_session() as db:
            # 既存の管理者ユーザーをチェック
            result = await db.execute(
                text("SELECT id, email, is_admin FROM users WHERE firebase_uid = :uid"),
                {"uid": firebase_uid}
            )
            existing_user = result.fetchone()
            
            if existing_user and existing_user[2]:  # is_admin = True
                logger.info(f"✅ 管理者は既に設定済みです: {existing_user[1]}")
                return
            
            # デフォルトロールを作成（存在しない場合のみ）
            await db.execute(text("""
                INSERT INTO roles (name, display_name, description, is_active, created_at)
                VALUES 
                    ('admin', '管理者', 'システム管理者', true, :now),
                    ('user', 'ユーザー', '一般ユーザー', true, :now)
                ON CONFLICT (name) DO NOTHING
            """), {"now": datetime.utcnow()})
            
            logger.info("✅ デフォルトロールを確認・作成しました")
            
            # 管理者ユーザーを作成または更新
            if existing_user:
                # 既存ユーザーを管理者に昇格
                await db.execute(
                    text("UPDATE users SET is_admin = true, updated_at = :now WHERE firebase_uid = :uid"),
                    {"now": datetime.utcnow(), "uid": firebase_uid}
                )
                user_id = existing_user[0]
                logger.info(f"✅ 既存ユーザーを管理者に昇格: {existing_user[1]}")
            else:
                # 新規管理者ユーザーを作成
                result = await db.execute(text("""
                    INSERT INTO users (
                        firebase_uid, email, username, display_name, 
                        is_active, is_admin, created_at, updated_at
                    ) VALUES (:uid, :email, :username, :display_name, true, true, :now, :now)
                    RETURNING id
                """), {
                    "uid": firebase_uid,
                    "email": email,
                    "username": email.split('@')[0],
                    "display_name": display_name,
                    "now": datetime.utcnow()
                })
                user_id = result.fetchone()[0]
                logger.info(f"✅ 新規管理者ユーザーを作成: {email}")
            
            # 管理者ロールを割り当て
            role_result = await db.execute(
                text("SELECT id FROM roles WHERE name = 'admin'")
            )
            admin_role_id = role_result.fetchone()[0]
            
            # 既存のロール割り当てをチェック
            role_check = await db.execute(text("""
                SELECT id FROM user_roles WHERE user_id = :user_id AND role_id = :role_id
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
                logger.info("✅ 管理者ロールを割り当てました")
            else:
                logger.info("✅ 管理者ロールは既に割り当て済みです")
            
            await db.commit()
            
            # Firebase Custom Claimsを設定
            try:
                success = set_admin_claim(firebase_uid, True)
                if success:
                    logger.info("✅ Firebase Custom Claimsを設定しました")
                else:
                    logger.warning("⚠️  Firebase Custom Claimsの設定に失敗しました")
            except Exception as e:
                logger.warning(f"⚠️  Firebase Custom Claimsエラー: {e}")
            
            logger.info(f"🎉 初期管理者設定完了: {email}")
            
    except Exception as e:
        logger.error(f"❌ 初期管理者設定エラー: {e}")


async def startup_events():
    """アプリケーション起動時に実行される初期化処理"""
    logger.info("🚀 アプリケーション初期化を開始...")
    
    # 初期管理者の自動作成
    await initialize_admin_user()
    
    logger.info("✅ アプリケーション初期化完了")


if __name__ == "__main__":
    # スタンドアロンでも実行可能
    asyncio.run(startup_events())
