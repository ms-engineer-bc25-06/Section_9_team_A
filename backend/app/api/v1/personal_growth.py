from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.analysis import (
    ImprovementPlan, ImprovementStep, GrowthGoal, PersonalGrowthProfile,
    AnalysisType
)
from app.services.personal_growth_service import PersonalGrowthService
from app.services.ai_analysis_service import AIAnalysisService
from app.services.privacy_service import PrivacyService
from app.dependencies import get_openai_client
from app.core.exceptions import AnalysisError, PrivacyError, AccessDeniedError

router = APIRouter()
logger = structlog.get_logger()

@router.post("/improvement-plan", response_model=ImprovementPlan)
async def generate_improvement_plan(
    target_skills: Optional[Dict[str, float]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """個人向け改善提案を生成"""
    try:
        openai_client = get_openai_client()
        personal_growth_service = PersonalGrowthService(openai_client)
        ai_analysis_service = AIAnalysisService(openai_client)
        privacy_service = PrivacyService()
        
        # ユーザーの分析結果を取得
        analyses = await ai_analysis_service.get_user_analyses(
            db=db,
            user=current_user,
            page=1,
            page_size=100
        )
        
        if not analyses.get("analyses"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="改善計画を生成するには分析結果が必要です"
            )
        
        # 改善計画を生成
        improvement_plan = await personal_growth_service.generate_improvement_plan(
            db=db,
            user=current_user,
            analysis_results=analyses["analyses"],
            target_skills=target_skills
        )
        
        # 改善計画を暗号化して保存
        encrypted_data = await privacy_service.encrypt_data(
            db=db,
            user=current_user,
            data=improvement_plan.dict(),
            data_type="improvement_plan",
            data_category="improvement",
            privacy_level="private"
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="generate_improvement_plan",
            data_id=encrypted_data.data_id,
            action_details={"plan_id": improvement_plan.id},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "改善計画生成完了",
            user_id=current_user.id,
            plan_id=improvement_plan.id
        )
        
        return improvement_plan
        
    except AnalysisError as e:
        logger.error("改善計画生成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except PrivacyError as e:
        logger.error("プライバシー関連エラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="データの保存に失敗しました"
        )
    except Exception as e:
        logger.error("予期しないエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="改善計画の生成に失敗しました"
        )

@router.get("/improvement-plan/{plan_id}", response_model=ImprovementPlan)
async def get_improvement_plan(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """改善計画を取得"""
    try:
        privacy_service = PrivacyService()
        
        # 暗号化されたデータを検索
        # 実際の実装では、plan_idからEncryptedDataを検索する必要があります
        # ここでは簡易実装
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="access_improvement_plan",
            data_id=plan_id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        # 仮の改善計画を返す（実際の実装では復号化したデータを返す）
        return ImprovementPlan(
            id=plan_id,
            title="サンプル改善計画",
            description="これはサンプルの改善計画です",
            current_level="中級",
            target_level="上級",
            steps=[],
            estimated_duration="3ヶ月",
            priority="medium",
            category="comprehensive"
        )
        
    except Exception as e:
        logger.error("改善計画取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="改善計画の取得に失敗しました"
        )

@router.post("/goals", response_model=GrowthGoal)
async def create_growth_goal(
    title: str,
    description: str,
    category: str,
    target_date: Optional[datetime] = None,
    metrics: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """成長目標を作成"""
    try:
        openai_client = get_openai_client()
        personal_growth_service = PersonalGrowthService(openai_client)
        privacy_service = PrivacyService()
        
        # 成長目標を作成
        goal = await personal_growth_service.create_growth_goal(
            user=current_user,
            title=title,
            description=description,
            category=category,
            target_date=target_date,
            metrics=metrics
        )
        
        # 目標を暗号化して保存
        encrypted_data = await privacy_service.encrypt_data(
            db=db,
            user=current_user,
            data=goal.dict(),
            data_type="growth_goal",
            data_category="goals",
            privacy_level="private"
        )
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="create_growth_goal",
            data_id=encrypted_data.data_id,
            action_details={"goal_id": goal.id, "title": title},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "成長目標作成完了",
            user_id=current_user.id,
            goal_id=goal.id,
            title=title
        )
        
        return goal
        
    except Exception as e:
        logger.error("成長目標作成でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="成長目標の作成に失敗しました"
        )

@router.put("/goals/{goal_id}/progress")
async def update_goal_progress(
    goal_id: str,
    progress: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """目標の進捗を更新"""
    try:
        openai_client = get_openai_client()
        personal_growth_service = PersonalGrowthService(openai_client)
        privacy_service = PrivacyService()
        
        # 仮の目標オブジェクト（実際の実装では復号化したデータを使用）
        goal = GrowthGoal(
            id=goal_id,
            title="サンプル目標",
            description="サンプル説明",
            category="general",
            progress=progress
        )
        
        # 進捗を更新
        updated_goal = await personal_growth_service.update_goal_progress(goal, progress)
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="update_goal_progress",
            data_id=goal_id,
            action_details={"old_progress": goal.progress, "new_progress": progress},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        logger.info(
            "目標進捗更新完了",
            user_id=current_user.id,
            goal_id=goal_id,
            progress=progress
        )
        
        return {"message": "進捗が更新されました", "progress": progress}
        
    except Exception as e:
        logger.error("目標進捗更新でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="進捗の更新に失敗しました"
        )

@router.get("/goals", response_model=List[GrowthGoal])
async def get_growth_goals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """ユーザーの成長目標一覧を取得"""
    try:
        privacy_service = PrivacyService()
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="list_growth_goals",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        # 仮の目標リストを返す（実際の実装では復号化したデータを返す）
        return [
            GrowthGoal(
                id="1",
                title="コミュニケーション能力向上",
                description="チーム内でのコミュニケーションを改善する",
                category="communication",
                progress=0.6,
                status="active"
            ),
            GrowthGoal(
                id="2",
                title="リーダーシップスキル開発",
                description="プロジェクトリーダーとしての能力を身につける",
                category="leadership",
                progress=0.3,
                status="active"
            )
        ]
        
    except Exception as e:
        logger.error("成長目標一覧取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="成長目標の取得に失敗しました"
        )

@router.get("/profile", response_model=PersonalGrowthProfile)
async def get_personal_growth_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """個人成長プロフィールを取得"""
    try:
        privacy_service = PrivacyService()
        
        # 監査ログに記録
        await privacy_service.log_privacy_action(
            db=db,
            user=current_user,
            action="access_growth_profile",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        # 仮のプロフィールを返す（実際の実装では復号化したデータを返す）
        return PersonalGrowthProfile(
            user_id=current_user.id,
            current_skills={
                "communication": 3.2,
                "leadership": 2.8,
                "technical": 4.1
            },
            target_skills={
                "communication": 4.0,
                "leadership": 3.5,
                "technical": 4.5
            },
            improvement_plans=[],
            growth_goals=[],
            learning_history=[]
        )
        
    except Exception as e:
        logger.error("成長プロフィール取得でエラー", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="成長プロフィールの取得に失敗しました"
        )
