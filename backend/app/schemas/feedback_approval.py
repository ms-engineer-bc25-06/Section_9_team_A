from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApprovalStatus(str, Enum):
    """承認ステータス"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


class VisibilityLevel(str, Enum):
    """可視性レベル"""
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"


class FeedbackApprovalBase(BaseModel):
    """フィードバック承認の基本スキーマ"""
    analysis_id: int = Field(..., description="分析ID")
    visibility_level: VisibilityLevel = Field(..., description="可視性レベル")
    request_reason: Optional[str] = Field(None, description="申請理由")
    is_staged_publication: bool = Field(False, description="段階的公開フラグ")
    publication_stages: Optional[str] = Field(None, description="公開段階（JSON文字列）")
    requires_confirmation: bool = Field(True, description="本人確認が必要か")


class FeedbackApprovalCreate(FeedbackApprovalBase):
    """フィードバック承認作成用スキーマ"""
    pass


class FeedbackApprovalUpdate(BaseModel):
    """フィードバック承認更新用スキーマ"""
    approval_status: Optional[ApprovalStatus] = Field(None, description="承認ステータス")
    review_notes: Optional[str] = Field(None, description="レビューコメント")
    rejection_reason: Optional[str] = Field(None, description="却下理由")
    visibility_level: Optional[VisibilityLevel] = Field(None, description="可視性レベル")


class FeedbackApprovalResponse(FeedbackApprovalBase):
    """フィードバック承認応答用スキーマ"""
    id: int
    requester_id: int
    reviewer_id: Optional[int]
    approval_status: ApprovalStatus
    current_stage: int
    is_confirmed: bool
    confirmation_date: Optional[datetime]
    requested_at: datetime
    reviewed_at: Optional[datetime]
    published_at: Optional[datetime]
    
    # 関連情報
    requester_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    analysis_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class FeedbackApprovalListResponse(BaseModel):
    """フィードバック承認一覧応答用スキーマ"""
    approvals: List[FeedbackApprovalResponse]
    total_count: int
    page: int
    page_size: int


class FeedbackApprovalFilters(BaseModel):
    """フィードバック承認フィルター用スキーマ"""
    analysis_id: Optional[int] = Field(None, description="分析ID")
    requester_id: Optional[int] = Field(None, description="申請者ID")
    reviewer_id: Optional[int] = Field(None, description="レビュアーID")
    approval_status: Optional[ApprovalStatus] = Field(None, description="承認ステータス")
    visibility_level: Optional[VisibilityLevel] = Field(None, description="可視性レベル")
    is_confirmed: Optional[bool] = Field(None, description="本人確認済みか")


class FeedbackApprovalQueryParams(BaseModel):
    """フィードバック承認クエリパラメータ用スキーマ"""
    page: int = Field(default=1, ge=1, description="ページ番号")
    page_size: int = Field(default=20, ge=1, le=100, description="ページサイズ")
    analysis_id: Optional[int] = Field(None, description="分析ID")
    requester_id: Optional[int] = Field(None, description="申請者ID")
    reviewer_id: Optional[int] = Field(None, description="レビュアーID")
    approval_status: Optional[ApprovalStatus] = Field(None, description="承認ステータス")
    visibility_level: Optional[VisibilityLevel] = Field(None, description="可視性レベル")
    is_confirmed: Optional[bool] = Field(None, description="本人確認済みか")


class ApprovalRequest(BaseModel):
    """承認リクエスト用スキーマ"""
    analysis_id: int = Field(..., description="分析ID")
    visibility_level: VisibilityLevel = Field(..., description="可視性レベル")
    request_reason: Optional[str] = Field(None, description="申請理由")
    is_staged_publication: bool = Field(False, description="段階的公開フラグ")
    publication_stages: Optional[List[Dict[str, Any]]] = Field(None, description="公開段階の詳細")


class ApprovalResponse(BaseModel):
    """承認レスポンス用スキーマ"""
    approval_status: ApprovalStatus
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class UserConfirmationRequest(BaseModel):
    """本人確認リクエスト用スキーマ"""
    approval_id: int = Field(..., description="承認ID")
    confirm: bool = Field(..., description="確認フラグ")
    confirmation_notes: Optional[str] = Field(None, description="確認コメント")


class PublicationStage(BaseModel):
    """公開段階の詳細スキーマ"""
    stage_number: int = Field(..., description="段階番号")
    visibility_level: VisibilityLevel = Field(..., description="可視性レベル")
    description: str = Field(..., description="段階の説明")
    delay_days: int = Field(0, description="前段階からの遅延日数")
    auto_advance: bool = Field(False, description="自動進行フラグ")


class StagedPublicationRequest(BaseModel):
    """段階的公開リクエスト用スキーマ"""
    analysis_id: int = Field(..., description="分析ID")
    stages: List[PublicationStage] = Field(..., description="公開段階のリスト")
    request_reason: Optional[str] = Field(None, description="申請理由")


class FeedbackApprovalStats(BaseModel):
    """フィードバック承認統計用スキーマ"""
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    under_review_approvals: int
    requires_changes_approvals: int
    average_approval_time_hours: float
    approval_rate: float  # 承認率（0.0-1.0）
    visibility_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
