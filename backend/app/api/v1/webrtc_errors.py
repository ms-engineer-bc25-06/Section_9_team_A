"""
WebRTCエラーハンドリングAPI
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.webrtc_error_handler import (
    webrtc_error_handler, 
    WebRTCErrorType, 
    ErrorSeverity
)
from app.core.exceptions import BridgeLineException

router = APIRouter()
logger = structlog.get_logger()


@router.post("/webrtc/errors/record")
async def record_webrtc_error(
    error_type: str,
    severity: str,
    peer_id: str,
    session_id: str,
    error_message: str,
    error_code: Optional[str] = None,
    stack_trace: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """WebRTCエラーを記録"""
    try:
        # エラータイプと重要度を検証
        try:
            error_type_enum = WebRTCErrorType(error_type)
            severity_enum = ErrorSeverity(severity)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無効なエラータイプまたは重要度: {e}"
            )
        
        # エラーを記録
        error = webrtc_error_handler.record_error(
            error_type=error_type_enum,
            severity=severity_enum,
            peer_id=peer_id,
            session_id=session_id,
            error_message=error_message,
            error_code=error_code,
            stack_trace=stack_trace,
            context=context
        )
        
        logger.info(
            "WebRTCエラーを記録",
            user_id=current_user.id,
            peer_id=peer_id,
            session_id=session_id,
            error_type=error_type,
            severity=severity,
            error_id=error.error_id
        )
        
        return {
            "success": True,
            "error": error.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WebRTCエラー記録エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebRTCエラーの記録に失敗しました"
        )


@router.get("/webrtc/errors/peer/{peer_id}")
async def get_peer_errors(
    peer_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """ピアのエラー履歴を取得"""
    try:
        errors = webrtc_error_handler.get_peer_errors(peer_id, limit)
        
        logger.info(
            "ピアエラー履歴を取得",
            user_id=current_user.id,
            peer_id=peer_id,
            errors_count=len(errors)
        )
        
        return {
            "success": True,
            "peer_id": peer_id,
            "errors": [error.to_dict() for error in errors]
        }
        
    except Exception as e:
        logger.error(f"ピアエラー履歴取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ピアエラー履歴の取得に失敗しました"
        )


@router.get("/webrtc/errors/session/{session_id}")
async def get_session_errors(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """セッションのエラー履歴を取得"""
    try:
        errors = webrtc_error_handler.get_session_errors(session_id, limit)
        
        logger.info(
            "セッションエラー履歴を取得",
            user_id=current_user.id,
            session_id=session_id,
            errors_count=len(errors)
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "errors": [error.to_dict() for error in errors]
        }
        
    except Exception as e:
        logger.error(f"セッションエラー履歴取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="セッションエラー履歴の取得に失敗しました"
        )


@router.get("/webrtc/errors/peer/{peer_id}/summary")
async def get_peer_error_summary(
    peer_id: str,
    duration_minutes: int = Query(5, ge=1, le=60),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """ピアのエラーサマリーを取得"""
    try:
        summary = webrtc_error_handler.get_error_summary(peer_id, duration_minutes)
        
        logger.info(
            "ピアエラーサマリーを取得",
            user_id=current_user.id,
            peer_id=peer_id,
            duration_minutes=duration_minutes,
            total_errors=summary["total_errors"]
        )
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"ピアエラーサマリー取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ピアエラーサマリーの取得に失敗しました"
        )


@router.get("/webrtc/errors/peer/{peer_id}/thresholds")
async def check_error_thresholds(
    peer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """エラー閾値をチェック"""
    try:
        violations = webrtc_error_handler.check_error_thresholds(peer_id)
        
        logger.info(
            "エラー閾値チェック",
            user_id=current_user.id,
            peer_id=peer_id,
            violations_count=len(violations)
        )
        
        return {
            "success": True,
            "peer_id": peer_id,
            "threshold_violations": violations,
            "has_violations": len(violations) > 0
        }
        
    except Exception as e:
        logger.error(f"エラー閾値チェックエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="エラー閾値チェックに失敗しました"
        )


@router.get("/webrtc/errors/types")
async def get_error_types(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """エラータイプ一覧を取得"""
    try:
        error_types = [
            {
                "type": error_type.value,
                "description": _get_error_type_description(error_type)
            }
            for error_type in WebRTCErrorType
        ]
        
        severities = [
            {
                "severity": severity.value,
                "description": _get_severity_description(severity)
            }
            for severity in ErrorSeverity
        ]
        
        logger.info(
            "エラータイプ一覧を取得",
            user_id=current_user.id,
            error_types_count=len(error_types),
            severities_count=len(severities)
        )
        
        return {
            "success": True,
            "error_types": error_types,
            "severities": severities
        }
        
    except Exception as e:
        logger.error(f"エラータイプ一覧取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="エラータイプ一覧の取得に失敗しました"
        )


@router.post("/webrtc/errors/cleanup")
async def cleanup_errors(
    hours: int = Query(24, ge=1, le=168),  # 1時間〜1週間
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """古いエラーをクリーンアップ"""
    try:
        # クリーンアップ前の状態を記録
        before_peers = len(webrtc_error_handler.error_history)
        before_errors = sum(len(errors) for errors in webrtc_error_handler.error_history.values())
        
        # クリーンアップを実行
        webrtc_error_handler.cleanup_old_errors(hours)
        
        # クリーンアップ後の状態を記録
        after_peers = len(webrtc_error_handler.error_history)
        after_errors = sum(len(errors) for errors in webrtc_error_handler.error_history.values())
        
        cleanup_result = {
            "cleanup_hours": hours,
            "before_peers": before_peers,
            "after_peers": after_peers,
            "before_errors": before_errors,
            "after_errors": after_errors,
            "errors_removed": before_errors - after_errors,
            "peers_removed": before_peers - after_peers
        }
        
        logger.info(
            "エラークリーンアップ実行",
            user_id=current_user.id,
            cleanup_result=cleanup_result
        )
        
        return {
            "success": True,
            "cleanup_result": cleanup_result
        }
        
    except Exception as e:
        logger.error(f"エラークリーンアップエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="エラーのクリーンアップに失敗しました"
        )


@router.get("/webrtc/errors/health")
async def get_error_handling_health(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """エラーハンドリングシステムのヘルスステータスを取得"""
    try:
        # システムの状態をチェック
        total_peers = len(webrtc_error_handler.error_history)
        total_errors = sum(len(errors) for errors in webrtc_error_handler.error_history.values())
        
        # 最近のエラーをチェック（過去1時間）
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)
        recent_errors = 0
        critical_errors = 0
        
        for peer_errors in webrtc_error_handler.error_history.values():
            for error in peer_errors:
                if error.timestamp >= recent_cutoff:
                    recent_errors += 1
                    if error.severity == ErrorSeverity.CRITICAL:
                        critical_errors += 1
        
        # 閾値違反をチェック
        threshold_violations = 0
        for peer_id in webrtc_error_handler.error_history.keys():
            violations = webrtc_error_handler.check_error_thresholds(peer_id)
            threshold_violations += len(violations)
        
        health_status = {
            "system_status": "healthy",
            "total_peers_with_errors": total_peers,
            "total_errors_stored": total_errors,
            "recent_errors_count": recent_errors,
            "critical_errors_count": critical_errors,
            "threshold_violations": threshold_violations,
            "error_handling_active": True,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # システムの状態を評価
        if critical_errors > 0:
            health_status["system_status"] = "critical"
            health_status["warning"] = f"重大なエラーが{critical_errors}件発生しています。"
        elif threshold_violations > 0:
            health_status["system_status"] = "warning"
            health_status["warning"] = f"エラー閾値違反が{threshold_violations}件発生しています。"
        elif total_errors > 1000:  # エラーが多すぎる場合
            health_status["system_status"] = "warning"
            health_status["warning"] = "エラー数が多すぎます。クリーンアップを推奨します。"
        
        logger.info(
            "エラーハンドリングシステムヘルスチェック",
            user_id=current_user.id,
            system_status=health_status["system_status"],
            total_peers=total_peers,
            total_errors=total_errors,
            critical_errors=critical_errors
        )
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        logger.error(f"エラーハンドリングシステムヘルスチェックエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="エラーハンドリングシステムのヘルスチェックに失敗しました"
        )


def _get_error_type_description(error_type: WebRTCErrorType) -> str:
    """エラータイプの説明を取得"""
    descriptions = {
        WebRTCErrorType.CONNECTION_FAILED: "接続に失敗しました",
        WebRTCErrorType.ICE_GATHERING_FAILED: "ICE gatheringに失敗しました",
        WebRTCErrorType.ICE_CONNECTION_FAILED: "ICE接続に失敗しました",
        WebRTCErrorType.SIGNALING_ERROR: "シグナリングエラーが発生しました",
        WebRTCErrorType.MEDIA_ACCESS_ERROR: "メディアアクセスエラーが発生しました",
        WebRTCErrorType.NETWORK_ERROR: "ネットワークエラーが発生しました",
        WebRTCErrorType.PERMISSION_ERROR: "権限エラーが発生しました",
        WebRTCErrorType.CONFIGURATION_ERROR: "設定エラーが発生しました",
        WebRTCErrorType.TIMEOUT_ERROR: "タイムアウトエラーが発生しました",
        WebRTCErrorType.UNKNOWN_ERROR: "不明なエラーが発生しました",
    }
    return descriptions.get(error_type, "不明なエラー")


def _get_severity_description(severity: ErrorSeverity) -> str:
    """重要度の説明を取得"""
    descriptions = {
        ErrorSeverity.LOW: "低 - 軽微な問題",
        ErrorSeverity.MEDIUM: "中 - 注意が必要",
        ErrorSeverity.HIGH: "高 - 重要な問題",
        ErrorSeverity.CRITICAL: "重大 - 緊急対応が必要",
    }
    return descriptions.get(severity, "不明")
