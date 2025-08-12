from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisType, AnalysisCreate, AnalysisUpdate
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundException, ValidationException

class AnalysisRepository(BaseRepository[Analysis, AnalysisCreate, AnalysisUpdate]):
    """分析リポジトリ"""
    
    def __init__(self):
        super().__init__(Analysis)
    
    async def create_analysis(
        self,
        db: AsyncSession,
        analysis_data: Dict[str, Any]
    ) -> Analysis:
        """分析データを作成"""
        try:
            analysis = Analysis(**analysis_data)
            db.add(analysis)
            await db.commit()
            await db.refresh(analysis)
            return analysis
        except Exception as e:
            await db.rollback()
            raise ValidationException(f"分析データの作成に失敗しました: {str(e)}")
    
    async def get_analysis_by_id(
        self,
        db: AsyncSession,
        analysis_id: str,
        user_id: int
    ) -> Optional[Analysis]:
        """分析IDで分析データを取得（ユーザー制限付き）"""
        try:
            query = select(Analysis).where(
                and_(
                    Analysis.analysis_id == analysis_id,
                    Analysis.user_id == user_id
                )
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise ValidationException(f"分析データの取得に失敗しました: {str(e)}")
    
    async def get_user_analyses(
        self,
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        analysis_type: Optional[AnalysisType] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """ユーザーの分析データ一覧を取得"""
        try:
            # 基本クエリ
            query = select(Analysis).where(Analysis.user_id == user_id)
            
            # フィルタリング
            if analysis_type:
                query = query.where(Analysis.analysis_type == analysis_type.value)
            if status:
                query = query.where(Analysis.status == status)
            
            # 総件数を取得
            count_query = select(func.count(Analysis.id)).where(Analysis.user_id == user_id)
            if analysis_type:
                count_query = count_query.where(Analysis.analysis_type == analysis_type.value)
            if status:
                count_query = count_query.where(Analysis.status == status)
            
            total_count = await db.scalar(count_query)
            
            # ページネーション
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(desc(Analysis.created_at))
            
            result = await db.execute(query)
            analyses = result.scalars().all()
            
            return {
                "analyses": analyses,
                "total_count": total_count,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            raise ValidationException(f"分析データ一覧の取得に失敗しました: {str(e)}")
    
    async def get_analyses_by_voice_session(
        self,
        db: AsyncSession,
        voice_session_id: int,
        user_id: int
    ) -> List[Analysis]:
        """音声セッションに関連する分析データを取得"""
        try:
            query = select(Analysis).where(
                and_(
                    Analysis.voice_session_id == voice_session_id,
                    Analysis.user_id == user_id
                )
            ).order_by(desc(Analysis.created_at))
            
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise ValidationException(f"音声セッション関連の分析データ取得に失敗しました: {str(e)}")
    
    async def get_analyses_by_transcription(
        self,
        db: AsyncSession,
        transcription_id: int,
        user_id: int
    ) -> List[Analysis]:
        """文字起こしに関連する分析データを取得"""
        try:
            query = select(Analysis).where(
                and_(
                    Analysis.transcription_id == transcription_id,
                    Analysis.user_id == user_id
                )
            ).order_by(desc(Analysis.created_at))
            
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise ValidationException(f"文字起こし関連の分析データ取得に失敗しました: {str(e)}")
    
    async def update_analysis(
        self,
        db: AsyncSession,
        analysis_id: str,
        user_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Analysis]:
        """分析データを更新"""
        try:
            analysis = await self.get_analysis_by_id(db, analysis_id, user_id)
            if not analysis:
                return None
            
            for key, value in update_data.items():
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            
            await db.commit()
            await db.refresh(analysis)
            return analysis
            
        except Exception as e:
            await db.rollback()
            raise ValidationException(f"分析データの更新に失敗しました: {str(e)}")
    
    async def delete_analysis(
        self,
        db: AsyncSession,
        analysis_id: str,
        user_id: int
    ) -> bool:
        """分析データを削除"""
        try:
            analysis = await self.get_analysis_by_id(db, analysis_id, user_id)
            if not analysis:
                return False
            
            await db.delete(analysis)
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            raise ValidationException(f"分析データの削除に失敗しました: {str(e)}")
    
    async def get_analysis_statistics(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """ユーザーの分析統計を取得"""
        try:
            from datetime import datetime, timedelta
            
            # 指定日数前の日付を計算
            start_date = datetime.now() - timedelta(days=days)
            
            # 分析タイプ別の件数
            type_count_query = select(
                Analysis.analysis_type,
                func.count(Analysis.id)
            ).where(
                and_(
                    Analysis.user_id == user_id,
                    Analysis.created_at >= start_date
                )
            ).group_by(Analysis.analysis_type)
            
            result = await db.execute(type_count_query)
            type_counts = dict(result.all())
            
            # 感情分析の平均スコア
            sentiment_query = select(
                func.avg(Analysis.sentiment_score)
            ).where(
                and_(
                    Analysis.user_id == user_id,
                    Analysis.sentiment_score.isnot(None),
                    Analysis.created_at >= start_date
                )
            )
            
            avg_sentiment = await db.scalar(sentiment_query)
            
            # 総分析件数
            total_count_query = select(func.count(Analysis.id)).where(
                and_(
                    Analysis.user_id == user_id,
                    Analysis.created_at >= start_date
                )
            )
            total_count = await db.scalar(total_count_query)
            
            return {
                "total_count": total_count,
                "type_counts": type_counts,
                "average_sentiment": float(avg_sentiment) if avg_sentiment else 0.0,
                "period_days": days
            }
            
        except Exception as e:
            raise ValidationException(f"分析統計の取得に失敗しました: {str(e)}")
    
    async def get_recent_analyses(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 5
    ) -> List[Analysis]:
        """最近の分析データを取得"""
        try:
            query = select(Analysis).where(
                Analysis.user_id == user_id
            ).order_by(desc(Analysis.created_at)).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationException(f"最近の分析データ取得に失敗しました: {str(e)}")
    
    async def get_analyses_by_keywords(
        self,
        db: AsyncSession,
        user_id: int,
        keywords: List[str],
        limit: int = 20
    ) -> List[Analysis]:
        """キーワードで分析データを検索"""
        try:
            # PostgreSQLのJSONB演算子を使用してキーワード検索
            from sqlalchemy import or_
            
            conditions = []
            for keyword in keywords:
                # keywordsフィールドにキーワードが含まれているかチェック
                conditions.append(Analysis.keywords.contains([keyword]))
                # topicsフィールドにキーワードが含まれているかチェック
                conditions.append(Analysis.topics.contains([keyword]))
                # 内容にキーワードが含まれているかチェック
                conditions.append(Analysis.content.ilike(f"%{keyword}%"))
            
            query = select(Analysis).where(
                and_(
                    Analysis.user_id == user_id,
                    or_(*conditions)
                )
            ).order_by(desc(Analysis.created_at)).limit(limit)
            
            result = await db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise ValidationException(f"キーワード検索に失敗しました: {str(e)}")
