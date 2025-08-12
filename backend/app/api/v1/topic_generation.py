from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.schemas.topic_generation import (
    TopicGenerationRequest,
    TopicGenerationResponse,
    TopicGenerationListResponse,
    PersonalizedTopicRequest,
    TopicCategory,
    TopicDifficulty
)
from app.services.topic_generation_service import TopicGenerationService
from app.core.exceptions import AnalysisError
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/generate", response_model=TopicGenerationResponse)
async def generate_topics(
    request: TopicGenerationRequest,
    current_user: User = Depends(get_current_user),
    topic_service: TopicGenerationService = Depends()
):
    """会話内容に基づいてトークテーマを生成"""
    try:
        # ユーザーIDを設定
        request.user_id = current_user.id
        
        # トークテーマを生成
        result = await topic_service.generate_topics(request)
        
        return TopicGenerationResponse(
            success=True,
            result=result,
            message="トークテーマの生成が完了しました",
            error_details=None
        )
        
    except AnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"トークテーマ生成中にエラーが発生しました: {str(e)}")

@router.post("/generate/personalized", response_model=TopicGenerationResponse)
async def generate_personalized_topics(
    request: PersonalizedTopicRequest,
    current_user: User = Depends(get_current_user),
    topic_service: TopicGenerationService = Depends()
):
    """参加者の興味・関心に基づいて個別化されたトークテーマを生成"""
    try:
        # ユーザーIDを設定
        request.user_id = current_user.id
        
        # 個別化されたトークテーマを生成
        result = await topic_service.generate_personalized_topics(request)
        
        return TopicGenerationResponse(
            success=True,
            result=result,
            message="個別化されたトークテーマの生成が完了しました",
            error_details=None
        )
        
    except AnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"個別化トークテーマ生成中にエラーが発生しました: {str(e)}")

@router.get("/categories", response_model=List[str])
async def get_topic_categories():
    """利用可能なトークテーマカテゴリを取得"""
    return [category.value for category in TopicCategory]

@router.get("/difficulties", response_model=List[str])
async def get_topic_difficulties():
    """利用可能なトークテーマ難易度を取得"""
    return [difficulty.value for difficulty in TopicDifficulty]

@router.get("/suggestions", response_model=TopicGenerationResponse)
async def get_topic_suggestions(
    category: Optional[TopicCategory] = Query(None, description="カテゴリでフィルタリング"),
    difficulty: Optional[TopicDifficulty] = Query(None, description="難易度でフィルタリング"),
    max_duration: Optional[int] = Query(None, description="最大所要時間（分）"),
    current_user: User = Depends(get_current_user),
    topic_service: TopicGenerationService = Depends()
):
    """条件に基づいてトークテーマの提案を取得"""
    try:
        # 基本的なトークテーマを生成
        request = TopicGenerationRequest(
            text_content="基本的な会話促進のためのトークテーマ生成",
            user_id=current_user.id,
            participant_ids=[current_user.id],
            analysis_types=["personality", "communication"],
            preferred_categories=[category] if category else None,
            max_duration=max_duration,
            difficulty_level=difficulty
        )
        
        result = await topic_service.generate_topics(request)
        
        return TopicGenerationResponse(
            success=True,
            result=result,
            message="トークテーマの提案を取得しました",
            error_details=None
        )
        
    except AnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"トークテーマ提案の取得中にエラーが発生しました: {str(e)}")

@router.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "topic_generation"}
