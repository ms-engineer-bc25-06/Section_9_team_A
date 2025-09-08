"""
userテーブルのデータを指定された内容に修正するスクリプト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from sqlalchemy import text
import structlog

logger = structlog.get_logger()


async def update_user_table_data():
    """userテーブルのデータを修正"""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("userテーブルのデータ修正を開始します")

            # 1. 既存の不要なユーザーを削除
            logger.info("1. 不要なユーザーを削除中...")
            delete_query = text("DELETE FROM users WHERE id IN (16, 25)")
            await db.execute(delete_query)
            logger.info("ID 16, 25のユーザーを削除しました")

            # 2. 既存のユーザーを更新
            logger.info("2. 既存のユーザーを更新中...")

            # ID 3: test_user → test-2@example.com
            update_query = text("""
                UPDATE users 
                SET email = 'test-2@example.com', username = 'テストユーザー2', 
                    firebase_uid = 'fJlRsfL7bGfCJwRyJwZDuUKFmqs1'
                WHERE id = 3
            """)
            await db.execute(update_query)
            logger.info("ID 3: test_user → test-2@example.com に更新")

            # ID 5: test-1@example.com → test-4@example.com
            update_query = text("""
                UPDATE users 
                SET email = 'test-4@example.com', username = 'テストユーザー4', 
                    firebase_uid = 'D0CnNOhwHXfpYCTLNIHZUOZ1byT2'
                WHERE id = 5
            """)
            await db.execute(update_query)
            logger.info("ID 5: test-1@example.com → test-4@example.com に更新")

            # ID 6: admin@example.com → erika@bridgeline.com
            update_query = text("""
                UPDATE users 
                SET email = 'erika@bridgeline.com', username = 'ペルソナ：えりか', 
                    firebase_uid = 'rI5UNAAjEBOrOSDq7M1j7ruQxRC3'
                WHERE id = 6
            """)
            await db.execute(update_query)
            logger.info("ID 6: admin@example.com → erika@bridgeline.com に更新")

            # ID 9: test@example.com → test-3@example.com
            update_query = text("""
                UPDATE users 
                SET email = 'test-3@example.com', username = 'テストユーザー3', 
                    firebase_uid = 'bhRfFPr6CuU0ICSoXfSSWkj5jrP2'
                WHERE id = 9
            """)
            await db.execute(update_query)
            logger.info("ID 9: test@example.com → test-3@example.com に更新")

            # 3. 新しいユーザーを追加
            logger.info("3. 新しいユーザーを追加中...")

            # ID 1: admin@example.com
            insert_query = text("""
                INSERT INTO users (id, email, username, firebase_uid, is_admin, is_active, is_verified)
                VALUES (1, 'admin@example.com', '管理者', 'g7lzX9SnUUeBpRAae9CjynV0CX43', true, true, true)
            """)
            await db.execute(insert_query)
            logger.info("ID 1: admin@example.com を追加")

            # ID 2: test-1@example.com
            insert_query = text("""
                INSERT INTO users (id, email, username, firebase_uid, is_admin, is_active, is_verified)
                VALUES (2, 'test-1@example.com', 'テストユーザー1', 'HUsqkQ1P4SbK68NU1mP75ugdSB03', false, true, true)
            """)
            await db.execute(insert_query)
            logger.info("ID 2: test-1@example.com を追加")

            # ID 7: uchi@bridgeline.com
            insert_query = text("""
                INSERT INTO users (id, email, username, firebase_uid, is_admin, is_active, is_verified)
                VALUES (7, 'uchi@bridgeline.com', 'ペルソナ：うっちー', 'zmTn7PmUC6Yjmn78GdM9qrkoPhq2', false, true, true)
            """)
            await db.execute(insert_query)
            logger.info("ID 7: uchi@bridgeline.com を追加")

            # ID 10: shizuka@bridgeline.com
            insert_query = text("""
                INSERT INTO users (id, email, username, firebase_uid, is_admin, is_active, is_verified)
                VALUES (10, 'shizuka@bridgeline.com', 'しづかさん', 'l97JVsZdEVSXvUB6491Q1LoqXSB2', false, true, true)
            """)
            await db.execute(insert_query)
            logger.info("ID 10: shizuka@bridgeline.com を追加")

            # ID 11: asuka@bridgeline.com
            insert_query = text("""
                INSERT INTO users (id, email, username, firebase_uid, is_admin, is_active, is_verified)
                VALUES (11, 'asuka@bridgeline.com', 'あっすー', 'thlwiFkQjgSycs2rglUZoHGThGh1', false, true, true)
            """)
            await db.execute(insert_query)
            logger.info("ID 11: asuka@bridgeline.com を追加")

            # 4. 変更をコミット
            await db.commit()
            logger.info("データベースの変更をコミットしました")

            # 5. 最終確認
            logger.info("5. 更新後のデータを確認中...")
            result = await db.execute(
                text("SELECT id, email, username, firebase_uid FROM users ORDER BY id")
            )
            users = result.fetchall()

            logger.info("更新後のuserテーブル:")
            for user in users:
                logger.info(f"  ID {user[0]}: {user[1]} / {user[2]} / {user[3]}")

            logger.info(f"総ユーザー数: {len(users)}")

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            await db.rollback()
            raise


async def main():
    """メイン関数"""
    logger.info("userテーブルのデータ修正処理を開始します")
    await update_user_table_data()
    logger.info("処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
