from typing import Generic, TypeVar, Type, Optional, List, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import structlog

from app.models.base import Base

logger = structlog.get_logger()

# ジェネリック型定義
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """ベースリポジトリクラス"""

    def __init__(self, model: Type[ModelType]):
        """
        Args:
            model: SQLAlchemyモデルクラス
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """IDでレコードを取得"""
        try:
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting record with id {id}: {e}")
            raise

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
    ) -> List[ModelType]:
        """複数レコードを取得"""
        try:
            query = select(self.model)

            # フィルター適用
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.where(getattr(self.model, field) == value)

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting multiple records: {e}")
            raise

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """レコードを作成"""
        try:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating record: {e}")
            raise

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict[str, Any]],
    ) -> ModelType:
        """レコードを更新"""
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating record: {e}")
            raise

    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """レコードを削除"""
        try:
            obj = await self.get(db, id)
            if obj:
                await db.delete(obj)
                await db.commit()
            return obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting record with id {id}: {e}")
            raise

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """レコードの存在確認"""
        try:
            query = select(self.model).where(self.model.id == id)
            result = await db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking existence of record with id {id}: {e}")
            raise

    async def count(self, db: AsyncSession, filters: Optional[dict] = None) -> int:
        """レコード数を取得"""
        try:
            query = select(self.model)

            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        query = query.where(getattr(self.model, field) == value)

            result = await db.execute(query)
            return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            raise
