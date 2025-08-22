from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
from typing import Optional
import enum


class ApprovalStatus(str, enum.Enum):
    """承認ステータス"""

    PENDING = "pending"  # 承認待ち
    UNDER_REVIEW = "under_review"  # レビュー中
    APPROVED = "approved"  # 承認済み
    REJECTED = "rejected"  # 却下
    REQUIRES_CHANGES = "requires_changes"  # 修正要求


class VisibilityLevel(str, enum.Enum):
    """可視性レベル"""

    PRIVATE = "private"  # 本人のみ
    TEAM = "team"  # チーム内
    ORGANIZATION = "organization"  # 組織内
    PUBLIC = "public"  # 公開


class FeedbackApproval(Base):
    """フィードバック承認モデル"""

    __tablename__ = "feedback_approvals"

    id = Column(Integer, primary_key=True, index=True)

    # 分析結果との関連
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)

    # 承認者・申請者
    requester_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )  # 申請者
    reviewer_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )  # レビュアー

    # 承認プロセス
    approval_status = Column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False
    )
    visibility_level = Column(
        Enum(VisibilityLevel), default=VisibilityLevel.PRIVATE, nullable=False
    )

    # 申請・承認情報
    request_reason = Column(Text, nullable=True)  # 申請理由
    review_notes = Column(Text, nullable=True)  # レビューコメント
    rejection_reason = Column(Text, nullable=True)  # 却下理由

    # 段階的公開設定
    is_staged_publication = Column(Boolean, default=False)  # 段階的公開フラグ
    publication_stages = Column(Text, nullable=True)  # 公開段階（JSON文字列）
    current_stage = Column(Integer, default=0)  # 現在の公開段階

    # 承認フロー
    requires_confirmation = Column(Boolean, default=True)  # 本人確認が必要か
    is_confirmed = Column(Boolean, default=False)  # 本人確認済みか
    confirmation_date = Column(DateTime(timezone=True), nullable=True)  # 本人確認日時

    # タイムスタンプ
    requested_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)  # レビュー日時
    published_at = Column(DateTime(timezone=True), nullable=True)  # 公開日時

    # リレーションシップ
    analysis = relationship("Analysis", back_populates="feedback_approvals")
    requester = relationship("User", foreign_keys=[requester_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<FeedbackApproval(id={self.id}, analysis_id={self.analysis_id}, status='{self.approval_status}')>"

    @property
    def is_pending(self) -> bool:
        """承認待ちかどうか"""
        return self.approval_status == ApprovalStatus.PENDING

    @property
    def is_approved(self) -> bool:
        """承認済みかどうか"""
        return self.approval_status == ApprovalStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        """却下されているかどうか"""
        return self.approval_status == ApprovalStatus.REJECTED

    @property
    def can_be_published(self) -> bool:
        """公開可能かどうか"""
        return (
            self.is_approved
            and self.is_confirmed
            and self.visibility_level != VisibilityLevel.PRIVATE
        )

    def request_approval(
        self,
        requester_id: int,
        visibility_level: VisibilityLevel,
        request_reason: Optional[str] = None,
        is_staged: bool = False,
    ):
        """承認をリクエスト"""
        self.requester_id = requester_id
        self.visibility_level = visibility_level
        self.request_reason = request_reason
        self.is_staged_publication = is_staged
        self.approval_status = ApprovalStatus.PENDING
        self.requested_at = datetime.utcnow()

    def start_review(self, reviewer_id: int):
        """レビュー開始"""
        self.reviewer_id = reviewer_id
        self.approval_status = ApprovalStatus.UNDER_REVIEW

    def approve(self, review_notes: Optional[str] = None):
        """承認"""
        self.approval_status = ApprovalStatus.APPROVED
        self.review_notes = review_notes
        self.reviewed_at = datetime.utcnow()

    def reject(self, rejection_reason: str):
        """却下"""
        self.approval_status = ApprovalStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.reviewed_at = datetime.utcnow()

    def request_changes(self, review_notes: str):
        """修正要求"""
        self.approval_status = ApprovalStatus.REQUIRES_CHANGES
        self.review_notes = review_notes
        self.reviewed_at = datetime.utcnow()

    def confirm_by_user(self):
        """本人確認"""
        self.is_confirmed = True
        self.confirmation_date = datetime.utcnow()

    def publish(self):
        """公開"""
        if self.can_be_published:
            self.published_at = datetime.utcnow()

    def advance_stage(self):
        """次の公開段階に進む"""
        if self.is_staged_publication and self.current_stage < self._get_total_stages():
            self.current_stage += 1

    def _get_total_stages(self) -> int:
        """総公開段階数を取得"""
        if not self.publication_stages:
            return 1
        try:
            import json

            stages = json.loads(self.publication_stages)
            return len(stages)
        except:
            return 1


# 循環参照を避けるための遅延インポート
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.analysis import Analysis
