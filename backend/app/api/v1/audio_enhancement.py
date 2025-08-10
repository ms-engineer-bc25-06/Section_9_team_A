from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import structlog
from datetime import datetime

from app.services.audio_enhancement_service import (
    audio_enhancement_service, 
    EnhancementType,
    EnhancementResult
)
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.audio_enhancement import (
    AudioEnhancementRequest,
    AudioEnhancementResponse,
    EnhancementStatsResponse,
    EnhancementParameters
)

logger = structlog.get_logger()

router = APIRouter(prefix="/audio-enhancement", tags=["音声品質向上"])


@router.post("/enhance", response_model=AudioEnhancementResponse)
async def enhance_audio(
    audio_file: UploadFile = File(...),
    enhancement_types: Optional[str] = Form(None),
    sample_rate: int = Form(16000),
    current_user: User = Depends(get_current_user)
):
    """
    音声ファイルの品質向上処理
    
    - **enhancement_types**: 適用する品質向上処理（カンマ区切り）
      - noise_reduction: ノイズ除去
      - echo_cancellation: エコーキャンセル
      - gain_control: ゲイン制御
      - spectral_enhancement: スペクトル強調
    - **sample_rate**: サンプリングレート（Hz）
    """
    try:
        # 音声ファイルの検証
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="音声ファイルをアップロードしてください")
        
        # ファイルサイズの制限（10MB）
        if audio_file.size and audio_file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ファイルサイズは10MB以下にしてください")
        
        # 音声データを読み込み
        audio_data = await audio_file.read()
        
        # 品質向上処理の種類を解析
        enhancement_list = []
        if enhancement_types:
            for et in enhancement_types.split(','):
                et = et.strip().lower()
                try:
                    enhancement_list.append(EnhancementType(et))
                except ValueError:
                    logger.warning(f"無効な品質向上処理タイプ: {et}")
        
        # デフォルトの処理を適用
        if not enhancement_list:
            enhancement_list = [EnhancementType.NOISE_REDUCTION, EnhancementType.ECHO_CANCELLATION]
        
        logger.info(
            "音声品質向上処理開始",
            user_id=current_user.id,
            enhancement_types=[et.value for et in enhancement_list],
            sample_rate=sample_rate,
            file_size=len(audio_data)
        )
        
        # 音声品質向上処理を実行
        result = await audio_enhancement_service.enhance_audio(
            audio_data=audio_data,
            sample_rate=sample_rate,
            enhancement_types=enhancement_list
        )
        
        # レスポンスを作成
        response = AudioEnhancementResponse(
            message="音声品質向上処理が完了しました",
            enhancement_types=[et.value for et in enhancement_list],
            quality_metrics=result.quality_metrics,
            processing_time_ms=result.processing_time_ms,
            original_file_size=len(audio_data),
            enhanced_file_size=len(result.enhanced_audio),
            timestamp=result.timestamp
        )
        
        logger.info(
            "音声品質向上処理完了",
            user_id=current_user.id,
            processing_time_ms=result.processing_time_ms,
            quality_metrics=result.quality_metrics
        )
        
        return response
        
    except Exception as e:
        logger.error(f"音声品質向上処理に失敗: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"音声品質向上処理に失敗しました: {str(e)}")


@router.post("/enhance-stream")
async def enhance_audio_stream(
    audio_file: UploadFile = File(...),
    enhancement_types: Optional[str] = Form(None),
    sample_rate: int = Form(16000),
    current_user: User = Depends(get_current_user)
):
    """
    音声ファイルの品質向上処理（ストリーミングレスポンス）
    """
    try:
        # 音声データを読み込み
        audio_data = await audio_file.read()
        
        # 品質向上処理の種類を解析
        enhancement_list = []
        if enhancement_types:
            for et in enhancement_types.split(','):
                et = et.strip().lower()
                try:
                    enhancement_list.append(EnhancementType(et))
                except ValueError:
                    logger.warning(f"無効な品質向上処理タイプ: {et}")
        
        if not enhancement_list:
            enhancement_list = [EnhancementType.NOISE_REDUCTION, EnhancementType.ECHO_CANCELLATION]
        
        # 音声品質向上処理を実行
        result = await audio_enhancement_service.enhance_audio(
            audio_data=audio_data,
            sample_rate=sample_rate,
            enhancement_types=enhancement_list
        )
        
        # ストリーミングレスポンスを作成
        enhanced_audio_io = io.BytesIO(result.enhanced_audio)
        
        return StreamingResponse(
            enhanced_audio_io,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=enhanced_{audio_file.filename}",
                "X-Processing-Time": str(result.processing_time_ms),
                "X-Quality-Metrics": str(result.quality_metrics)
            }
        )
        
    except Exception as e:
        logger.error(f"音声品質向上ストリーミング処理に失敗: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"音声品質向上処理に失敗しました: {str(e)}")


@router.get("/stats", response_model=EnhancementStatsResponse)
async def get_enhancement_stats(
    current_user: User = Depends(get_current_user)
):
    """音声品質向上の統計情報を取得"""
    try:
        stats = audio_enhancement_service.get_enhancement_stats()
        
        response = EnhancementStatsResponse(
            total_processed=stats["total_processed"],
            avg_processing_time_ms=stats["avg_processing_time_ms"],
            avg_snr_improvement=stats["avg_snr_improvement"],
            avg_echo_reduction=stats["avg_echo_reduction"],
            noise_profile_available=stats["noise_profile_available"],
            echo_profile_available=stats["echo_profile_available"],
            timestamp=datetime.now()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"統計情報取得に失敗: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"統計情報の取得に失敗しました: {str(e)}")


@router.post("/parameters")
async def set_enhancement_parameters(
    params: EnhancementParameters,
    current_user: User = Depends(get_current_user)
):
    """音声品質向上パラメータを設定"""
    try:
        # パラメータの検証
        if params.noise_reduction_strength is not None and not (0.1 <= params.noise_reduction_strength <= 5.0):
            raise HTTPException(status_code=400, detail="ノイズ除去強度は0.1から5.0の範囲で指定してください")
        
        if params.echo_cancellation_strength is not None and not (0.1 <= params.echo_cancellation_strength <= 1.0):
            raise HTTPException(status_code=400, detail="エコーキャンセル強度は0.1から1.0の範囲で指定してください")
        
        if params.gain_boost_factor is not None and not (0.5 <= params.gain_boost_factor <= 3.0):
            raise HTTPException(status_code=400, detail="ゲインブースト係数は0.5から3.0の範囲で指定してください")
        
        # パラメータを設定
        audio_enhancement_service.set_enhancement_parameters(
            noise_reduction_strength=params.noise_reduction_strength,
            echo_cancellation_strength=params.echo_cancellation_strength,
            gain_boost_factor=params.gain_boost_factor
        )
        
        logger.info(
            "音声品質向上パラメータを更新",
            user_id=current_user.id,
            parameters=params.dict()
        )
        
        return {"message": "パラメータが正常に更新されました"}
        
    except Exception as e:
        logger.error(f"パラメータ設定に失敗: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"パラメータの設定に失敗しました: {str(e)}")


@router.delete("/history")
async def clear_enhancement_history(
    current_user: User = Depends(get_current_user)
):
    """音声品質向上の処理履歴をクリア"""
    try:
        audio_enhancement_service.clear_history()
        
        logger.info("音声品質向上履歴をクリア", user_id=current_user.id)
        
        return {"message": "処理履歴がクリアされました"}
        
    except Exception as e:
        logger.error(f"履歴クリアに失敗: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"履歴のクリアに失敗しました: {str(e)}")


@router.get("/health")
async def health_check():
    """音声品質向上サービスのヘルスチェック"""
    try:
        stats = audio_enhancement_service.get_enhancement_stats()
        
        return {
            "status": "healthy",
            "service": "audio_enhancement",
            "noise_profile_available": stats["noise_profile_available"],
            "echo_profile_available": stats["echo_profile_available"],
            "total_processed": stats["total_processed"]
        }
        
    except Exception as e:
        logger.error(f"ヘルスチェックに失敗: {e}")
        return {
            "status": "unhealthy",
            "service": "audio_enhancement",
            "error": str(e)
        }
