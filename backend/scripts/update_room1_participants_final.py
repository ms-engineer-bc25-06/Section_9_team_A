#!/usr/bin/env python3
"""
room-1の参加者リストを更新するスクリプト
現在のユーザーテーブルの状況に合わせて参加者リストを再構築
"""

import asyncio
import json
from datetime import datetime
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def update_room1_participants():
    """room-1の参加者リストを更新"""

    # 現在のユーザーテーブルの状況
    participants_data = [
        {
            "user_id": 1,
            "email": "admin@example.com",
            "username": "管理者",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 2,
            "email": "test-1@example.com",
            "username": "テストユーザー1",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 3,
            "email": "test-2@example.com",
            "username": "テストユーザー2",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 4,
            "email": "test-3@example.com",
            "username": "テストユーザー3",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 5,
            "email": "test-4@example.com",
            "username": "テストユーザー4",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 6,
            "email": "erika@bridgeline.com",
            "username": "ペルソナ：えりか",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 7,
            "email": "uchi@bridgeline.com",
            "username": "ペルソナ：うっちー",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 8,
            "email": "kodai@bridgeline.com",
            "username": "こだい",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 9,
            "email": "rui@bridgeline.com",
            "username": "rui",
            "role": "host",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 10,
            "email": "shizuka@bridgeline.com",
            "username": "しづかさん",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
        {
            "user_id": 11,
            "email": "asuka@bridgeline.com",
            "username": "あっすー",
            "role": "participant",
            "joined_at": "2025-08-24T16:32:05.000000+00:00",
            "is_active": True,
        },
    ]

    async with AsyncSessionLocal() as db:
        try:
            # room-1の参加者リストを更新
            participants_json = json.dumps(participants_data, ensure_ascii=False)
            participant_count = len(participants_data)

            # 参加者リストと参加者数を更新
            update_query = text("""
                UPDATE voice_sessions 
                SET participants = :participants, 
                    participant_count = :participant_count,
                    updated_at = NOW()
                WHERE session_id = 'room-1'
            """)

            result = await db.execute(
                update_query,
                {
                    "participants": participants_json,
                    "participant_count": participant_count,
                },
            )

            await db.commit()

            print(f"✅ room-1の参加者リストを更新しました")
            print(f"   参加者数: {participant_count}人")
            print(f"   ホスト: rui@bridgeline.com (ID: 9)")
            print(f"   参加者: {participant_count - 1}人")

            # 更新結果を確認
            select_query = text("""
                SELECT session_id, title, participant_count, user_id 
                FROM voice_sessions 
                WHERE session_id = 'room-1'
            """)

            result = await db.execute(select_query)
            room_data = result.fetchone()

            if room_data:
                print(f"\n📋 更新後のroom-1情報:")
                print(f"   セッションID: {room_data.session_id}")
                print(f"   タイトル: {room_data.title}")
                print(f"   参加者数: {room_data.participant_count}")
                print(f"   作成者ID: {room_data.user_id}")

        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(update_room1_participants())
