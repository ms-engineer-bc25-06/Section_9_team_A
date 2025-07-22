"""
LINEメッセージイベント処理サービス
- 署名検証
- OpenAI連携
"""

from typing import Any
from app.services.openai_service import chat_with_openai


async def handle_line_event(body: bytes) -> Any:
    """
    LINEイベントを解析し、必要に応じてOpenAIへ問い合わせる
    """
    # TODO: LINEイベントのパース・返信処理を実装
    # 例: テキストメッセージ受信時にOpenAIへ問い合わせ
    # ここではダミー応答
    openai_response = await chat_with_openai("こんにちは！")
    return openai_response
