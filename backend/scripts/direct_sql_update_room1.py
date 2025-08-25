#!/usr/bin/env python3
"""
直接SQLを使用してroom-1のparticipantsフィールドを更新するスクリプト
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


async def update_room1_participants_direct():
    """直接SQLを使用してroom-1のparticipantsフィールドを更新"""
    async with AsyncSessionLocal() as db:
        try:
            # 全ユーザーを取得
            result = await db.execute(
                text("SELECT id, email, username FROM users ORDER BY id")
            )
            users = result.fetchall()

            logger.info(f"全ユーザー数: {len(users)}")

            # room-1セッションのuser_idを取得
            result = await db.execute(
                text("SELECT user_id FROM voice_sessions WHERE session_id = 'room-1'")
            )
            session_result = result.fetchone()

            if not session_result:
                logger.error("room-1セッションが見つかりません")
                return

            host_user_id = session_result[0]
            logger.info(f"room-1セッションのホストユーザーID: {host_user_id}")

            # 参加者情報を作成
            participants_data = []
            for user in users:
                participant_info = {
                    "user_id": user[0],
                    "email": user[1],
                    "username": user[2],
                    "role": "host" if user[0] == host_user_id else "participant",
                    "joined_at": "2025-08-24T15:52:42.441074+00:00",
                    "is_active": True,
                }
                participants_data.append(participant_info)
                logger.info(
                    f"参加者情報を追加: {user[1]} (ID: {user[0]}, 役割: {participant_info['role']})"
                )

            # participantsフィールドを更新
            participants_json = json.dumps(participants_data, ensure_ascii=False)

            # SQLで直接更新
            update_query = text("""
                UPDATE voice_sessions 
                SET participants = :participants, participant_count = :count
                WHERE session_id = 'room-1'
            """)

            await db.execute(
                update_query,
                {"participants": participants_json, "count": len(participants_data)},
            )

            await db.commit()
            logger.info(
                f"room-1の参加者情報を更新しました。総参加者数: {len(participants_data)}"
            )

            # 最終確認
            logger.info("更新後の参加者情報:")
            for participant in participants_data:
                logger.info(f"  - {participant['email']} (役割: {participant['role']})")

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            await db.rollback()
            raise


async def main():
    """メイン関数"""
    logger.info("直接SQLを使用してroom-1の参加者情報を更新する処理を開始します")
    await update_room1_participants_direct()
    logger.info("処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
