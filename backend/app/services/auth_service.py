from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import structlog
from datetime import datetime

from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.auth import get_user_by_firebase_uid, create_user_from_firebase

logger = structlog.get_logger()


class AuthService:
    """認証サービス（Firebase認証対応）"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Firebase UIDでユーザー取得"""
        return await get_user_by_firebase_uid(firebase_uid, self.db)

    async def create_user_from_firebase(
        self, firebase_user_data: dict
    ) -> Optional[User]:
        """Firebaseユーザー情報からユーザー作成"""
        return await create_user_from_firebase(firebase_user_data, self.db)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """メールアドレスでユーザー取得"""
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """IDでユーザー取得"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None

    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """ユーザー情報更新"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return None

            # 更新フィールドを設定
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"User updated successfully: {user.email}")
            return user

        except Exception as e:
            logger.error(f"User update failed: {e}")
            await self.db.rollback()
            return None

    async def delete_user(self, user_id: int) -> bool:
        """ユーザー削除"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False

            await self.db.delete(user)
            await self.db.commit()

            logger.info(f"User deleted successfully: {user.email}")
            return True

        except Exception as e:
            logger.error(f"User deletion failed: {e}")
            await self.db.rollback()
            return False

    async def update_user_profile(
        self, user_id: int, profile_data: dict
    ) -> Optional[User]:
        """ユーザープロフィール更新"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return None

            # プロフィールフィールドの更新
            profile_fields = [
                "full_name",
                "avatar_url",
                "bio",
                "nickname",
                "department",
                "join_date",
                "birth_date",
                "hometown",
                "residence",
                "hobbies",
                "student_activities",
                "holiday_activities",
                "favorite_food",
                "favorite_media",
                "favorite_music",
                "pets_oshi",
                "respected_person",
                "motto",
                "future_goals",
            ]

            for field in profile_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])

            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"User profile updated successfully: {user.email}")
            return user

        except Exception as e:
            logger.error(f"User profile update failed: {e}")
            await self.db.rollback()
            return None
