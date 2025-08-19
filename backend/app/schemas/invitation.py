from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class InvitationBase(BaseModel):
    """招待基本スキーマ"""
    email: EmailStr = Field(..., description="招待先メールアドレス")
    invitation_type: str = Field(..., description="招待タイプ（team, project等）")
    role: str = Field(default="member", description="役割（owner, admin, member, guest）")
    message: Optional[str] = Field(None, description="招待メッセージ")
    team_id: Optional[int] = Field(None, description="チームID")
    expires_in_days: int = Field(default=7, description="有効期限（日数）")


class InvitationCreate(InvitationBase):
    """招待作成スキーマ"""
    pass


class InvitationUpdate(BaseModel):
    """招待更新スキーマ"""
    role: Optional[str] = Field(None, description="役割")
    message: Optional[str] = Field(None, description="招待メッセージ")
    expires_in_days: Optional[int] = Field(None, description="有効期限（日数）")


class InvitationResponse(InvitationBase):
    """招待応答スキーマ"""
    id: int
    invitation_id: str
    status: str
    is_active: bool
    invited_by: int
    invited_user: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    accepted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InvitationList(BaseModel):
    """招待一覧スキーマ"""
    invitations: List[InvitationResponse]
    total: int
    page: int
    size: int


class InvitationAccept(BaseModel):
    """招待承認スキーマ"""
    token: str = Field(..., description="招待トークン")


class InvitationDecline(BaseModel):
    """招待辞退スキーマ"""
    token: str = Field(..., description="招待トークン")


class InvitationResend(BaseModel):
    """招待再送信スキーマ"""
    invitation_id: int = Field(..., description="招待ID")


class InvitationCancel(BaseModel):
    """招待キャンセルスキーマ"""
    invitation_id: int = Field(..., description="招待ID")


class InvitationStats(BaseModel):
    """招待統計スキーマ"""
    total_invitations: int
    pending_invitations: int
    accepted_invitations: int
    declined_invitations: int
    expired_invitations: int
    active_invitations: int
