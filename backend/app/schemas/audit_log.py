"""
監査ログのスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AuditLogBase(BaseModel):
    """監査ログ基本スキーマ"""
    user_id: Optional[int] = Field(None, description="ユーザーID")
    action: str = Field(..., description="実行されたアクション", max_length=100)
    resource_type: str = Field(..., description="リソースタイプ", max_length=100)
    resource_id: Optional[str] = Field(None, description="リソースID")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細情報")
    ip_address: Optional[str] = Field(None, description="IPアドレス", max_length=45)
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント", max_length=500)


class AuditLogCreate(AuditLogBase):
    """監査ログ作成スキーマ"""
    pass


class AuditLogUpdate(BaseModel):
    """監査ログ更新スキーマ"""
    action: Optional[str] = Field(None, description="実行されたアクション", max_length=100)
    resource_type: Optional[str] = Field(None, description="リソースタイプ", max_length=100)
    resource_id: Optional[str] = Field(None, description="リソースID")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細情報")
    ip_address: Optional[str] = Field(None, description="IPアドレス", max_length=45)
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント", max_length=500)


class AuditLogResponse(AuditLogBase):
    """監査ログ応答スキーマ"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """監査ログ一覧応答スキーマ"""
    audit_logs: List[AuditLogResponse]
    total_count: int
    page: int
    page_size: int


class AuditLogFilter(BaseModel):
    """監査ログフィルタースキーマ"""
    user_id: Optional[int] = Field(None, description="ユーザーIDでフィルタリング")
    action: Optional[str] = Field(None, description="アクションでフィルタリング")
    resource_type: Optional[str] = Field(None, description="リソースタイプでフィルタリング")
    start_date: Optional[datetime] = Field(None, description="開始日時")
    end_date: Optional[datetime] = Field(None, description="終了日時")
    ip_address: Optional[str] = Field(None, description="IPアドレスでフィルタリング")
