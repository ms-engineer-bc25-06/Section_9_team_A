#!/usr/bin/env python3
"""
新しいユーザーID（1-11）に対応して、room-1の参加者情報を更新するスクリプト
"""

import asyncio
import sys
import os
import json

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from sqlalchemy import text
import structlog

logger = structlog.get_logger()


async def update_room1_participants_new_users():
    """新しいユーザーID（1-11）に対応して、room-1の参加者情報を更新"""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("room-1の参加者情報を新しいユーザーIDに対応して更新します")

            # 1. 現在のuserテーブルの状況を確認
            logger.info("1. 現在のuserテーブルの状況を確認中...")
            result = await db.execute(
                text("SELECT id, email, username, firebase_uid FROM users ORDER BY id")
            )
            users = result.fetchall()

            logger.info(f"現在のユーザー数: {len(users)}")
            for user in users:
                logger.info(f"  ID {user[0]}: {user[1]} / {user[2]} / {user[3]}")

            # 2. room-1セッションの現在の状況を確認
            logger.info("2. room-1セッションの現在の状況を確認中...")
            result = await db.execute(
                text(
                    "SELECT session_id, title, user_id, participant_count, participants FROM voice_sessions WHERE session_id = 'room-1'"
                )
            )
            session_result = result.fetchone()

            if not session_result:
                logger.error("room-1セッションが見つかりません")
                return

            session_id, title, host_user_id, participant_count, participants = (
                session_result
            )
            logger.info(f"room-1セッション: {title}, ホストユーザーID: {host_user_id}")
            logger.info(f"現在の参加者数: {participant_count}")

            # 3. 新しい参加者情報を作成
            logger.info("3. 新しい参加者情報を作成中...")
            participants_data = []

            for user in users:
                participant_info = {
                    "user_id": user[0],
                    "email": user[1],
                    "username": user[2],
                    "role": "host" if user[0] == host_user_id else "participant",
                    "joined_at": "2025-08-24T16:32:05.000000+00:00",  # 更新時刻
                    "is_active": True,
                }
                participants_data.append(participant_info)
                logger.info(
                    f"参加者情報を追加: {user[1]} (ID: {user[0]}, 役割: {participant_info['role']})"
                )

            # 4. participantsフィールドを更新
            participants_json = json.dumps(participants_data, ensure_ascii=False)

            update_query = text("""
                UPDATE voice_sessions 
                SET participants = :participants, participant_count = :count
                WHERE session_id = 'room-1'
            """)

            await db.execute(
                update_query,
                {"participants": participants_json, "count": len(participants_data)},
            )

            # 5. 変更をコミット
            await db.commit()
            logger.info(
                f"room-1の参加者情報を更新しました。総参加者数: {len(participants_data)}"
            )

            # 6. 最終確認
            logger.info("6. 更新後の参加者情報を確認中...")
            result = await db.execute(
                text(
                    "SELECT session_id, title, user_id, participant_count, LEFT(participants, 200) as participants_preview FROM voice_sessions WHERE session_id = 'room-1'"
                )
            )
            final_result = result.fetchone()

            if final_result:
                logger.info(f"更新後のroom-1セッション:")
                logger.info(f"  セッションID: {final_result[0]}")
                logger.info(f"  タイトル: {final_result[1]}")
                logger.info(f"  ホストユーザーID: {final_result[2]}")
                logger.info(f"  参加者数: {final_result[3]}")
                logger.info(f"  参加者情報プレビュー: {final_result[4][:100]}...")

            logger.info("更新完了！")

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            await db.rollback()
            raise


async def main():
    """メイン関数"""
    logger.info(
        "room-1の参加者情報を新しいユーザーIDに対応して更新する処理を開始します"
    )
    await update_room1_participants_new_users()
    logger.info("処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
