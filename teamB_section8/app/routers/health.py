"""
ヘルスチェックAPI
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    サーバーの稼働確認用エンドポイント
    """
    return {"status": "ok"}
