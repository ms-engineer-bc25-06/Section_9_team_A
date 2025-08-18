from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """監査ログ基本スキーマ"""
    action: str = Field(..., description="アクション（create, update, delete, login等）")
    resource_type: str = Field(..., description="リソースタイプ（user, team, voice_session等）")
    resource_id: Optional[str] = Field(None, description="リソースID")
    description: Optional[str] = Field(None, description="詳細説明")
    details: Optional[Dict[str, Any]] = Field(None, description="追加詳細情報")
    session_id: Optional[str] = Field(None, description="セッションID")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")


class AuditLogCreate(AuditLogBase):
    """監査ログ作成スキーマ"""
    user_id: Optional[int] = Field(None, description="ユーザーID")
    user_email: Optional[str] = Field(None, description="ユーザーメールアドレス")
    user_ip: Optional[str] = Field(None, description="ユーザーIPアドレス")


class AuditLogResponse(AuditLogBase):
    """監査ログ応答スキーマ"""
    id: int
    log_id: str
    user_id: Optional[int]
    user_email: Optional[str]
    user_ip: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    """監査ログ一覧スキーマ"""
    audit_logs: List[AuditLogResponse]
    total: int
    page: int
    size: int


class AuditLogFilter(BaseModel):
    """監査ログフィルタースキーマ"""
    action: Optional[str] = Field(None, description="アクションでフィルター")
    resource_type: Optional[str] = Field(None, description="リソースタイプでフィルター")
    user_id: Optional[int] = Field(None, description="ユーザーIDでフィルター")
    start_date: Optional[datetime] = Field(None, description="開始日時")
    end_date: Optional[datetime] = Field(None, description="終了日時")
    page: int = Field(default=1, description="ページ番号")
    size: int = Field(default=50, description="ページサイズ")


class AuditLogStats(BaseModel):
    """監査ログ統計スキーマ"""
    total_logs: int
    logs_today: int
    logs_this_week: int
    logs_this_month: int
    action_counts: Dict[str, int]
    resource_type_counts: Dict[str, int]
    user_action_counts: Dict[str, int]


class SystemAuditLogCreate(BaseModel):
    """システム監査ログ作成スキーマ"""
    action: str = Field(..., description="アクション")
    resource_type: str = Field(..., description="リソースタイプ")
    description: Optional[str] = Field(None, description="詳細説明")
    details: Optional[Dict[str, Any]] = Field(None, description="追加詳細情報")


class UserAuditLogCreate(BaseModel):
    """ユーザー監査ログ作成スキーマ"""
    user_id: int = Field(..., description="ユーザーID")
    action: str = Field(..., description="アクション")
    resource_type: str = Field(..., description="リソースタイプ")
    description: Optional[str] = Field(None, description="詳細説明")
    details: Optional[Dict[str, Any]] = Field(None, description="追加詳細情報")
    user_ip: Optional[str] = Field(None, description="ユーザーIPアドレス")
    session_id: Optional[str] = Field(None, description="セッションID")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")
