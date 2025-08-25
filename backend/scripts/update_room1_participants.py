#!/usr/bin/env python3
"""
既存の設計を活用して、room-1のparticipantsフィールドに全ユーザーのIDを含めるスクリプト
"""

import asyncio
import sys
import os
import json

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.voice_session import VoiceSession
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


async def update_room1_participants():
    """room-1のparticipantsフィールドに全ユーザーのIDを含める"""
    async with AsyncSessionLocal() as db:
        try:
            # room-1セッションを取得
            result = await db.execute(
                select(VoiceSession).where(VoiceSession.session_id == "room-1")
            )
            voice_session = result.scalar_one_or_none()

            if not voice_session:
                logger.error("room-1セッションが見つかりません")
                return

            logger.info(f"room-1セッションを取得: ID={voice_session.id}")

            # 全ユーザーを取得
            result = await db.execute(select(User))
            users = result.scalars().all()

            logger.info(f"全ユーザー数: {len(users)}")

            # 参加者情報を作成
            participants_data = []
            for user in users:
                participant_info = {
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": "host"
                    if user.id == voice_session.user_id
                    else "participant",
                    "joined_at": "2025-08-24T15:52:42.441074+00:00",  # セッション作成時刻
                }
                participants_data.append(participant_info)
                logger.info(
                    f"参加者情報を追加: {user.email} (ID: {user.id}, 役割: {participant_info['role']})"
                )

            # participantsフィールドを更新
            voice_session.participants = json.dumps(
                participants_data, ensure_ascii=False
            )
            voice_session.participant_count = len(participants_data)

            # データベースに保存
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
    logger.info("room-1の参加者情報を更新する処理を開始します")
    await update_room1_participants()
    logger.info("処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
