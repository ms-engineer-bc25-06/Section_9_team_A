#!/usr/bin/env python3
"""
リアルタイム通信機能テストスクリプト
参加者管理、メッセージング、セッション制御機能をテストします
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict

from app.services.participant_management_service import (
    ParticipantManagementService,
    ParticipantRole,
    ParticipantStatus,
)
from app.services.messaging_service import (
    MessagingService,
    MessageType,
    MessagePriority,
)
from app.services.audio_processing_service import AudioProcessingService


async def test_participant_management():
    """参加者管理機能のテスト"""
    print("👥 参加者管理機能テストを開始します")
    print("=" * 50)

    # 参加者管理サービスを初期化
    participant_manager = ParticipantManagementService()

    # テスト用セッションID
    session_id = "test-realtime-session"

    try:
        # 1. 参加者追加テスト
        print("📊 1. 参加者追加テスト")

        # モックユーザーを作成
        class MockUser:
            def __init__(self, user_id: int, display_name: str):
                self.id = user_id
                self.display_name = display_name
                self.avatar_url = f"https://example.com/avatar/{user_id}.jpg"

        users = [
            MockUser(1, "Alice (Host)"),
            MockUser(2, "Bob (Participant)"),
            MockUser(3, "Charlie (Guest)"),
            MockUser(4, "David (Observer)"),
        ]

        # 参加者を追加
        for i, user in enumerate(users):
            role = ParticipantRole.HOST if i == 0 else ParticipantRole.PARTICIPANT
            participant = await participant_manager.add_participant(
                session_id, user, role
            )
            print(f"   ✅ 参加者追加: {user.display_name} ({role.value})")

        # 2. 参加者一覧取得テスト
        print("\n📊 2. 参加者一覧取得テスト")

        participants = await participant_manager.get_session_participants(session_id)
        print(f"   📈 参加者数: {len(participants)}")

        for p in participants:
            print(f"      👤 {p.user.display_name}: {p.role.value}, {p.status.value}")

        # 3. 参加者状態更新テスト
        print("\n📊 3. 参加者状態更新テスト")

        # ユーザー2をミュート
        await participant_manager.mute_participant(session_id, 2, 1, True)
        print("   🔇 ユーザー2をミュートしました")

        # ユーザー3のロールを変更
        await participant_manager.change_participant_role(
            session_id, 3, ParticipantRole.GUEST, 1
        )
        print("   🔄 ユーザー3のロールをGUESTに変更しました")

        # 状態を確認
        updated_participants = await participant_manager.get_session_participants(
            session_id
        )
        for p in updated_participants:
            if p.user_id == 2:
                print(f"      🔇 ユーザー2: ミュート={p.is_muted}")
            elif p.user_id == 3:
                print(f"      🔄 ユーザー3: ロール={p.role.value}")

        # 4. 権限チェックテスト
        print("\n📊 4. 権限チェックテスト")

        # ホストの権限チェック
        can_manage = await participant_manager.check_permission(
            session_id, 1, "manage_session"
        )
        print(f"   👑 ホストの管理権限: {can_manage}")

        # 参加者の権限チェック
        can_send_audio = await participant_manager.check_permission(
            session_id, 2, "send_audio"
        )
        print(f"   🎤 参加者の音声送信権限: {can_send_audio}")

        # 5. 参加者統計テスト
        print("\n📊 5. 参加者統計テスト")

        for user_id in [1, 2, 3]:
            stats = await participant_manager.get_participant_stats(session_id, user_id)
            activity = await participant_manager.get_participant_activity(
                session_id, user_id, 5
            )

            print(f"   📊 ユーザー{user_id}の統計:")
            print(f"      - 統計: {stats}")
            print(f"      - 最近の活動: {len(activity)}件")

        # 6. 参加者削除テスト
        print("\n📊 6. 参加者削除テスト")

        await participant_manager.remove_participant(session_id, 4, "left")
        print("   👋 ユーザー4を削除しました")

        remaining_participants = await participant_manager.get_session_participants(
            session_id
        )
        print(f"   📈 残り参加者数: {len(remaining_participants)}")

        print("\n✅ 参加者管理機能テスト完了")

    except Exception as e:
        print(f"\n❌ 参加者管理テストエラー: {e}")
        raise


async def test_messaging_system():
    """メッセージングシステムのテスト"""
    print("\n💬 メッセージングシステムテストを開始します")
    print("=" * 50)

    # メッセージングサービスを初期化
    messaging_service = MessagingService()

    # テスト用セッションID
    session_id = "test-messaging-session"

    try:
        # 1. テキストメッセージ送信テスト
        print("📊 1. テキストメッセージ送信テスト")

        messages = [
            ("Hello, everyone!", MessagePriority.NORMAL),
            ("This is an important message!", MessagePriority.HIGH),
            ("Just a quick note.", MessagePriority.LOW),
        ]

        for content, priority in messages:
            message = await messaging_service.send_text_message(
                session_id, 1, content, priority
            )
            print(f"   📤 メッセージ送信: {message.id} (優先度: {priority.value})")

        # 2. システムメッセージ送信テスト
        print("\n📊 2. システムメッセージ送信テスト")

        system_messages = [
            "Session started",
            "Recording enabled",
            "New participant joined",
        ]

        for content in system_messages:
            message = await messaging_service.send_system_message(session_id, content)
            print(f"   🔧 システムメッセージ: {message.id}")

        # 3. 絵文字リアクションテスト
        print("\n📊 3. 絵文字リアクションテスト")

        emoji_reactions = ["👍", "❤️", "🎉", "🤔"]
        target_message_id = f"{session_id}_1"  # 最初のメッセージ

        for emoji in emoji_reactions:
            message = await messaging_service.send_emoji_reaction(
                session_id, 2, target_message_id, emoji
            )
            print(f"   😊 リアクション送信: {emoji}")

        # 4. メッセージ編集テスト
        print("\n📊 4. メッセージ編集テスト")

        message_id = f"{session_id}_1"
        new_content = "Hello, everyone! (edited)"

        edited_message = await messaging_service.edit_message(
            session_id, message_id, 1, new_content
        )
        print(f"   ✏️ メッセージ編集: {message_id}")

        # 5. メッセージ検索テスト
        print("\n📊 5. メッセージ検索テスト")

        search_results = await messaging_service.search_messages(
            session_id, "important", 10
        )
        print(f"   🔍 検索結果: {len(search_results)}件")

        for msg in search_results:
            print(f"      - {msg.content}")

        # 6. メッセージ履歴取得テスト
        print("\n📊 6. メッセージ履歴取得テスト")

        messages = await messaging_service.get_session_messages(session_id, 20, 0)
        print(f"   📚 メッセージ履歴: {len(messages)}件")

        for msg in messages[-5:]:  # 最新5件
            print(f"      - [{msg.message_type.value}] {msg.content}")

        # 7. メッセージ削除テスト
        print("\n📊 7. メッセージ削除テスト")

        message_to_delete = f"{session_id}_2"
        await messaging_service.delete_message(session_id, message_to_delete, 1)
        print(f"   🗑️ メッセージ削除: {message_to_delete}")

        print("\n✅ メッセージングシステムテスト完了")

    except Exception as e:
        print(f"\n❌ メッセージングテストエラー: {e}")
        raise


async def test_session_control():
    """セッション制御機能のテスト"""
    print("\n🎛️ セッション制御機能テストを開始します")
    print("=" * 50)

    # 各サービスを初期化
    participant_manager = ParticipantManagementService()
    messaging_service = MessagingService()
    audio_processor = AudioProcessingService()

    # テスト用セッションID
    session_id = "test-session-control"

    try:
        # 1. セッション参加者設定
        print("📊 1. セッション参加者設定")

        class MockUser:
            def __init__(self, user_id: int, display_name: str):
                self.id = user_id
                self.display_name = display_name
                self.avatar_url = f"https://example.com/avatar/{user_id}.jpg"

        # ホストと参加者を追加
        host = MockUser(1, "Session Host")
        participant = MockUser(2, "Session Participant")

        await participant_manager.add_participant(
            session_id, host, ParticipantRole.HOST
        )
        await participant_manager.add_participant(
            session_id, participant, ParticipantRole.PARTICIPANT
        )

        print("   ✅ ホストと参加者を追加しました")

        # 2. 権限チェックテスト
        print("\n📊 2. 権限チェックテスト")

        # ホストの権限
        host_permissions = [
            "manage_session",
            "manage_participants",
            "record_audio",
            "mute_others",
        ]

        for permission in host_permissions:
            has_permission = await participant_manager.check_permission(
                session_id, 1, permission
            )
            print(f"   👑 ホストの{permission}権限: {has_permission}")

        # 参加者の権限
        participant_permissions = ["send_audio", "send_messages", "view_participants"]

        for permission in participant_permissions:
            has_permission = await participant_manager.check_permission(
                session_id, 2, permission
            )
            print(f"   👤 参加者の{permission}権限: {has_permission}")

        # 3. システムメッセージ送信テスト
        print("\n📊 3. システムメッセージ送信テスト")

        system_messages = [
            ("Session control started", "high"),
            ("Recording enabled", "normal"),
            ("Participant muted", "normal"),
        ]

        for content, priority in system_messages:
            priority_enum = MessagePriority(priority)
            message = await messaging_service.send_system_message(
                session_id, content, priority_enum
            )
            print(f"   🔧 システムメッセージ: {content} (優先度: {priority})")

        # 4. 参加者制御テスト
        print("\n📊 4. 参加者制御テスト")

        # 参加者をミュート
        await participant_manager.mute_participant(session_id, 2, 1, True)
        print("   🔇 参加者をミュートしました")

        # 参加者の状態を確認
        participant = await participant_manager.get_participant(session_id, 2)
        if participant:
            print(
                f"   📊 参加者状態: {participant.status.value}, ミュート: {participant.is_muted}"
            )

        # 5. 音声レベル監視テスト
        print("\n📊 5. 音声レベル監視テスト")

        # 録音を開始
        await audio_processor.start_recording(session_id)
        print("   🎙️ 録音を開始しました")

        # 音声レベルを取得
        audio_levels = await audio_processor.get_session_participants_audio_levels(
            session_id
        )
        print(f"   📈 音声レベル監視: {len(audio_levels)}参加者")

        # 6. セッション状態統合テスト
        print("\n📊 6. セッション状態統合テスト")

        # 参加者一覧
        participants = await participant_manager.get_session_participants(session_id)
        print(f"   👥 参加者数: {len(participants)}")

        # メッセージ履歴
        messages = await messaging_service.get_session_messages(session_id, 10, 0)
        print(f"   💬 メッセージ数: {len(messages)}")

        # 録音状態
        is_recording = session_id in audio_processor.recording_sessions
        print(f"   🎙️ 録音状態: {is_recording}")

        # 7. クリーンアップ
        print("\n📊 7. クリーンアップ")

        # 録音を停止
        await audio_processor.stop_recording(session_id)
        print("   🛑 録音を停止しました")

        # 参加者を削除
        await participant_manager.remove_participant(session_id, 1, "test_complete")
        await participant_manager.remove_participant(session_id, 2, "test_complete")
        print("   🧹 参加者を削除しました")

        print("\n✅ セッション制御機能テスト完了")

    except Exception as e:
        print(f"\n❌ セッション制御テストエラー: {e}")
        raise


async def test_integration():
    """統合テスト"""
    print("\n🔗 統合テストを開始します")
    print("=" * 50)

    try:
        # 各機能を順次テスト
        await test_participant_management()
        await test_messaging_system()
        await test_session_control()

        print("\n🎉 全ての統合テストが完了しました")

    except Exception as e:
        print(f"\n❌ 統合テストエラー: {e}")
        raise


if __name__ == "__main__":
    print("🚀 リアルタイム通信機能テストを開始します")

    # 統合テストを実行
    asyncio.run(test_integration())

    print("\n🎉 全てのテストが完了しました")
