import asyncio
import structlog
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from app.models.user import User
from app.models.voice_session import VoiceSession
from app.services.voice_session_service import VoiceSessionService
from app.core.websocket import manager

logger = structlog.get_logger()


class SessionState(str, Enum):
    """セッション状態"""
    PREPARING = "preparing"      # 準備中
    ACTIVE = "active"            # アクティブ
    PAUSED = "paused"           # 一時停止
    RECORDING = "recording"      # 録音中
    TRANSCRIBING = "transcribing"  # 転写中
    ANALYZING = "analyzing"      # 分析中
    COMPLETED = "completed"      # 完了
    CANCELLED = "cancelled"      # キャンセル
    ERROR = "error"              # エラー


class ParticipantState(str, Enum):
    """参加者状態"""
    CONNECTING = "connecting"    # 接続中
    CONNECTED = "connected"      # 接続済み
    SPEAKING = "speaking"        # 発話中
    LISTENING = "listening"      # 聞き取り中
    MUTED = "muted"             # ミュート
    DISCONNECTED = "disconnected"  # 切断


class RecordingState(str, Enum):
    """録音状態"""
    STOPPED = "stopped"          # 停止
    RECORDING = "recording"      # 録音中
    PAUSED = "paused"           # 一時停止
    PROCESSING = "processing"    # 処理中


@dataclass
class SessionParticipant:
    """セッション参加者情報"""
    
    user_id: int
    display_name: str
    state: ParticipantState = ParticipantState.CONNECTING
    connected_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_speaking: bool = False
    is_muted: bool = False
    audio_level: float = 0.0
    connection_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionRecording:
    """セッション録音情報"""
    
    state: RecordingState = RecordingState.STOPPED
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    total_duration: float = 0.0
    file_path: Optional[str] = None
    file_size: int = 0
    quality: str = "high"
    format: str = "wav"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionTranscription:
    """セッション転写情報"""
    
    is_active: bool = False
    started_at: Optional[datetime] = None
    total_chunks: int = 0
    total_duration: float = 0.0
    average_confidence: float = 0.0
    unique_speakers: int = 0
    languages_detected: List[str] = field(default_factory=list)
    last_update: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionAnalytics:
    """セッション分析情報"""
    
    is_active: bool = False
    started_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_phase: str = "preparation"
    completed_steps: List[str] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionStateInfo:
    """セッション状態情報"""
    
    session_id: str
    state: SessionState = SessionState.PREPARING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: float = 0.0
    participants: Dict[int, SessionParticipant] = field(default_factory=dict)
    recording: SessionRecording = field(default_factory=SessionRecording)
    transcription: SessionTranscription = field(default_factory=SessionTranscription)
    analytics: SessionAnalytics = field(default_factory=SessionAnalytics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.now)


class SessionStateManager:
    """セッション状態管理クラス"""
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionStateInfo] = {}
        self.session_history: Dict[str, List[SessionStateInfo]] = {}
        self.state_change_callbacks: Dict[str, List[callable]] = {}
        self.cleanup_interval = 300  # 5分
        self.max_session_duration = 7200  # 2時間
        
    async def create_session(self, session_id: str, host_user: User) -> SessionStateInfo:
        """セッションを作成"""
        try:
            # 既存セッションをチェック
            if session_id in self.active_sessions:
                logger.warning(f"Session {session_id} already exists")
                return self.active_sessions[session_id]
            
            # 新しいセッション状態を作成
            session_state = SessionStateInfo(
                session_id=session_id,
                state=SessionState.PREPARING,
                created_at=datetime.now()
            )
            
            # ホストを参加者として追加
            host_participant = SessionParticipant(
                user_id=host_user.id,
                display_name=host_user.display_name,
                state=ParticipantState.CONNECTING,
                connected_at=datetime.now()
            )
            session_state.participants[host_user.id] = host_participant
            
            # アクティブセッションに追加
            self.active_sessions[session_id] = session_state
            
            # 履歴に追加
            if session_id not in self.session_history:
                self.session_history[session_id] = []
            self.session_history[session_id].append(session_state)
            
            logger.info(f"Created session state for {session_id}")
            return session_state
            
        except Exception as e:
            logger.error(f"Failed to create session state for {session_id}: {e}")
            raise
    
    async def start_session(self, session_id: str, user_id: int) -> SessionStateInfo:
        """セッションを開始"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")
            
            # 状態を更新
            session_state.state = SessionState.ACTIVE
            session_state.started_at = datetime.now()
            session_state.last_update = datetime.now()
            
            # 参加者状態を更新
            if user_id in session_state.participants:
                session_state.participants[user_id].state = ParticipantState.CONNECTED
                session_state.participants[user_id].last_activity = datetime.now()
            
            # コールバックを実行
            await self._execute_state_change_callbacks(session_id, SessionState.ACTIVE)
            
            logger.info(f"Started session {session_id}")
            return session_state
            
        except Exception as e:
            logger.error(f"Failed to start session {session_id}: {e}")
            raise
    
    async def pause_session(self, session_id: str, user_id: int) -> SessionStateInfo:
        """セッションを一時停止"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")
            
            # 状態を更新
            session_state.state = SessionState.PAUSED
            session_state.last_update = datetime.now()
            
            # 録音も一時停止
            if session_state.recording.state == RecordingState.RECORDING:
                session_state.recording.state = RecordingState.PAUSED
                session_state.recording.paused_at = datetime.now()
            
            # コールバックを実行
            await self._execute_state_change_callbacks(session_id, SessionState.PAUSED)
            
            logger.info(f"Paused session {session_id}")
            return session_state
            
        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            raise
    
    async def resume_session(self, session_id: str, user_id: int) -> SessionStateInfo:
        """セッションを再開"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")
            
            # 状態を更新
            session_state.state = SessionState.ACTIVE
            session_state.last_update = datetime.now()
            
            # 録音も再開
            if session_state.recording.state == RecordingState.PAUSED:
                session_state.recording.state = RecordingState.RECORDING
                session_state.recording.paused_at = None
            
            # コールバックを実行
            await self._execute_state_change_callbacks(session_id, SessionState.ACTIVE)
            
            logger.info(f"Resumed session {session_id}")
            return session_state
            
        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            raise
    
    async def end_session(self, session_id: str, user_id: int) -> SessionStateInfo:
        """セッションを終了"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")
            
            # 状態を更新
            session_state.state = SessionState.COMPLETED
            session_state.ended_at = datetime.now()
            session_state.duration = (session_state.ended_at - session_state.started_at).total_seconds() if session_state.started_at else 0.0
            session_state.last_update = datetime.now()
            
            # 録音を停止
            if session_state.recording.state in [RecordingState.RECORDING, RecordingState.PAUSED]:
                session_state.recording.state = RecordingState.STOPPED
            
            # 転写を停止
            if session_state.transcription.is_active:
                session_state.transcription.is_active = False
            
            # 分析を停止
            if session_state.analytics.is_active:
                session_state.analytics.is_active = False
            
            # コールバックを実行
            await self._execute_state_change_callbacks(session_id, SessionState.COMPLETED)
            
            logger.info(f"Ended session {session_id}")
            return session_state
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise
    
    async def add_participant(self, session_id: str, user: User, connection_id: str) -> SessionParticipant:
        """参加者を追加"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                raise ValueError(f"Session {session_id} not found")
            
            # 参加者を作成
            participant = SessionParticipant(
                user_id=user.id,
                display_name=user.display_name,
                state=ParticipantState.CONNECTED,
                connected_at=datetime.now(),
                last_activity=datetime.now(),
                connection_id=connection_id
            )
            
            session_state.participants[user.id] = participant
            session_state.last_update = datetime.now()
            
            logger.info(f"Added participant {user.id} to session {session_id}")
            return participant
            
        except Exception as e:
            logger.error(f"Failed to add participant to session {session_id}: {e}")
            raise
    
    async def remove_participant(self, session_id: str, user_id: int) -> bool:
        """参加者を削除"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            if user_id in session_state.participants:
                participant = session_state.participants[user_id]
                participant.state = ParticipantState.DISCONNECTED
                session_state.last_update = datetime.now()
                
                logger.info(f"Removed participant {user_id} from session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove participant from session {session_id}: {e}")
            return False
    
    async def update_participant_state(self, session_id: str, user_id: int, state: ParticipantState, **kwargs) -> bool:
        """参加者状態を更新"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state or user_id not in session_state.participants:
                return False
            
            participant = session_state.participants[user_id]
            participant.state = state
            participant.last_activity = datetime.now()
            
            # 追加の属性を更新
            for key, value in kwargs.items():
                if hasattr(participant, key):
                    setattr(participant, key, value)
            
            session_state.last_update = datetime.now()
            
            logger.debug(f"Updated participant {user_id} state to {state} in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update participant state in session {session_id}: {e}")
            return False
    
    async def start_recording(self, session_id: str, user_id: int, **kwargs) -> bool:
        """録音を開始"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            session_state.recording.state = RecordingState.RECORDING
            session_state.recording.started_at = datetime.now()
            session_state.recording.paused_at = None
            
            # 追加の属性を設定
            for key, value in kwargs.items():
                if hasattr(session_state.recording, key):
                    setattr(session_state.recording, key, value)
            
            session_state.last_update = datetime.now()
            
            logger.info(f"Started recording for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording for session {session_id}: {e}")
            return False
    
    async def stop_recording(self, session_id: str, user_id: int) -> bool:
        """録音を停止"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            session_state.recording.state = RecordingState.STOPPED
            session_state.last_update = datetime.now()
            
            logger.info(f"Stopped recording for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop recording for session {session_id}: {e}")
            return False
    
    async def start_transcription(self, session_id: str, **kwargs) -> bool:
        """転写を開始"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            session_state.transcription.is_active = True
            session_state.transcription.started_at = datetime.now()
            session_state.transcription.last_update = datetime.now()
            
            # 追加の属性を設定
            for key, value in kwargs.items():
                if hasattr(session_state.transcription, key):
                    setattr(session_state.transcription, key, value)
            
            session_state.last_update = datetime.now()
            
            logger.info(f"Started transcription for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start transcription for session {session_id}: {e}")
            return False
    
    async def update_transcription_stats(self, session_id: str, **kwargs) -> bool:
        """転写統計を更新"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            # 統計を更新
            for key, value in kwargs.items():
                if hasattr(session_state.transcription, key):
                    setattr(session_state.transcription, key, value)
            
            session_state.transcription.last_update = datetime.now()
            session_state.last_update = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update transcription stats for session {session_id}: {e}")
            return False
    
    async def start_analytics(self, session_id: str, **kwargs) -> bool:
        """分析を開始"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            session_state.analytics.is_active = True
            session_state.analytics.started_at = datetime.now()
            
            # 追加の属性を設定
            for key, value in kwargs.items():
                if hasattr(session_state.analytics, key):
                    setattr(session_state.analytics, key, value)
            
            session_state.last_update = datetime.now()
            
            logger.info(f"Started analytics for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start analytics for session {session_id}: {e}")
            return False
    
    async def update_analytics_progress(self, session_id: str, progress_percentage: float, current_phase: str, **kwargs) -> bool:
        """分析進捗を更新"""
        try:
            session_state = self.active_sessions.get(session_id)
            if not session_state:
                return False
            
            session_state.analytics.progress_percentage = progress_percentage
            session_state.analytics.current_phase = current_phase
            
            # 追加の属性を更新
            for key, value in kwargs.items():
                if hasattr(session_state.analytics, key):
                    setattr(session_state.analytics, key, value)
            
            session_state.last_update = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update analytics progress for session {session_id}: {e}")
            return False
    
    async def get_session_state(self, session_id: str) -> Optional[SessionStateInfo]:
        """セッション状態を取得"""
        return self.active_sessions.get(session_id)
    
    async def get_all_active_sessions(self) -> List[SessionStateInfo]:
        """すべてのアクティブセッションを取得"""
        return list(self.active_sessions.values())
    
    async def get_session_participants(self, session_id: str) -> List[SessionParticipant]:
        """セッション参加者を取得"""
        session_state = self.active_sessions.get(session_id)
        if not session_state:
            return []
        return list(session_state.participants.values())
    
    async def get_session_history(self, session_id: str) -> List[SessionStateInfo]:
        """セッション履歴を取得"""
        return self.session_history.get(session_id, [])
    
    async def register_state_change_callback(self, session_id: str, callback: callable):
        """状態変更コールバックを登録"""
        if session_id not in self.state_change_callbacks:
            self.state_change_callbacks[session_id] = []
        self.state_change_callbacks[session_id].append(callback)
    
    async def _execute_state_change_callbacks(self, session_id: str, new_state: SessionState):
        """状態変更コールバックを実行"""
        try:
            callbacks = self.state_change_callbacks.get(session_id, [])
            for callback in callbacks:
                try:
                    await callback(session_id, new_state)
                except Exception as e:
                    logger.error(f"Error executing state change callback: {e}")
        except Exception as e:
            logger.error(f"Error executing state change callbacks: {e}")
    
    async def cleanup_expired_sessions(self):
        """期限切れセッションをクリーンアップ"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session_state in self.active_sessions.items():
                # 最大セッション時間を超えたセッション
                if session_state.started_at and (current_time - session_state.started_at).total_seconds() > self.max_session_duration:
                    expired_sessions.append(session_id)
                    continue
                
                # 長時間アクティブでないセッション
                if session_state.last_update and (current_time - session_state.last_update).total_seconds() > self.cleanup_interval:
                    # 参加者がいないセッション
                    active_participants = [p for p in session_state.participants.values() if p.state != ParticipantState.DISCONNECTED]
                    if not active_participants:
                        expired_sessions.append(session_id)
            
            # 期限切れセッションを削除
            for session_id in expired_sessions:
                await self.end_session(session_id, 0)  # システムによる終了
                logger.info(f"Cleaned up expired session {session_id}")
                
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")


# グローバルインスタンス
session_state_manager = SessionStateManager()
