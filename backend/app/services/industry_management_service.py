import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.orm import selectinload

from app.models.industry_benchmark import (
    IndustryBenchmark, IndustryBenchmarkHistory, IndustryBenchmarkRequest
)
from app.models.user import User
from app.schemas.industry_management import (
    IndustryBenchmarkCreate, IndustryBenchmarkUpdate, IndustryBenchmarkResponse,
    IndustryBenchmarkRequestCreate, IndustryBenchmarkRequestUpdate, IndustryBenchmarkRequestResponse,
    IndustryBenchmarkFilter, IndustryBenchmarkBulkCreate, IndustryBenchmarkStats,
    CompanySize, RequestStatus
)
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException, DuplicateException
)

logger = structlog.get_logger()


class IndustryManagementService:
    """業界管理サービス"""

    def __init__(self):
        pass

    async def create_industry_benchmark(
        self,
        db: AsyncSession,
        user: User,
        benchmark_data: IndustryBenchmarkCreate
    ) -> IndustryBenchmarkResponse:
        """業界ベンチマークを作成"""
        try:
            # 権限チェック（管理者または責任者のみ）
            if not await self._check_management_permission(db, user):
                raise PermissionException("業界ベンチマークの作成権限がありません")

            # 重複チェック
            existing = await self._get_benchmark_by_code_and_size(
                db, benchmark_data.industry_code, benchmark_data.company_size
            )
            if existing:
                raise DuplicateException(
                    f"業界コード {benchmark_data.industry_code} と企業規模 {benchmark_data.company_size} の組み合わせは既に存在します"
                )

            # ベンチマークデータの作成
            benchmark = IndustryBenchmark(
                industry_name=benchmark_data.industry_name,
                industry_code=benchmark_data.industry_code,
                display_name=benchmark_data.display_name,
                description=benchmark_data.description,
                company_size=benchmark_data.company_size,
                company_size_display=benchmark_data.company_size_display,
                communication_skills_avg=benchmark_data.communication_skills_avg,
                leadership_avg=benchmark_data.leadership_avg,
                collaboration_avg=benchmark_data.collaboration_avg,
                problem_solving_avg=benchmark_data.problem_solving_avg,
                emotional_intelligence_avg=benchmark_data.emotional_intelligence_avg,
                best_practices=benchmark_data.best_practices,
                data_source=benchmark_data.data_source,
                data_source_url=benchmark_data.data_source_url,
                confidence_level=benchmark_data.confidence_level,
                is_public=benchmark_data.is_public,
                tags=benchmark_data.tags or [],
                notes=benchmark_data.notes,
                created_by=user.id
            )

            db.add(benchmark)
            await db.commit()
            await db.refresh(benchmark)

            # 履歴の記録
            await self._record_history(db, benchmark, "create", user.id, "新規作成")

            logger.info(
                "業界ベンチマークを作成",
                benchmark_id=benchmark.id,
                industry_code=benchmark.industry_code,
                created_by=user.id
            )

            return IndustryBenchmarkResponse.from_orm(benchmark)

        except Exception as e:
            await db.rollback()
            logger.error(f"業界ベンチマーク作成に失敗: {e}")
            raise

    async def update_industry_benchmark(
        self,
        db: AsyncSession,
        user: User,
        benchmark_id: int,
        update_data: IndustryBenchmarkUpdate
    ) -> IndustryBenchmarkResponse:
        """業界ベンチマークを更新"""
        try:
            # 権限チェック
            if not await self._check_management_permission(db, user):
                raise PermissionException("業界ベンチマークの更新権限がありません")

            # ベンチマークの取得
            benchmark = await self._get_benchmark_by_id(db, benchmark_id)
            if not benchmark:
                raise NotFoundException("業界ベンチマークが見つかりません")

            # 変更前のデータを保存（履歴用）
            previous_data = self._benchmark_to_dict(benchmark)

            # 更新可能なフィールドのみ更新
            update_fields = update_data.dict(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(benchmark, field, value)

            benchmark.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(benchmark)

            # 履歴の記録
            await self._record_history(db, benchmark, "update", user.id, "データ更新", previous_data)

            logger.info(
                "業界ベンチマークを更新",
                benchmark_id=benchmark.id,
                updated_by=user.id
            )

            return IndustryBenchmarkResponse.from_orm(benchmark)

        except Exception as e:
            await db.rollback()
            logger.error(f"業界ベンチマーク更新に失敗: {e}")
            raise

    async def delete_industry_benchmark(
        self,
        db: AsyncSession,
        user: User,
        benchmark_id: int
    ) -> bool:
        """業界ベンチマークを削除（論理削除）"""
        try:
            # 権限チェック
            if not await self._check_management_permission(db, user):
                raise PermissionException("業界ベンチマークの削除権限がありません")

            # ベンチマークの取得
            benchmark = await self._get_benchmark_by_id(db, benchmark_id)
            if not benchmark:
                raise NotFoundException("業界ベンチマークが見つかりません")

            # 変更前のデータを保存（履歴用）
            previous_data = self._benchmark_to_dict(benchmark)

            # 論理削除（is_activeをFalseに設定）
            benchmark.is_active = False
            benchmark.updated_at = datetime.utcnow()
            await db.commit()

            # 履歴の記録
            await self._record_history(db, benchmark, "delete", user.id, "論理削除", previous_data)

            logger.info(
                "業界ベンチマークを削除",
                benchmark_id=benchmark.id,
                deleted_by=user.id
            )

            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"業界ベンチマーク削除に失敗: {e}")
            raise

    async def get_industry_benchmarks(
        self,
        db: AsyncSession,
        user: User,
        filters: Optional[IndustryBenchmarkFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[IndustryBenchmarkResponse], int]:
        """業界ベンチマーク一覧を取得"""
        try:
            # クエリの構築
            query = select(IndustryBenchmark).where(IndustryBenchmark.is_active == True)
            count_query = select(func.count(IndustryBenchmark.id)).where(IndustryBenchmark.is_active == True)

            # フィルターの適用
            if filters:
                query, count_query = self._apply_filters(query, count_query, filters, user)

            # ソートとページネーション
            query = query.order_by(desc(IndustryBenchmark.updated_at)).offset(skip).limit(limit)

            # データの取得
            result = await db.execute(query)
            benchmarks = result.scalars().all()

            # 総件数の取得
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()

            return [IndustryBenchmarkResponse.from_orm(b) for b in benchmarks], total_count

        except Exception as e:
            logger.error(f"業界ベンチマーク一覧取得に失敗: {e}")
            raise

    async def get_industry_benchmark(
        self,
        db: AsyncSession,
        user: User,
        benchmark_id: int
    ) -> IndustryBenchmarkResponse:
        """業界ベンチマーク詳細を取得"""
        try:
            benchmark = await self._get_benchmark_by_id(db, benchmark_id)
            if not benchmark:
                raise NotFoundException("業界ベンチマークが見つかりません")

            # 公開チェック
            if not benchmark.is_public and not await self._check_management_permission(db, user):
                raise PermissionException("この業界ベンチマークへのアクセス権限がありません")

            return IndustryBenchmarkResponse.from_orm(benchmark)

        except Exception as e:
            logger.error(f"業界ベンチマーク詳細取得に失敗: {e}")
            raise

    async def create_benchmark_request(
        self,
        db: AsyncSession,
        user: User,
        request_data: IndustryBenchmarkRequestCreate
    ) -> IndustryBenchmarkRequestResponse:
        """業界ベンチマーク追加リクエストを作成"""
        try:
            # 重複リクエストチェック
            existing_request = await self._get_pending_request_by_user_and_industry(
                db, user.id, request_data.industry_code, request_data.company_size
            )
            if existing_request:
                raise DuplicateException("同じ業界・企業規模のリクエストが既に存在します")

            # リクエストの作成
            request = IndustryBenchmarkRequest(
                requester_id=user.id,
                requester_role=await self._get_user_role(db, user.id),
                industry_name=request_data.industry_name,
                industry_code=request_data.industry_code,
                company_size=request_data.company_size,
                proposed_metrics=request_data.proposed_metrics,
                proposed_best_practices=request_data.proposed_best_practices,
                data_source=request_data.data_source
            )

            db.add(request)
            await db.commit()
            await db.refresh(request)

            logger.info(
                "業界ベンチマーク追加リクエストを作成",
                request_id=request.id,
                requester_id=user.id,
                industry_code=request.industry_code
            )

            return IndustryBenchmarkRequestResponse.from_orm(request)

        except Exception as e:
            await db.rollback()
            logger.error(f"業界ベンチマーク追加リクエスト作成に失敗: {e}")
            raise

    async def review_benchmark_request(
        self,
        db: AsyncSession,
        user: User,
        request_id: int,
        review_data: IndustryBenchmarkRequestUpdate
    ) -> IndustryBenchmarkRequestResponse:
        """業界ベンチマーク追加リクエストをレビュー"""
        try:
            # 権限チェック
            if not await self._check_management_permission(db, user):
                raise PermissionException("リクエストのレビュー権限がありません")

            # リクエストの取得
            request = await self._get_request_by_id(db, request_id)
            if not request:
                raise NotFoundException("リクエストが見つかりません")

            # ステータス更新
            request.status = review_data.status
            request.reviewed_by = user.id
            request.review_notes = review_data.review_notes
            request.reviewed_at = datetime.utcnow()
            request.updated_at = datetime.utcnow()

            # 承認された場合、ベンチマークを作成
            if review_data.status == RequestStatus.APPROVED:
                await self._create_benchmark_from_request(db, request, user)

            await db.commit()
            await db.refresh(request)

            logger.info(
                "業界ベンチマーク追加リクエストをレビュー",
                request_id=request.id,
                status=review_data.status,
                reviewed_by=user.id
            )

            return IndustryBenchmarkRequestResponse.from_orm(request)

        except Exception as e:
            await db.rollback()
            logger.error(f"業界ベンチマーク追加リクエストレビューに失敗: {e}")
            raise

    async def get_benchmark_requests(
        self,
        db: AsyncSession,
        user: User,
        status: Optional[RequestStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[IndustryBenchmarkRequestResponse], int]:
        """業界ベンチマーク追加リクエスト一覧を取得"""
        try:
            # 権限に応じたクエリの構築
            if await self._check_management_permission(db, user):
                # 管理者・責任者は全リクエストを閲覧可能
                query = select(IndustryBenchmarkRequest)
                count_query = select(func.count(IndustryBenchmarkRequest.id))
            else:
                # 一般ユーザーは自分のリクエストのみ閲覧可能
                query = select(IndustryBenchmarkRequest).where(IndustryBenchmarkRequest.requester_id == user.id)
                count_query = select(func.count(IndustryBenchmarkRequest.id)).where(IndustryBenchmarkRequest.requester_id == user.id)

            # ステータスフィルター
            if status:
                query = query.where(IndustryBenchmarkRequest.status == status)
                count_query = count_query.where(IndustryBenchmarkRequest.status == status)

            # ソートとページネーション
            query = query.order_by(desc(IndustryBenchmarkRequest.created_at)).offset(skip).limit(limit)

            # データの取得
            result = await db.execute(query)
            requests = result.scalars().all()

            # 総件数の取得
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()

            return [IndustryBenchmarkRequestResponse.from_orm(r) for r in requests], total_count

        except Exception as e:
            logger.error(f"業界ベンチマーク追加リクエスト一覧取得に失敗: {e}")
            raise

    async def get_benchmark_stats(
        self,
        db: AsyncSession,
        user: User
    ) -> IndustryBenchmarkStats:
        """業界ベンチマーク統計情報を取得"""
        try:
            # 権限チェック
            if not await self._check_management_permission(db, user):
                raise PermissionException("統計情報の閲覧権限がありません")

            # 基本統計
            total_result = await db.execute(select(func.count(IndustryBenchmark.id)))
            total_benchmarks = total_result.scalar()

            active_result = await db.execute(
                select(func.count(IndustryBenchmark.id)).where(IndustryBenchmark.is_active == True)
            )
            active_benchmarks = active_result.scalar()

            public_result = await db.execute(
                select(func.count(IndustryBenchmark.id)).where(
                    and_(IndustryBenchmark.is_active == True, IndustryBenchmark.is_public == True)
                )
            )
            public_benchmarks = public_result.scalar()

            # 業界別統計
            industry_counts_result = await db.execute(
                select(
                    IndustryBenchmark.industry_name,
                    func.count(IndustryBenchmark.id)
                ).where(IndustryBenchmark.is_active == True).group_by(IndustryBenchmark.industry_name)
            )
            industry_counts = dict(industry_counts_result.all())

            # 企業規模別統計
            size_counts_result = await db.execute(
                select(
                    IndustryBenchmark.company_size,
                    func.count(IndustryBenchmark.id)
                ).where(IndustryBenchmark.is_active == True).group_by(IndustryBenchmark.company_size)
            )
            company_size_counts = dict(size_counts_result.all())

            # データ品質統計
            confidence_result = await db.execute(
                select(func.avg(IndustryBenchmark.confidence_level)).where(IndustryBenchmark.is_active == True)
            )
            average_confidence = confidence_result.scalar() or 0.0

            # 最近更新されたベンチマーク数
            recent_date = datetime.utcnow() - timedelta(days=30)
            recent_result = await db.execute(
                select(func.count(IndustryBenchmark.id)).where(
                    and_(
                        IndustryBenchmark.is_active == True,
                        IndustryBenchmark.updated_at >= recent_date
                    )
                )
            )
            recently_updated = recent_result.scalar()

            # リクエスト統計
            total_requests_result = await db.execute(select(func.count(IndustryBenchmarkRequest.id)))
            total_requests = total_requests_result.scalar()

            pending_requests_result = await db.execute(
                select(func.count(IndustryBenchmarkRequest.id)).where(IndustryBenchmarkRequest.status == RequestStatus.PENDING)
            )
            pending_requests = pending_requests_result.scalar()

            approved_requests_result = await db.execute(
                select(func.count(IndustryBenchmarkRequest.id)).where(IndustryBenchmarkRequest.status == RequestStatus.APPROVED)
            )
            approved_requests = approved_requests_result.scalar()

            return IndustryBenchmarkStats(
                total_benchmarks=total_benchmarks,
                active_benchmarks=active_benchmarks,
                public_benchmarks=public_benchmarks,
                industry_counts=industry_counts,
                company_size_counts=company_size_counts,
                average_confidence=average_confidence,
                recently_updated=recently_updated,
                total_requests=total_requests,
                pending_requests=pending_requests,
                approved_requests=approved_requests
            )

        except Exception as e:
            logger.error(f"業界ベンチマーク統計情報取得に失敗: {e}")
            raise

    # プライベートメソッド

    async def _check_management_permission(self, db: AsyncSession, user: User) -> bool:
        """管理権限のチェック"""
        # TODO: 実際の権限チェックロジックを実装
        # 現在は管理者ロールを持つユーザーのみ許可
        return user.role == "admin" or user.role == "manager"

    async def _get_benchmark_by_id(self, db: AsyncSession, benchmark_id: int) -> Optional[IndustryBenchmark]:
        """IDでベンチマークを取得"""
        result = await db.execute(
            select(IndustryBenchmark).where(IndustryBenchmark.id == benchmark_id)
        )
        return result.scalar_one_or_none()

    async def _get_benchmark_by_code_and_size(
        self, db: AsyncSession, industry_code: str, company_size: str
    ) -> Optional[IndustryBenchmark]:
        """業界コードと企業規模でベンチマークを取得"""
        result = await db.execute(
            select(IndustryBenchmark).where(
                and_(
                    IndustryBenchmark.industry_code == industry_code,
                    IndustryBenchmark.company_size == company_size,
                    IndustryBenchmark.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_request_by_id(self, db: AsyncSession, request_id: int) -> Optional[IndustryBenchmarkRequest]:
        """IDでリクエストを取得"""
        result = await db.execute(
            select(IndustryBenchmarkRequest).where(IndustryBenchmarkRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def _get_pending_request_by_user_and_industry(
        self, db: AsyncSession, user_id: int, industry_code: str, company_size: str
    ) -> Optional[IndustryBenchmarkRequest]:
        """ユーザーと業界・企業規模で保留中のリクエストを取得"""
        result = await db.execute(
            select(IndustryBenchmarkRequest).where(
                and_(
                    IndustryBenchmarkRequest.requester_id == user_id,
                    IndustryBenchmarkRequest.industry_code == industry_code,
                    IndustryBenchmarkRequest.company_size == company_size,
                    IndustryBenchmarkRequest.status == RequestStatus.PENDING
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_user_role(self, db: AsyncSession, user_id: int) -> str:
        """ユーザーの役割を取得"""
        # TODO: 実際のユーザーロール取得ロジックを実装
        return "user"

    async def _record_history(
        self,
        db: AsyncSession,
        benchmark: IndustryBenchmark,
        change_type: str,
        changed_by: int,
        change_reason: str,
        previous_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """変更履歴を記録"""
        history = IndustryBenchmarkHistory(
            benchmark_id=benchmark.id,
            previous_data=previous_data,
            change_type=change_type,
            changed_by=changed_by,
            change_reason=change_reason
        )
        db.add(history)

    def _benchmark_to_dict(self, benchmark: IndustryBenchmark) -> Dict[str, Any]:
        """ベンチマークを辞書形式に変換"""
        return {
            "id": benchmark.id,
            "industry_name": benchmark.industry_name,
            "industry_code": benchmark.industry_code,
            "display_name": benchmark.display_name,
            "description": benchmark.description,
            "company_size": benchmark.company_size,
            "company_size_display": benchmark.company_size_display,
            "communication_skills_avg": benchmark.communication_skills_avg,
            "leadership_avg": benchmark.leadership_avg,
            "collaboration_avg": benchmark.collaboration_avg,
            "problem_solving_avg": benchmark.problem_solving_avg,
            "emotional_intelligence_avg": benchmark.emotional_intelligence_avg,
            "best_practices": benchmark.best_practices,
            "data_source": benchmark.data_source,
            "data_source_url": benchmark.data_source_url,
            "confidence_level": benchmark.confidence_level,
            "is_public": benchmark.is_public,
            "is_active": benchmark.is_active,
            "tags": benchmark.tags,
            "notes": benchmark.notes
        }

    def _apply_filters(
        self,
        query: select,
        count_query: select,
        filters: IndustryBenchmarkFilter,
        user: User
    ) -> Tuple[select, select]:
        """フィルターを適用"""
        # 業界名フィルター
        if filters.industry_name:
            industry_filter = IndustryBenchmark.industry_name.ilike(f"%{filters.industry_name}%")
            query = query.where(industry_filter)
            count_query = count_query.where(industry_filter)

        # 企業規模フィルター
        if filters.company_size:
            query = query.where(IndustryBenchmark.company_size == filters.company_size)
            count_query = count_query.where(IndustryBenchmark.company_size == filters.company_size)

        # 有効フラグフィルター
        if filters.is_active is not None:
            query = query.where(IndustryBenchmark.is_active == filters.is_active)
            count_query = count_query.where(IndustryBenchmark.is_active == filters.is_active)

        # 公開フラグフィルター
        if filters.is_public is not None:
            query = query.where(IndustryBenchmark.is_public == filters.is_public)
            count_query = count_query.where(IndustryBenchmark.is_public == filters.is_public)

        # タグフィルター
        if filters.tags:
            for tag in filters.tags:
                query = query.where(IndustryBenchmark.tags.contains([tag]))
                count_query = count_query.where(IndustryBenchmark.tags.contains([tag]))

        # 作成者フィルター
        if filters.created_by:
            query = query.where(IndustryBenchmark.created_by == filters.created_by)
            count_query = count_query.where(IndustryBenchmark.created_by == filters.created_by)

        return query, count_query

    async def _create_benchmark_from_request(
        self,
        db: AsyncSession,
        request: IndustryBenchmarkRequest,
        user: User
    ) -> None:
        """リクエストからベンチマークを作成"""
        # ベンチマークデータの作成
        benchmark = IndustryBenchmark(
            industry_name=request.industry_name,
            industry_code=request.industry_code,
            display_name=request.industry_name,  # デフォルト値
            company_size=request.company_size,
            company_size_display=request.company_size.value,  # デフォルト値
            communication_skills_avg=request.proposed_metrics.get("communication_skills", 0.75),
            leadership_avg=request.proposed_metrics.get("leadership", 0.75),
            collaboration_avg=request.proposed_metrics.get("collaboration", 0.75),
            problem_solving_avg=request.proposed_metrics.get("problem_solving", 0.75),
            emotional_intelligence_avg=request.proposed_metrics.get("emotional_intelligence", 0.75),
            best_practices=request.proposed_best_practices,
            data_source=request.data_source,
            confidence_level=0.8,  # デフォルト値
            is_public=True,  # デフォルト値
            created_by=request.requester_id
        )

        db.add(benchmark)


# グローバルインスタンス
industry_management_service = IndustryManagementService()
