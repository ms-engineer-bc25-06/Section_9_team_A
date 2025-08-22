from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Analysis(Base):
    """分析結果モデル"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    
    # 分析情報
    analysis_id = Column(String(255), unique=True, index=True, nullable=False)
    analysis_type = Column(String(50), nullable=False)  # sentiment, topic, summary, etc.
    title = Column(String(255), nullable=True)
    
    # 分析結果
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # キーワードリスト（JSON文字列として保存）
    topics = Column(Text, nullable=True)  # トピックリスト（JSON文字列として保存）
    
    # 感情分析
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    sentiment_label = Column(String(50), nullable=True)  # positive, negative, neutral
    
    # 統計情報
    word_count = Column(Integer, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    speaking_time = Column(Float, nullable=True)  # 秒単位
    
    # 処理状態
    status = Column(String(50), default="processing")  # processing, completed, failed
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    
    # 公開制御
    is_public = Column(Boolean, default=False)  # 公開フラグ
    visibility_level = Column(String(50), default="private")  # 可視性レベル
    requires_approval = Column(Boolean, default=True)  # 承認が必要か
    
    # 外部キー
    voice_session_id = Column(Integer, ForeignKey("voice_sessions.id"), nullable=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # リレーションシップ（循環参照を避けるため、back_populatesは使用しない）
    voice_session = relationship("VoiceSession")
    transcription = relationship("Transcription")
    user = relationship("User")
    # feedback_approvals = relationship("FeedbackApproval", back_populates="analysis")

    def __repr__(self):
        return f"<Analysis(id={self.id}, type='{self.analysis_type}', title='{self.title}')>"

    @property
    def is_completed(self) -> bool:
        """分析が完了しているかどうか"""
        return self.status == "completed" and self.processed_at is not None

    @property
    def is_processing(self) -> bool:
        """分析が処理中かどうか"""
        return self.status == "processing"

    @property
    def is_failed(self) -> bool:
        """分析が失敗しているかどうか"""
        return self.status == "failed"

    @property
    def is_approved_for_publication(self) -> bool:
        """公開承認済みかどうか"""
        if not self.requires_approval:
            return True
        return any(approval.is_approved for approval in self.feedback_approvals)

    @property
    def current_visibility_level(self) -> str:
        """現在の可視性レベルを取得"""
        if not self.is_approved_for_publication:
            return "private"
        return self.visibility_level

    def mark_as_completed(self, processed_at: datetime = None):
        """分析を完了としてマーク"""
        self.status = "completed"
        self.processed_at = processed_at or datetime.utcnow()

    def mark_as_failed(self):
        """分析を失敗としてマーク"""
        self.status = "failed"

    def update_sentiment(self, score: float, label: str):
        """感情分析結果を更新"""
        self.sentiment_score = score
        self.sentiment_label = label
        self.updated_at = datetime.utcnow()

    def update_statistics(self, word_count: int = None, sentence_count: int = None, speaking_time: float = None):
        """統計情報を更新"""
        if word_count is not None:
            self.word_count = word_count
        if sentence_count is not None:
            self.sentence_count = sentence_count
        if speaking_time is not None:
            self.speaking_time = speaking_time
        self.updated_at = datetime.utcnow()

    def get_sentiment_category(self) -> str:
        """感情スコアから感情カテゴリを取得"""
        if self.sentiment_score is None:
            return "unknown"
        elif self.sentiment_score >= 0.1:
            return "positive"
        elif self.sentiment_score <= -0.1:
            return "negative"
        else:
            return "neutral"

    def set_visibility(self, level: str, requires_approval: bool = True):
        """可視性レベルを設定"""
        self.visibility_level = level
        self.requires_approval = requires_approval
        self.updated_at = datetime.utcnow()

    def make_public(self):
        """公開設定にする"""
        self.is_public = True
        self.visibility_level = "public"
        self.updated_at = datetime.utcnow()

    def make_private(self):
        """非公開設定にする"""
        self.is_public = False
        self.visibility_level = "private"
        self.updated_at = datetime.utcnow()
