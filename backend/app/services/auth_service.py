from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import structlog
from datetime import datetime

from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.auth import get_password_hash, verify_password

logger = structlog.get_logger()


class AuthService:
    """認証サービス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """ユーザー認証"""
        try:
            # ユーザー取得
            result = await self.db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if not user:
                return None

            # パスワード検証
            if not verify_password(password, user.hashed_password):
                return None

            # 最終ログイン時刻更新
            user.last_login_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"User authenticated successfully: {email}")
            return user

        except Exception as e:
            logger.error(f"Authentication failed for {email}: {e}")
            await self.db.rollback()
            return None

    async def create_user(self, user_data: UserCreate) -> User:
        """ユーザー作成"""
        try:
            # 既存ユーザーチェック
            result = await self.db.execute(
                select(User).where(User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                raise ValueError("Email already registered")

            result = await self.db.execute(
                select(User).where(User.username == user_data.username)
            )
            if result.scalar_one_or_none():
                raise ValueError("Username already taken")

            # パスワードハッシュ化
            hashed_password = get_password_hash(user_data.password)

            # ユーザー作成
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                avatar_url=user_data.avatar_url,
                bio=user_data.bio,
                firebase_uid=user_data.firebase_uid,
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"User created successfully: {user.email}")
            return user

        except ValueError as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            await self.db.rollback()
            raise ValueError("Failed to create user")

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
                    # 日付フィールドの特別処理
                    if field in ["join_date", "birth_date"] and value == "":
                        setattr(user, field, None)  # 空文字列の場合はNULLに設定
                    else:
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

    async def get_or_create_firebase_user(
        self, firebase_uid: str, email: str, display_name: str | None = None
    ) -> User:
        """Firebaseユーザーを取得または作成"""
        try:
            logger.info(
                f"Starting get_or_create_firebase_user for email: {email}, firebase_uid: {firebase_uid}"
            )

            # 既存ユーザーを検索（firebase_uidまたはemailで）
            logger.info(
                f"Searching for existing user with firebase_uid: {firebase_uid} or email: {email}"
            )
            result = await self.db.execute(
                select(User).where(
                    (User.firebase_uid == firebase_uid) | (User.email == email)
                )
            )
            user = result.scalar_one_or_none()

            if user:
                logger.info(f"Found existing user: {user.id}, updating information")
                # 既存ユーザーの情報を更新
                if not user.firebase_uid:
                    user.firebase_uid = firebase_uid
                user.email = email
                user.last_login_at = datetime.utcnow()
                if display_name:
                    user.full_name = display_name
                user.is_verified = True
                user.is_active = True

                await self.db.commit()
                await self.db.refresh(user)
                logger.info(f"Existing Firebase user logged in: {email}")
                return user

            logger.info(f"No existing user found, creating new user for email: {email}")
            # 新しいユーザーを作成
            # ユーザー名の重複を避ける
            username = email.split("@")[0]
            counter = 1
            original_username = username

            while True:
                result = await self.db.execute(
                    select(User).where(User.username == username)
                )
                if not result.scalar_one_or_none():
                    break
                username = f"{original_username}{counter}"
                counter += 1

            logger.info(f"Creating new user with username: {username}")
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                username=username,
                full_name=display_name or email,  # Noneの場合はemailを使用
                is_active=True,
                is_verified=True,
                last_login_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            logger.info(f"Adding user to database: {user.email}")
            self.db.add(user)
            logger.info(f"Committing user to database")
            await self.db.commit()
            logger.info(f"Refreshing user object")
            await self.db.refresh(user)

            logger.info(f"New Firebase user created: {email} with username: {username}")
            return user

        except Exception as e:
            logger.error(f"Firebase user creation/update failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            await self.db.rollback()
            raise ValueError(f"Failed to create or update Firebase user: {str(e)}")
