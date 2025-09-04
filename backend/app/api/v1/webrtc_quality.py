"""
WebRTC品質監視API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.webrtc_quality_monitor import webrtc_quality_monitor, QualityMetrics
from app.core.exceptions import BridgeLineException

router = APIRouter()
logger = structlog.get_logger()


@router.post("/webrtc/quality/metrics")
async def record_quality_metrics(
    peer_id: str,
    session_id: str,
    metrics_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """品質メトリクスを記録"""
    try:
        # メトリクスを記録
        metrics = webrtc_quality_monitor.record_metrics(peer_id, session_id, metrics_data)
        
        logger.info(
            "品質メトリクスを記録",
            user_id=current_user.id,
            peer_id=peer_id,
            session_id=session_id,
            quality=metrics.overall_quality.value,
            score=metrics.quality_score
        )
        
        return {
            "success": True,
            "metrics": metrics.to_dict()
        }
        
    except Exception as e:
        logger.error(f"品質メトリクス記録エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="品質メトリクスの記録に失敗しました"
        )


@router.get("/webrtc/quality/peer/{peer_id}")
async def get_peer_quality_metrics(
    peer_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """ピアの品質メトリクスを取得"""
    try:
        metrics = webrtc_quality_monitor.get_peer_metrics(peer_id, limit)
        
        logger.info(
            "ピア品質メトリクスを取得",
            user_id=current_user.id,
            peer_id=peer_id,
            metrics_count=len(metrics)
        )
        
        return {
            "success": True,
            "peer_id": peer_id,
            "metrics": [m.to_dict() for m in metrics]
        }
        
    except Exception as e:
        logger.error(f"ピア品質メトリクス取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ピア品質メトリクスの取得に失敗しました"
        )


@router.get("/webrtc/quality/session/{session_id}")
async def get_session_quality_metrics(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """セッションの品質メトリクスを取得"""
    try:
        metrics = webrtc_quality_monitor.get_session_metrics(session_id, limit)
        
        logger.info(
            "セッション品質メトリクスを取得",
            user_id=current_user.id,
            session_id=session_id,
            metrics_count=len(metrics)
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "metrics": [m.to_dict() for m in metrics]
        }
        
    except Exception as e:
        logger.error(f"セッション品質メトリクス取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッション品質メトリクスの取得に失敗しました"
        )


@router.get("/webrtc/quality/peer/{peer_id}/summary")
async def get_peer_quality_summary(
    peer_id: str,
    duration_minutes: int = Query(5, ge=1, le=60),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """ピアの品質サマリーを取得"""
    try:
        summary = webrtc_quality_monitor.get_quality_summary(peer_id, duration_minutes)
        
        logger.info(
            "ピア品質サマリーを取得",
            user_id=current_user.id,
            peer_id=peer_id,
            duration_minutes=duration_minutes,
            total_samples=summary["total_samples"]
        )
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"ピア品質サマリー取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ピア品質サマリーの取得に失敗しました"
        )


@router.get("/webrtc/quality/session/{session_id}/summary")
async def get_session_quality_summary(
    session_id: str,
    duration_minutes: int = Query(5, ge=1, le=60),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """セッションの品質サマリーを取得"""
    try:
        summary = webrtc_quality_monitor.get_session_quality_summary(session_id, duration_minutes)
        
        logger.info(
            "セッション品質サマリーを取得",
            user_id=current_user.id,
            session_id=session_id,
            duration_minutes=duration_minutes,
            total_peers=summary["total_peers"],
            total_samples=summary["total_samples"]
        )
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"セッション品質サマリー取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッション品質サマリーの取得に失敗しました"
        )


@router.get("/webrtc/quality/health")
async def get_quality_health_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """品質監視システムのヘルスステータスを取得"""
    try:
        # システムの状態をチェック
        total_peers = len(webrtc_quality_monitor.metrics_history)
        total_metrics = sum(len(metrics) for metrics in webrtc_quality_monitor.metrics_history.values())
        
        # 最近のメトリクスをチェック（過去5分）
        recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
        recent_metrics = 0
        
        for peer_metrics in webrtc_quality_monitor.metrics_history.values():
            recent_metrics += sum(1 for m in peer_metrics if m.timestamp >= recent_cutoff)
        
        health_status = {
            "system_status": "healthy",
            "total_peers_monitored": total_peers,
            "total_metrics_stored": total_metrics,
            "recent_metrics_count": recent_metrics,
            "monitoring_active": True,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # システムの状態を評価
        if total_metrics > 10000:  # メトリクスが多すぎる場合
            health_status["system_status"] = "warning"
            health_status["warning"] = "メトリクス数が多すぎます。クリーンアップを推奨します。"
        elif recent_metrics == 0 and total_peers > 0:  # 最近のメトリクスがない場合
            health_status["system_status"] = "warning"
            health_status["warning"] = "最近のメトリクスがありません。"
        
        logger.info(
            "品質監視システムヘルスチェック",
            user_id=current_user.id,
            system_status=health_status["system_status"],
            total_peers=total_peers,
            total_metrics=total_metrics
        )
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        logger.error(f"品質監視システムヘルスチェックエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="品質監視システムのヘルスチェックに失敗しました"
        )


@router.post("/webrtc/quality/cleanup")
async def cleanup_quality_metrics(
    hours: int = Query(24, ge=1, le=168),  # 1時間〜1週間
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """古い品質メトリクスをクリーンアップ"""
    try:
        # クリーンアップ前の状態を記録
        before_peers = len(webrtc_quality_monitor.metrics_history)
        before_metrics = sum(len(metrics) for metrics in webrtc_quality_monitor.metrics_history.values())
        
        # クリーンアップを実行
        webrtc_quality_monitor.cleanup_old_metrics(hours)
        
        # クリーンアップ後の状態を記録
        after_peers = len(webrtc_quality_monitor.metrics_history)
        after_metrics = sum(len(metrics) for metrics in webrtc_quality_monitor.metrics_history.values())
        
        cleanup_result = {
            "cleanup_hours": hours,
            "before_peers": before_peers,
            "after_peers": after_peers,
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "metrics_removed": before_metrics - after_metrics,
            "peers_removed": before_peers - after_peers
        }
        
        logger.info(
            "品質メトリクスクリーンアップ実行",
            user_id=current_user.id,
            cleanup_result=cleanup_result
        )
        
        return {
            "success": True,
            "cleanup_result": cleanup_result
        }
        
    except Exception as e:
        logger.error(f"品質メトリクスクリーンアップエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="品質メトリクスのクリーンアップに失敗しました"
        )
