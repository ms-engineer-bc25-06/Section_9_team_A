"""
OpenAI API連携サービス
- Chat Completions API
- エラーハンドリング
- レート制限・タイムアウト
"""

import openai
from app.config import settings
from typing import Any
import asyncio


async def chat_with_openai(prompt: str) -> Any:
    """
    OpenAI Chat Completions APIを呼び出し、応答を返す
    """
    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_key=settings.OPENAI_API_KEY,
            timeout=10,
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.RateLimitError:
        return "OpenAI APIのレート制限に達しました。しばらく待って再試行してください。"
    except Exception as e:
        return f"OpenAI API呼び出し中にエラー: {e}"
