"""
参加者管理サービスのテスト
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.services.participant_management_service import (
    participant_management_service,
    ParticipantRole,
    ParticipantStatus
)
from app.models.user import User
from app.models.voice_session import VoiceSession


class TestParticipantManagementService:
    """参加者管理サービスのテスト"""

    @pytest.fixture
    def sample_user(self):
        """サンプルユーザー"""
        return User(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="テストユーザー",
            is_active=True,
        )

    @pytest.fixture
    def sample_session(self):
        """サンプルセッション"""
        return VoiceSession(
            id=1,
            session_id="test-session-123",
            title="テストセッション",
            user_id=1,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.mark.asyncio
    async def test_join_session(self, sample_user, sample_session):
        """セッション参加のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # セッションに参加
        participant = await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # 検証
        assert participant is not None
        assert participant.user_id == sample_user.id
        assert participant.role == ParticipantRole.PARTICIPANT
        assert participant.status == ParticipantStatus.CONNECTED

    @pytest.mark.asyncio
    async def test_leave_session(self, sample_user, sample_session):
        """セッション退出のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # まずセッションに参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # セッションから退出
        result = await service.leave_session(
            session_id=sample_session.session_id,
            user_id=sample_user.id
        )
        
        # 検証
        assert result is True

    @pytest.mark.asyncio
    async def test_change_participant_role(self, sample_user, sample_session):
        """参加者ロール変更のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # まずセッションにホストとして参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.HOST
        )
        
        # 別のユーザーを作成して参加者として追加
        other_user = User(
            id=2,
            email="other@example.com",
            username="otheruser",
            full_name="他のユーザー",
            is_active=True,
        )
        await service.join_session(
            session_id=sample_session.session_id,
            user=other_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # ホスト権限でロールを変更
        participant = await service.change_participant_role(
            session_id=sample_session.session_id,
            user_id=other_user.id,
            new_role=ParticipantRole.MODERATOR,
            changed_by=sample_user.id
        )
        
        # 検証
        assert participant is not None
        assert participant.role == ParticipantRole.MODERATOR

    @pytest.mark.asyncio
    async def test_get_session_participants(self, sample_user, sample_session):
        """セッション参加者取得のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # セッションに参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # 参加者一覧を取得
        participants = await service.get_session_participants(
            session_id=sample_session.session_id
        )
        
        # 検証
        assert len(participants) > 0
        assert any(p.user_id == sample_user.id for p in participants)

    @pytest.mark.asyncio
    async def test_get_participant_info(self, sample_user, sample_session):
        """参加者情報取得のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # セッションに参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # 参加者情報を取得
        participant = await service.get_participant_info(
            session_id=sample_session.session_id,
            user_id=sample_user.id
        )
        
        # 検証
        assert participant is not None
        assert participant.user_id == sample_user.id

    @pytest.mark.asyncio
    async def test_update_participant_status(self, sample_user, sample_session):
        """参加者ステータス更新のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # まずセッションにホストとして参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.HOST
        )
        
        # 別のユーザーを作成して参加者として追加
        other_user = User(
            id=2,
            email="other@example.com",
            username="otheruser",
            full_name="他のユーザー",
            is_active=True,
        )
        await service.join_session(
            session_id=sample_session.session_id,
            user=other_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # ホスト権限でステータスを更新
        participant = await service.update_participant_status(
            session_id=sample_session.session_id,
            user_id=other_user.id,
            status=ParticipantStatus.MUTED,
            updated_by=sample_user.id
        )
        
        # 検証
        assert participant is not None
        assert participant.status == ParticipantStatus.MUTED

    @pytest.mark.asyncio
    async def test_mute_participant(self, sample_user, sample_session):
        """参加者ミュートのテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # まずセッションにホストとして参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.HOST
        )
        
        # 別のユーザーを作成して参加者として追加
        other_user = User(
            id=2,
            email="other@example.com",
            username="otheruser",
            full_name="他のユーザー",
            is_active=True,
        )
        await service.join_session(
            session_id=sample_session.session_id,
            user=other_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # ホスト権限で参加者をミュート
        participant = await service.mute_participant(
            session_id=sample_session.session_id,
            user_id=other_user.id,
            muted=True,
            muted_by=sample_user.id
        )
        
        # 検証
        assert participant is not None
        assert participant.is_muted is True

    @pytest.mark.asyncio
    async def test_get_session_stats(self, sample_user, sample_session):
        """セッション統計取得のテスト"""
        # 参加者管理サービスを初期化
        service = participant_management_service
        
        # セッションに参加
        await service.join_session(
            session_id=sample_session.session_id,
            user=sample_user,
            role=ParticipantRole.PARTICIPANT
        )
        
        # セッション統計を取得
        stats = await service.get_session_stats(
            session_id=sample_session.session_id
        )
        
        # 検証
        assert stats is not None
        assert "connected_participants" in stats
        assert "active_participants" in stats
