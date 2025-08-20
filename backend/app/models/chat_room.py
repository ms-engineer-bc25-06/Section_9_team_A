from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class ChatRoom(Base):
    """雑談ルームモデル"""

    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)

    # ルーム情報
    room_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # ルーム設定
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)

    # ルーム状態
    status = Column(String(50), default="waiting")  # waiting, active, ended
    room_type = Column(String(50), default="casual")  # casual, business, study

    # 参加者情報
    participants = Column(JSON, nullable=True)  # 参加者リスト
    moderators = Column(JSON, nullable=True)  # モデレーターリスト

    # ルーム統計
    total_messages = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)  # 秒単位

    # 外部キー
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # リレーションシップ
    messages = relationship(
        "ChatMessage", back_populates="chat_room", cascade="all, delete-orphan"
    )
    participants_rel = relationship("ChatRoomParticipant", back_populates="chat_room")
    creator = relationship("User", back_populates="created_chat_rooms", foreign_keys=[created_by])
    team = relationship("Team", back_populates="chat_rooms")

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}', room_id='{self.room_id}')>"

    @property
    def is_active_room(self) -> bool:
        """ルームがアクティブかどうか"""
        return self.status == "active" and self.is_active

    @property
    def is_full(self) -> bool:
        """ルームが満員かどうか"""
        return self.current_participants >= self.max_participants

    def start_room(self):
        """ルームを開始"""
        self.status = "active"
        self.started_at = datetime.utcnow()

    def end_room(self):
        """ルームを終了"""
        self.status = "ended"
        self.ended_at = datetime.utcnow()

    def add_participant(self):
        """参加者を追加"""
        if not self.is_full:
            self.current_participants += 1

    def remove_participant(self):
        """参加者を削除"""
        if self.current_participants > 0:
            self.current_participants -= 1


class ChatMessage(Base):
    """チャットメッセージモデル"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    # メッセージ情報
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, audio, image, system

    # 音声関連（音声メッセージの場合）
    audio_file_path = Column(String(500), nullable=True)
    audio_duration = Column(Integer, nullable=True)  # 秒単位
    transcription = Column(Text, nullable=True)

    # メッセージ状態
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # 外部キー
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="chat_messages", foreign_keys=[sender_id])

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, content='{self.content[:50]}...')>"

    @property
    def is_audio_message(self) -> bool:
        """音声メッセージかどうか"""
        return self.message_type == "audio" and self.audio_file_path is not None

    @property
    def is_system_message(self) -> bool:
        """システムメッセージかどうか"""
        return self.message_type == "system"

    def mark_as_edited(self):
        """編集済みとしてマーク"""
        self.is_edited = True
        self.updated_at = datetime.utcnow()

    def mark_as_deleted(self):
        """削除済みとしてマーク"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()


class ChatRoomParticipant(Base):
    """チャットルーム参加者モデル"""

    __tablename__ = "chat_room_participants"

    id = Column(Integer, primary_key=True, index=True)

    # 参加者情報
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 参加者状態
    role = Column(String(50), default="participant")  # participant, moderator, admin
    status = Column(String(50), default="active")  # active, muted, banned
    is_online = Column(Boolean, default=False)

    # 参加統計
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    total_messages = Column(Integer, default=0)

    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    chat_room = relationship("ChatRoom", back_populates="participants_rel")
    user = relationship("User", back_populates="chat_room_participations", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ChatRoomParticipant(room_id={self.chat_room_id}, user_id={self.user_id})>"

    @property
    def is_moderator(self) -> bool:
        """モデレーターかどうか"""
        return self.role in ["moderator", "admin"]

    @property
    def is_admin(self) -> bool:
        """管理者かどうか"""
        return self.role == "admin"

    @property
    def is_muted(self) -> bool:
        """ミュートされているかどうか"""
        return self.status == "muted"

    @property
    def is_banned(self) -> bool:
        """BANされているかどうか"""
        return self.status == "banned"

    def update_last_active(self):
        """最終アクティブ時間を更新"""
        self.last_active_at = datetime.utcnow()

    def increment_message_count(self):
        """メッセージ数を増加"""
        self.total_messages += 1

    def set_role(self, new_role: str):
        """役割を設定"""
        if new_role in ["participant", "moderator", "admin"]:
            self.role = new_role

    def set_status(self, new_status: str):
        """ステータスを設定"""
        if new_status in ["active", "muted", "banned"]:
            self.status = new_status
