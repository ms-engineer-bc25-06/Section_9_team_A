from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundException, ValidationException

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """ユーザーリポジトリ"""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得"""
        try:
            result = await db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValidationException(f"メールアドレスでのユーザー取得に失敗しました: {str(e)}")

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """ユーザー名でユーザーを取得"""
        try:
            result = await db.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValidationException(f"ユーザー名でのユーザー取得に失敗しました: {str(e)}")

    async def get_by_firebase_uid(self, db: AsyncSession, firebase_uid: str) -> Optional[User]:
        """Firebase UIDでユーザーを取得"""
        try:
            result = await db.execute(
                select(User).where(User.firebase_uid == firebase_uid)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValidationException(f"Firebase UIDでのユーザー取得に失敗しました: {str(e)}")

    async def get_active_users(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """アクティブなユーザー一覧を取得"""
        try:
            query = (
                select(User)
                .where(User.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(desc(User.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise ValidationException(f"アクティブユーザーの取得に失敗しました: {str(e)}")

    async def get_premium_users(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """プレミアムユーザー一覧を取得"""
        try:
            query = (
                select(User)
                .where(User.is_premium == True)
                .offset(skip)
                .limit(limit)
                .order_by(desc(User.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise ValidationException(f"プレミアムユーザーの取得に失敗しました: {str(e)}")

    async def search_users(
        self, 
        db: AsyncSession, 
        search_term: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """ユーザーを検索"""
        try:
            query = (
                select(User)
                .where(
                    and_(
                        User.is_active == True,
                        or_(
                            User.username.ilike(f"%{search_term}%"),
                            User.full_name.ilike(f"%{search_term}%"),
                            User.email.ilike(f"%{search_term}%")
                        )
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(desc(User.created_at))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise ValidationException(f"ユーザー検索に失敗しました: {str(e)}")

    async def update_last_login(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """最終ログイン時刻を更新"""
        try:
            user = await self.get(db, user_id)
            if user:
                user.last_login_at = func.now()
                db.add(user)
                await db.commit()
                await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise ValidationException(f"最終ログイン時刻の更新に失敗しました: {str(e)}")

# グローバルインスタンス
user_repository = UserRepository()
