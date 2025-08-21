#!/usr/bin/env python3
"""
参加者管理機能のテストスクリプト
"""

import asyncio
import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.services.participant_management_service import participant_management_service
from app.models.user import User
from app.models.voice_session import VoiceSession
from app.models.team import Team
from app.services.participant_management_service import (
    ParticipantRole,
    ParticipantStatus,
)


async def test_participant_management():
    """参加者管理機能のテスト"""
    print("=== 参加者管理機能テスト開始 ===")

    # データベース接続
    from app.core.database import AsyncSessionLocal

    db = None

    try:
        db = AsyncSessionLocal()
        await db.begin()

        # テスト用のユーザーを作成
        test_users = []
        for i in range(3):
            user = User(
                email=f"test_user_{i}@example.com",
                username=f"test_user_{i}",
                full_name=f"テストユーザー{i}",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            test_users.append(user)
            print(f"テストユーザー作成: {user.username}")

        # テスト用のチームを作成
        team = Team(
            name="テストチーム",
            description="参加者管理テスト用チーム",
            owner_id=test_users[0].id,
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        print(f"テストチーム作成: {team.name}")

        # テスト用の音声セッションを作成
        session = VoiceSession(
            name="テストセッション",
            description="参加者管理テスト用セッション",
            team_id=team.id,
            created_by=test_users[0].id,
            status="active",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"テストセッション作成: {session.name}")

        # 参加者管理サービスのテスト
        print("\n--- 参加者管理テスト ---")

        # 1. セッション参加テスト
        print("\n1. セッション参加テスト")
        for i, user in enumerate(test_users):
            role = ParticipantRole.HOST if i == 0 else ParticipantRole.PARTICIPANT
            participant = await participant_management_service.join_session(
                session.id, user, role
            )
            print(f"  ユーザー {user.username} が {role.value} として参加")
            print(f"    参加時刻: {participant.joined_at}")
            print(f"    権限: {participant.permissions}")

        # 2. 参加者リスト取得テスト
        print("\n2. 参加者リスト取得テスト")
        participants = await participant_management_service.get_session_participants(
            session.id
        )
        print(f"  参加者数: {len(participants)}")
        for p in participants:
            print(f"    {p.user.username} - {p.role.value} - {p.status.value}")

        # 3. 参加者状態更新テスト
        print("\n3. 参加者状態更新テスト")
        user_to_update = test_users[1]
        await participant_management_service.update_participant_status(
            session.id, user_to_update.id, ParticipantStatus.MUTED, test_users[0].id
        )
        print(f"  ユーザー {user_to_update.username} をミュート状態に更新")

        # 4. 音声レベル更新テスト
        print("\n4. 音声レベル更新テスト")
        await participant_management_service.update_audio_level(
            session.id, user_to_update.id, 0.75
        )
        print(f"  ユーザー {user_to_update.username} の音声レベルを0.75に更新")

        # 5. 参加者役割変更テスト
        print("\n5. 参加者役割変更テスト")
        await participant_management_service.change_participant_role(
            session.id, user_to_update.id, ParticipantRole.MODERATOR, test_users[0].id
        )
        print(f"  ユーザー {user_to_update.username} の役割をモデレーターに変更")

        # 6. 更新後の参加者リスト確認
        print("\n6. 更新後の参加者リスト確認")
        updated_participants = (
            await participant_management_service.get_session_participants(session.id)
        )
        for p in updated_participants:
            print(f"    {p.user.username} - {p.role.value} - {p.status.value}")
            if p.user.id == user_to_update.id:
                print(f"      音声レベル: {p.audio_level}")
                print(f"      権限: {p.permissions}")

        # 7. 参加者退出テスト
        print("\n7. 参加者退出テスト")
        await participant_management_service.leave_session(
            session.id, user_to_update.id
        )
        print(f"  ユーザー {user_to_update.username} がセッションから退出")

        # 8. 最終参加者リスト確認
        print("\n8. 最終参加者リスト確認")
        final_participants = (
            await participant_management_service.get_session_participants(session.id)
        )
        print(f"  最終参加者数: {len(final_participants)}")
        for p in final_participants:
            print(f"    {p.user.username} - {p.role.value} - {p.status.value}")

        # 9. セッション統計情報テスト
        print("\n9. セッション統計情報テスト")
        stats = await participant_management_service.get_session_stats(session.id)
        print(f"  総参加者数: {stats.get('total_participants', 0)}")
        print(f"  現在の参加者数: {stats.get('connected_participants', 0)}")
        print(f"  発話中参加者数: {stats.get('speaking_participants', 0)}")
        print(f"  総発話時間: {stats.get('total_speak_time', 0):.2f}秒")

        print("\n=== 参加者管理機能テスト完了 ===")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if db is not None:
            await db.close()


if __name__ == "__main__":
    asyncio.run(test_participant_management())
