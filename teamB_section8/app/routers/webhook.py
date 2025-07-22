"""
LINE Webhookエンドポイント
- 署名検証
- メッセージイベント処理
- OpenAI連携
"""

from fastapi import APIRouter, Request, Header, HTTPException
from app.services.line_service import handle_line_event
from app.config import settings

router = APIRouter()


@router.post("/webhook", tags=["LINE Webhook"])
async def line_webhook(request: Request, x_line_signature: str = Header(None)) -> dict:
    """
    LINEプラットフォームからのWebhookイベントを受信し処理する
    """
    body = await request.body()
    # 署名検証
    from linebot import WebhookHandler, exceptions

    handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except exceptions.InvalidSignatureError:
        raise HTTPException(status_code=400, detail="署名検証に失敗しました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook処理中にエラー: {e}")
    # メッセージ処理（OpenAI連携含む）
    result = await handle_line_event(body)
    return {"result": result}
