import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.models.feedback_approval import FeedbackApproval, ApprovalStatus, VisibilityLevel
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.feedback_approval import (
    FeedbackApprovalCreate, FeedbackApprovalUpdate, ApprovalRequest,
    UserConfirmationRequest, StagedPublicationRequest, PublicationStage,
    FeedbackApprovalStats
)
from app.core.exceptions import (
    NotFoundException, PermissionException, ValidationException,
    BusinessLogicException
)

logger = structlog.get_logger()


class FeedbackApprovalService:
    """フィードバック承認サービス"""

    def __init__(self):
        pass

    async def create_approval_request(
        self,
        db: AsyncSession,
        user: User,
        approval_data: ApprovalRequest
    ) -> FeedbackApproval:
        """承認リクエストを作成"""
        try:
            # 分析結果の存在確認
            analysis = await self._get_analysis(db, approval_data.analysis_id)
            
            # 権限チェック（分析結果の所有者かチェック）
            if analysis.user_id != user.id:
                raise PermissionException("分析結果の所有者のみが承認リクエストを作成できます")
            
            # 既存の承認リクエストがあるかチェック
            existing_approval = await self._get_existing_approval(
                db, approval_data.analysis_id, user.id
            )
            if existing_approval:
                raise BusinessLogicException("既に承認リクエストが存在します")
            
            # 段階的公開の設定
            publication_stages_json = None
            if approval_data.is_staged_publication and approval_data.publication_stages:
                publication_stages_json = self._serialize_publication_stages(
                    approval_data.publication_stages
                )
            
            # 承認リクエストを作成
            approval = FeedbackApproval(
                analysis_id=approval_data.analysis_id,
                requester_id=user.id,
                visibility_level=approval_data.visibility_level,
                request_reason=approval_data.request_reason,
                is_staged_publication=approval_data.is_staged_publication,
                publication_stages=publication_stages_json,
                requires_confirmation=True
            )
            
            # 承認リクエストを保存
            db.add(approval)
            await db.commit()
            await db.refresh(approval)
            
            logger.info(
                "承認リクエストを作成",
                approval_id=approval.id,
                analysis_id=approval_data.analysis_id,
                user_id=user.id
            )
            
            return approval
            
        except Exception as e:
            await db.rollback()
            logger.error(f"承認リクエストの作成に失敗: {e}")
            raise

    async def get_user_approvals(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[FeedbackApproval], int]:
        """ユーザーの承認リクエスト一覧を取得"""
        try:
            # クエリの構築
            query = select(FeedbackApproval).where(
                FeedbackApproval.requester_id == user.id
            )
            
            # フィルターの適用
            if filters:
                query = self._apply_filters(query, filters)
            
            # 総件数を取得
            count_query = select(func.count(FeedbackApproval.id)).where(
                FeedbackApproval.requester_id == user.id
            )
            if filters:
                count_query = self._apply_filters(count_query, filters)
            
            total_count = await db.scalar(count_query)
            
            # ページネーション
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(
                desc(FeedbackApproval.requested_at)
            )
            
            # 関連データをロード
            query = query.options(
                selectinload(FeedbackApproval.analysis),
                selectinload(FeedbackApproval.reviewer)
            )
            
            result = await db.execute(query)
            approvals = result.scalars().all()
            
            return approvals, total_count
            
        except Exception as e:
            logger.error(f"ユーザーの承認リクエスト取得に失敗: {e}")
            raise

    async def get_pending_approvals(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[FeedbackApproval], int]:
        """レビュー待ちの承認リクエスト一覧を取得（レビュアー用）"""
        try:
            # ユーザーがレビュアーになれる権限があるかチェック
            if not await self._can_review_approvals(user):
                raise PermissionException("承認のレビュー権限がありません")
            
            # レビュー待ちの承認リクエストを取得
            query = select(FeedbackApproval).where(
                FeedbackApproval.approval_status == ApprovalStatus.PENDING
            )
            
            # 総件数を取得
            total_count = await db.scalar(
                select(func.count(FeedbackApproval.id)).where(
                    FeedbackApproval.approval_status == ApprovalStatus.PENDING
                )
            )
            
            # ページネーション
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(
                FeedbackApproval.requested_at
            )
            
            # 関連データをロード
            query = query.options(
                selectinload(FeedbackApproval.analysis),
                selectinload(FeedbackApproval.requester)
            )
            
            result = await db.execute(query)
            approvals = result.scalars().all()
            
            return approvals, total_count
            
        except Exception as e:
            logger.error(f"レビュー待ちの承認リクエスト取得に失敗: {e}")
            raise

    async def review_approval(
        self,
        db: AsyncSession,
        user: User,
        approval_id: int,
        review_data: FeedbackApprovalUpdate
    ) -> FeedbackApproval:
        """承認リクエストをレビュー"""
        try:
            # 承認リクエストの存在確認
            approval = await self._get_approval(db, approval_id)
            
            # 権限チェック
            if not await self._can_review_approval(user, approval):
                raise PermissionException("この承認リクエストをレビューする権限がありません")
            
            # レビュー開始
            if approval.approval_status == ApprovalStatus.PENDING:
                approval.start_review(user.id)
            
            # レビュー結果の適用
            if review_data.approval_status:
                if review_data.approval_status == ApprovalStatus.APPROVED:
                    approval.approve(review_data.review_notes)
                elif review_data.approval_status == ApprovalStatus.REJECTED:
                    approval.reject(review_data.rejection_reason)
                elif review_data.approval_status == ApprovalStatus.REQUIRES_CHANGES:
                    approval.request_changes(review_data.review_notes)
            
            # 可視性レベルの更新
            if review_data.visibility_level:
                approval.visibility_level = review_data.visibility_level
            
            # 変更を保存
            await db.commit()
            await db.refresh(approval)
            
            logger.info(
                "承認リクエストをレビュー",
                approval_id=approval_id,
                reviewer_id=user.id,
                status=approval.approval_status
            )
            
            return approval
            
        except Exception as e:
            await db.rollback()
            logger.error(f"承認リクエストのレビューに失敗: {e}")
            raise

    async def confirm_by_user(
        self,
        db: AsyncSession,
        user: User,
        confirmation_data: UserConfirmationRequest
    ) -> FeedbackApproval:
        """本人確認を実行"""
        try:
            # 承認リクエストの存在確認
            approval = await self._get_approval(db, confirmation_data.approval_id)
            
            # 権限チェック（申請者本人かチェック）
            if approval.requester_id != user.id:
                raise PermissionException("申請者本人のみが確認できます")
            
            # 確認処理
            if confirmation_data.confirm:
                approval.confirm_by_user()
                logger.info(
                    "本人確認完了",
                    approval_id=approval.id,
                    user_id=user.id
                )
            else:
                # 確認を拒否した場合、承認リクエストを削除
                await db.delete(approval)
                await db.commit()
                logger.info(
                    "本人確認拒否、承認リクエストを削除",
                    approval_id=approval.id,
                    user_id=user.id
                )
                return None
            
            # 変更を保存
            await db.commit()
            await db.refresh(approval)
            
            return approval
            
        except Exception as e:
            await db.rollback()
            logger.error(f"本人確認に失敗: {e}")
            raise

    async def publish_approved_analysis(
        self,
        db: AsyncSession,
        approval_id: int
    ) -> bool:
        """承認済みの分析結果を公開"""
        try:
            # 承認リクエストの存在確認
            approval = await self._get_approval(db, approval_id)
            
            # 公開可能かチェック
            if not approval.can_be_published:
                raise BusinessLogicException("公開条件を満たしていません")
            
            # 分析結果を公開
            analysis = approval.analysis
            analysis.is_public = True
            analysis.visibility_level = approval.visibility_level.value
            
            # 承認リクエストを公開済みとしてマーク
            approval.publish()
            
            # 変更を保存
            await db.commit()
            
            logger.info(
                "分析結果を公開",
                approval_id=approval_id,
                analysis_id=approval.analysis_id
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"分析結果の公開に失敗: {e}")
            raise

    async def advance_publication_stage(
        self,
        db: AsyncSession,
        approval_id: int
    ) -> bool:
        """段階的公開の次の段階に進む"""
        try:
            # 承認リクエストの存在確認
            approval = await self._get_approval(db, approval_id)
            
            # 段階的公開が有効かチェック
            if not approval.is_staged_publication:
                raise BusinessLogicException("段階的公開が設定されていません")
            
            # 次の段階に進む
            approval.advance_stage()
            
            # 変更を保存
            await db.commit()
            
            logger.info(
                "段階的公開の次の段階に進行",
                approval_id=approval_id,
                current_stage=approval.current_stage
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"段階的公開の進行に失敗: {e}")
            raise

    async def get_approval_stats(
        self,
        db: AsyncSession,
        user: User
    ) -> FeedbackApprovalStats:
        """承認統計を取得"""
        try:
            # ユーザーがアクセスできる承認リクエストの統計を取得
            if await self._can_review_approvals(user):
                # レビュアー権限がある場合、全体の統計
                total_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id))
                )
                pending_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.approval_status == ApprovalStatus.PENDING
                    )
                )
                approved_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.approval_status == ApprovalStatus.APPROVED
                    )
                )
                rejected_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.approval_status == ApprovalStatus.REJECTED
                    )
                )
                under_review_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.approval_status == ApprovalStatus.UNDER_REVIEW
                    )
                )
                requires_changes_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.approval_status == ApprovalStatus.REQUIRES_CHANGES
                    )
                )
            else:
                # 一般ユーザーの場合、自分の承認リクエストの統計
                total_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        FeedbackApproval.requester_id == user.id
                    )
                )
                pending_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        and_(
                            FeedbackApproval.requester_id == user.id,
                            FeedbackApproval.approval_status == ApprovalStatus.PENDING
                        )
                    )
                )
                approved_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        and_(
                            FeedbackApproval.requester_id == user.id,
                            FeedbackApproval.approval_status == ApprovalStatus.APPROVED
                        )
                    )
                )
                rejected_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        and_(
                            FeedbackApproval.requester_id == user.id,
                            FeedbackApproval.approval_status == ApprovalStatus.REJECTED
                        )
                    )
                )
                under_review_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        and_(
                            FeedbackApproval.requester_id == user.id,
                            FeedbackApproval.approval_status == ApprovalStatus.UNDER_REVIEW
                        )
                    )
                )
                requires_changes_approvals = await db.scalar(
                    select(func.count(FeedbackApproval.id)).where(
                        and_(
                            FeedbackApproval.requester_id == user.id,
                            FeedbackApproval.approval_status == ApprovalStatus.REQUIRES_CHANGES
                        )
                    )
                )
            
            # 承認率を計算
            approval_rate = 0.0
            if total_approvals > 0:
                approval_rate = approved_approvals / total_approvals
            
            # 平均承認時間を計算（承認済みのもののみ）
            if approved_approvals > 0:
                avg_time_result = await db.execute(
                    select(
                        func.avg(
                            func.extract('epoch', 
                                FeedbackApproval.reviewed_at - FeedbackApproval.requested_at
                            ) / 3600
                        )
                    ).where(
                        and_(
                            FeedbackApproval.approval_status == ApprovalStatus.APPROVED,
                            FeedbackApproval.reviewed_at.isnot(None)
                        )
                    )
                )
                average_approval_time_hours = avg_time_result.scalar() or 0.0
            else:
                average_approval_time_hours = 0.0
            
            # 可視性レベルの分布
            visibility_distribution = await self._get_visibility_distribution(db, user)
            
            # ステータスの分布
            status_distribution = {
                "pending": pending_approvals,
                "under_review": under_review_approvals,
                "approved": approved_approvals,
                "rejected": rejected_approvals,
                "requires_changes": requires_changes_approvals
            }
            
            return FeedbackApprovalStats(
                total_approvals=total_approvals,
                pending_approvals=pending_approvals,
                approved_approvals=approved_approvals,
                rejected_approvals=rejected_approvals,
                under_review_approvals=under_review_approvals,
                requires_changes_approvals=requires_changes_approvals,
                average_approval_time_hours=average_approval_time_hours,
                approval_rate=approval_rate,
                visibility_distribution=visibility_distribution,
                status_distribution=status_distribution
            )
            
        except Exception as e:
            logger.error(f"承認統計の取得に失敗: {e}")
            raise

    # プライベートメソッド

    async def _get_analysis(self, db: AsyncSession, analysis_id: int) -> Analysis:
        """分析結果を取得"""
        result = await db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise NotFoundException("分析結果が見つかりません")
        return analysis

    async def _get_approval(self, db: AsyncSession, approval_id: int) -> FeedbackApproval:
        """承認リクエストを取得"""
        result = await db.execute(
            select(FeedbackApproval).where(FeedbackApproval.id == approval_id)
        )
        approval = result.scalar_one_or_none()
        if not approval:
            raise NotFoundException("承認リクエストが見つかりません")
        return approval

    async def _get_existing_approval(
        self, db: AsyncSession, analysis_id: int, requester_id: int
    ) -> Optional[FeedbackApproval]:
        """既存の承認リクエストを取得"""
        result = await db.execute(
            select(FeedbackApproval).where(
                and_(
                    FeedbackApproval.analysis_id == analysis_id,
                    FeedbackApproval.requester_id == requester_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def _can_review_approvals(self, user: User) -> bool:
        """承認のレビュー権限があるかチェック"""
        # 管理者またはプレミアムユーザーの場合
        return user.is_admin or user.is_premium_user

    async def _can_review_approval(self, user: User, approval: FeedbackApproval) -> bool:
        """特定の承認リクエストをレビューする権限があるかチェック"""
        # 管理者またはプレミアムユーザーの場合
        return user.is_admin or user.is_premium_user

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """フィルターを適用"""
        if filters.get("analysis_id"):
            query = query.where(FeedbackApproval.analysis_id == filters["analysis_id"])
        if filters.get("approval_status"):
            query = query.where(FeedbackApproval.approval_status == filters["approval_status"])
        if filters.get("visibility_level"):
            query = query.where(FeedbackApproval.visibility_level == filters["visibility_level"])
        if filters.get("is_confirmed") is not None:
            query = query.where(FeedbackApproval.is_confirmed == filters["is_confirmed"])
        return query

    def _serialize_publication_stages(self, stages: List[PublicationStage]) -> str:
        """公開段階をJSON文字列にシリアライズ"""
        stages_data = []
        for stage in stages:
            stages_data.append({
                "stage_number": stage.stage_number,
                "visibility_level": stage.visibility_level.value,
                "description": stage.description,
                "delay_days": stage.delay_days,
                "auto_advance": stage.auto_advance
            })
        return json.dumps(stages_data, ensure_ascii=False)

    async def _get_visibility_distribution(self, db: AsyncSession, user: User) -> Dict[str, int]:
        """可視性レベルの分布を取得"""
        if await self._can_review_approvals(user):
            # 全体の分布
            result = await db.execute(
                select(
                    FeedbackApproval.visibility_level,
                    func.count(FeedbackApproval.id)
                ).group_by(FeedbackApproval.visibility_level)
            )
        else:
            # ユーザー自身の分布
            result = await db.execute(
                select(
                    FeedbackApproval.visibility_level,
                    func.count(FeedbackApproval.id)
                ).where(
                    FeedbackApproval.requester_id == user.id
                ).group_by(FeedbackApproval.visibility_level)
            )
        
        distribution = {}
        for visibility_level, count in result:
            distribution[visibility_level.value] = count
        
        return distribution


# グローバルインスタンス
feedback_approval_service = FeedbackApprovalService()
