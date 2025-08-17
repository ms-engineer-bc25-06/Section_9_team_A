from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
import structlog

from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate, UserResponse

logger = structlog.get_logger()


class UserService:
    """ユーザーサービス"""

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """ユーザーを作成"""
        return await user_repository.create(db, user_data)

    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """ユーザーを取得"""
        return await user_repository.get(db, user_id)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        return await user_repository.get_by_email(db, email)

    async def get_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """ユーザー一覧を取得"""
        return await user_repository.get_multi(db, skip=skip, limit=limit)

    async def update_user(
        self, db: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """ユーザーを更新"""
        return await user_repository.update(db, user_id, user_data)

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """ユーザーを削除"""
        return await user_repository.delete(db, user_id)

    async def get_team_members(
        self, db: AsyncSession, team_id: int
    ) -> List[User]:
        """チームのメンバーを取得"""
        return await user_repository.get_team_members(db, team_id)

    async def search_users(
        self, db: AsyncSession, query: str, limit: int = 50
    ) -> List[User]:
        """ユーザーを検索"""
        return await user_repository.search_users(db, query, limit)


# シングルトンインスタンス
user_service = UserService()
