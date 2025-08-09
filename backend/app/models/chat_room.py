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
    creator = relationship("User", back_populates="created_chat_rooms")
    team = relationship("Team", back_populates="chat_rooms")
    messages = relationship(
        "ChatMessage", back_populates="chat_room", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}', room_id='{self.room_id}')>"


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

    # リレーションシップ
    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, content='{self.content[:50]}...')>"


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

    # リレーションシップ
    chat_room = relationship("ChatRoom")
    user = relationship("User", back_populates="chat_room_participations")

    def __repr__(self):
        return f"<ChatRoomParticipant(room_id={self.chat_room_id}, user_id={self.user_id})>"
