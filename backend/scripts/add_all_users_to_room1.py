#!/usr/bin/env python3
"""
全ユーザーをroom-1に参加者として追加するスクリプト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.voice_session import VoiceSession
from app.models.voice_session_participant import VoiceSessionParticipant
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


async def add_all_users_to_room1():
    """全ユーザーをroom-1に参加者として追加"""
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

            # 既存の参加者を確認
            existing_participants = set()
            for participant in voice_session.participants:
                existing_participants.add(participant.user_id)

            logger.info(f"既存の参加者数: {len(existing_participants)}")

            # 新しく追加する参加者を作成
            new_participants = []
            for user in users:
                if user.id not in existing_participants:
                    # ホストユーザーは既に参加者として登録されているはず
                    if user.id == voice_session.user_id:
                        role = "host"
                    else:
                        role = "participant"

                    participant = VoiceSessionParticipant(
                        voice_session_id=voice_session.id, user_id=user.id, role=role
                    )
                    new_participants.append(participant)
                    logger.info(
                        f"参加者を追加: {user.email} (ID: {user.id}, 役割: {role})"
                    )

            # データベースに追加
            if new_participants:
                db.add_all(new_participants)
                await db.commit()
                logger.info(f"{len(new_participants)}人の参加者を追加しました")
            else:
                logger.info("追加する参加者はいません")

            # 最終確認
            result = await db.execute(
                select(VoiceSessionParticipant).where(
                    VoiceSessionParticipant.voice_session_id == voice_session.id
                )
            )
            all_participants = result.scalars().all()
            logger.info(f"room-1の総参加者数: {len(all_participants)}")

            # 参加者一覧を表示
            for participant in all_participants:
                user_result = await db.execute(
                    select(User).where(User.id == participant.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    logger.info(f"参加者: {user.email} (役割: {participant.role})")

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            await db.rollback()
            raise


async def main():
    """メイン関数"""
    logger.info("全ユーザーをroom-1に追加する処理を開始します")
    await add_all_users_to_room1()
    logger.info("処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())
