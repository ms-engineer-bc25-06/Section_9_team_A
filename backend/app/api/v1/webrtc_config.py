"""
WebRTC設定API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.webrtc_config_service import webrtc_config_service
from app.core.exceptions import BridgeLineException

router = APIRouter()
logger = structlog.get_logger()


@router.get("/webrtc/config")
async def get_webrtc_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """WebRTC設定を取得"""
    try:
        config = webrtc_config_service.get_configuration_for_client()
        
        logger.info(
            "WebRTC設定を取得",
            user_id=current_user.id,
            stun_servers=len(config["rtcConfiguration"]["iceServers"]),
            turn_available=config["environment"]["turn_available"]
        )
        
        return {
            "success": True,
            "config": config,
            "timestamp": "2024-01-01T00:00:00Z"  # 実際の実装では現在時刻を使用
        }
        
    except Exception as e:
        logger.error(f"WebRTC設定取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebRTC設定の取得に失敗しました"
        )


@router.get("/webrtc/ice-servers")
async def get_ice_servers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """ICEサーバー設定を取得"""
    try:
        ice_servers = webrtc_config_service.get_ice_servers()
        
        logger.info(
            "ICEサーバー設定を取得",
            user_id=current_user.id,
            servers_count=len(ice_servers)
        )
        
        return {
            "success": True,
            "iceServers": ice_servers
        }
        
    except Exception as e:
        logger.error(f"ICEサーバー設定取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ICEサーバー設定の取得に失敗しました"
        )


@router.get("/webrtc/environment")
async def get_webrtc_environment(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """WebRTC環境情報を取得"""
    try:
        environment_info = webrtc_config_service.get_environment_info()
        
        logger.info(
            "WebRTC環境情報を取得",
            user_id=current_user.id,
            environment=environment_info["environment"]
        )
        
        return {
            "success": True,
            "environment": environment_info
        }
        
    except Exception as e:
        logger.error(f"WebRTC環境情報取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebRTC環境情報の取得に失敗しました"
        )


@router.post("/webrtc/test-connection")
async def test_webrtc_connection(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """WebRTC接続テスト（簡易版）"""
    try:
        # 設定の検証
        config = webrtc_config_service.get_rtc_configuration()
        ice_servers = webrtc_config_service.get_ice_servers()
        
        # 基本的な設定チェック
        test_results = {
            "stun_servers_configured": len(webrtc_config_service.stun_servers) > 0,
            "turn_servers_configured": webrtc_config_service.is_turn_available(),
            "ice_servers_count": len(ice_servers),
            "configuration_valid": bool(config.get("iceServers")),
            "timeouts_configured": bool(
                webrtc_config_service.get_connection_timeout() > 0
            )
        }
        
        # 総合的な接続可能性の評価
        connection_possible = (
            test_results["stun_servers_configured"] and
            test_results["configuration_valid"] and
            test_results["timeouts_configured"]
        )
        
        logger.info(
            "WebRTC接続テスト実行",
            user_id=current_user.id,
            connection_possible=connection_possible,
            test_results=test_results
        )
        
        return {
            "success": True,
            "connection_possible": connection_possible,
            "test_results": test_results,
            "recommendations": _get_connection_recommendations(test_results)
        }
        
    except Exception as e:
        logger.error(f"WebRTC接続テストエラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebRTC接続テストの実行に失敗しました"
        )


def _get_connection_recommendations(test_results: dict) -> list:
    """接続テスト結果に基づく推奨事項を生成"""
    recommendations = []
    
    if not test_results["stun_servers_configured"]:
        recommendations.append("STUNサーバーを設定してください")
    
    if not test_results["turn_servers_configured"]:
        recommendations.append("NAT環境での接続を改善するため、TURNサーバーの設定を検討してください")
    
    if not test_results["timeouts_configured"]:
        recommendations.append("接続タイムアウト設定を確認してください")
    
    if not recommendations:
        recommendations.append("WebRTC設定は正常です")
    
    return recommendations
