from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """ステータス列挙型"""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PaginationParams(BaseModel):
    """ページネーションパラメータ"""

    page: int = Field(1, ge=1, description="ページ番号")
    size: int = Field(10, ge=1, le=100, description="ページサイズ")


class PaginatedResponse(BaseModel):
    """ページネーション応答スキーマ"""

    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class BaseResponse(BaseModel):
    """基本応答スキーマ"""

    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """エラー応答スキーマ"""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class TimestampMixin(BaseModel):
    """タイムスタンプミキシン"""

    created_at: datetime
    updated_at: Optional[datetime] = None
