from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.api.deps import get_current_user, get_db
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisUpdate,
    AnalysisResponse,
    AnalysisListResponse,
    AnalysisQueryParams,
    SentimentAnalysisRequest,
    SentimentAnalysisResponse,
    TopicAnalysisRequest,
    TopicAnalysisResponse,
)
from app.models.user import User
from app.models.analysis import Analysis
from app.repositories.analysis_repository import analysis_repository

logger = structlog.get_logger()

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    analysis: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析を作成"""
    try:
        # 基本的なバリデーション
        if not analysis.content.strip():
            raise HTTPException(status_code=400, detail="分析対象のコンテンツは必須です")
        
        # 分析IDの生成（UUIDベース）
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # データベースに保存
        db_analysis = await analysis_repository.create(
            db=db,
            obj_in=analysis,
            analysis_id=analysis_id,
        )
        
        logger.info(
            "Analysis created",
            analysis_id=db_analysis.id,
            analysis_type=analysis.analysis_type,
            user_id=current_user.id,
        )
        
        return db_analysis
        
    except Exception as e:
        logger.error(f"Failed to create analysis: {e}")
        raise HTTPException(status_code=500, detail="分析の作成に失敗しました")


@router.get("/", response_model=AnalysisListResponse)
async def list_analyses(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(20, ge=1, le=100, description="ページサイズ"),
    analysis_type: Optional[str] = Query(None, description="分析タイプ"),
    user_id: Optional[int] = Query(None, description="ユーザーID"),
    voice_session_id: Optional[int] = Query(None, description="音声セッションID"),
    transcription_id: Optional[int] = Query(None, description="文字起こしID"),
    status: Optional[str] = Query(None, description="ステータス"),
    sentiment_label: Optional[str] = Query(None, description="感情ラベル"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析一覧を取得"""
    try:
        # クエリパラメータの構築
        query_params = AnalysisQueryParams(
            page=page,
            size=size,
            analysis_type=analysis_type,
            user_id=user_id,
            voice_session_id=voice_session_id,
            transcription_id=transcription_id,
            status=status,
            sentiment_label=sentiment_label,
        )
        
        # データベースから取得
        analyses, total = await analysis_repository.get_multi(
            db=db,
            query_params=query_params,
        )
        
        return AnalysisListResponse(
            analyses=analyses,
            total=total,
            page=page,
            size=size,
        )
        
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(status_code=500, detail="分析一覧の取得に失敗しました")


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """特定の分析を取得"""
    try:
        analysis = await analysis_repository.get(db=db, id=analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="分析が見つかりません")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="分析の取得に失敗しました")


@router.put("/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: int,
    analysis_update: AnalysisUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析を更新"""
    try:
        # 既存の分析を取得
        existing_analysis = await analysis_repository.get(db=db, id=analysis_id)
        if not existing_analysis:
            raise HTTPException(status_code=404, detail="分析が見つかりません")
        
        # 権限チェック（自分の分析または管理者のみ）
        if existing_analysis.user_id != current_user.id:
            # TODO: 管理者権限チェックを追加
            raise HTTPException(status_code=403, detail="この分析を更新する権限がありません")
        
        # 更新
        updated_analysis = await analysis_repository.update(
            db=db,
            db_obj=existing_analysis,
            obj_in=analysis_update,
        )
        
        logger.info(
            "Analysis updated",
            analysis_id=analysis_id,
            user_id=current_user.id,
        )
        
        return updated_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="分析の更新に失敗しました")


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析を削除"""
    try:
        # 既存の分析を取得
        existing_analysis = await analysis_repository.get(db=db, id=analysis_id)
        if not existing_analysis:
            raise HTTPException(status_code=404, detail="分析が見つかりません")
        
        # 権限チェック（自分の分析または管理者のみ）
        if existing_analysis.user_id != current_user.id:
            # TODO: 管理者権限チェックを追加
            raise HTTPException(status_code=403, detail="この分析を削除する権限がありません")
        
        # 削除
        await analysis_repository.remove(db=db, id=analysis_id)
        
        logger.info(
            "Analysis deleted",
            analysis_id=analysis_id,
            user_id=current_user.id,
        )
        
        return {"message": "分析が削除されました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="分析の削除に失敗しました")


@router.post("/sentiment", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """感情分析を実行"""
    try:
        # 基本的なバリデーション
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="分析対象のテキストは必須です")
        
        # TODO: 実際のAI感情分析APIを呼び出し
        # 現在はダミーデータを返す
        import random
        
        # ダミーの感情分析結果
        sentiment_score = random.uniform(-1.0, 1.0)
        if sentiment_score >= 0.1:
            sentiment_label = "positive"
        elif sentiment_score <= -0.1:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        confidence = random.uniform(0.7, 1.0)
        
        # 確率の計算（合計が1.0になるように調整）
        if sentiment_label == "positive":
            positive_prob = confidence
            negative_prob = (1.0 - confidence) * 0.3
            neutral_prob = (1.0 - confidence) * 0.7
        elif sentiment_label == "negative":
            positive_prob = (1.0 - confidence) * 0.3
            negative_prob = confidence
            neutral_prob = (1.0 - confidence) * 0.7
        else:
            positive_prob = (1.0 - confidence) * 0.3
            negative_prob = (1.0 - confidence) * 0.3
            neutral_prob = confidence
        
        return SentimentAnalysisResponse(
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
            positive_probability=positive_prob,
            negative_probability=negative_prob,
            neutral_probability=neutral_prob,
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        raise HTTPException(status_code=500, detail="感情分析の実行に失敗しました")


@router.post("/topics", response_model=TopicAnalysisResponse)
async def analyze_topics(
    request: TopicAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """トピック分析を実行"""
    try:
        # 基本的なバリデーション
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="分析対象のテキストは必須です")
        
        # TODO: 実際のAIトピック分析APIを呼び出し
        # 現在はダミーデータを返す
        import random
        
        # ダミーのトピック分析結果
        topics = []
        for i in range(min(request.num_topics, 5)):
            topics.append({
                "id": i + 1,
                "name": f"トピック{i + 1}",
                "weight": random.uniform(0.1, 1.0),
                "description": f"これはサンプルトピック{i + 1}の説明です。"
            })
        
        # ダミーのキーワード
        keywords = [f"キーワード{i + 1}" for i in range(min(request.num_topics, 5))]
        
        confidence = random.uniform(0.7, 1.0)
        
        return TopicAnalysisResponse(
            topics=topics,
            keywords=keywords,
            confidence=confidence,
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze topics: {e}")
        raise HTTPException(status_code=500, detail="トピック分析の実行に失敗しました")
