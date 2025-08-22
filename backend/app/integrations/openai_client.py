import os
import asyncio
import base64
import io
import wave
import numpy as np
from typing import Optional, Dict, Any, List
import structlog
from openai import AsyncOpenAI
from app.config import settings

logger = structlog.get_logger()


class OpenAIClient:
    """OpenAI APIクライアント"""

    def __init__(self):
        # 環境に応じたAPIキーを取得
        api_key = settings.get_openai_api_key
        if not api_key:
            raise ValueError(
                f"OpenAI API key not found for environment: {settings.ENVIRONMENT}. "
                f"Please set OPENAI_PERSONAL_API_KEY for production or OPENAI_EDUCATIONAL_API_KEY for development."
            )

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "whisper-1"
        self.max_retries = 3
        self.retry_delay = 1.0

        logger.info(
            f"OpenAI client initialized with environment: {settings.ENVIRONMENT}"
        )

    async def transcribe_audio_file(
        self, audio_file_path: str, language: str = "ja"
    ) -> Dict[str, Any]:
        """音声ファイルを転写"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["word"],
                )

            logger.info(f"Transcription completed for {audio_file_path}")
            return response.model_dump()

        except Exception as e:
            logger.error(f"Failed to transcribe audio file {audio_file_path}: {e}")
            raise

    async def transcribe_audio_data(
        self, audio_data: bytes, language: str = "ja"
    ) -> Dict[str, Any]:
        """音声データを転写"""
        try:
            # 音声データをファイルオブジェクトとして作成
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

            logger.info("Audio data transcription completed")
            return response.model_dump()

        except Exception as e:
            logger.error(f"Failed to transcribe audio data: {e}")
            raise

    async def transcribe_chunk(
        self, audio_chunk: bytes, language: str = "ja"
    ) -> Optional[Dict[str, Any]]:
        """音声チャンクを転写（短時間用）"""
        try:
            # 音声チャンクをWAV形式に変換
            wav_data = self._convert_to_wav(audio_chunk)

            audio_file = io.BytesIO(wav_data)
            audio_file.name = "chunk.wav"

            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

            return response.model_dump()

        except Exception as e:
            logger.error(f"Failed to transcribe audio chunk: {e}")
            return None

    def _convert_to_wav(
        self, audio_data: bytes, sample_rate: int = 16000, channels: int = 1
    ) -> bytes:
        """音声データをWAV形式に変換"""
        try:
            # バイトデータを数値配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # WAVファイルとして出力
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)

            return wav_buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to convert audio to WAV: {e}")
            raise

    async def get_embedding(self, text: str) -> List[float]:
        """テキストの埋め込みベクトルを取得"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small", input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """テキストの感情分析"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "以下のテキストの感情分析を行い、JSON形式で返してください。感情（positive/negative/neutral）、信頼度（0-1）、主要な感情キーワードを含めてください。",
                    },
                    {"role": "user", "content": text},
                ],
                response_format={"type": "json_object"},
            )

            import json

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "keywords": []}


# グローバルインスタンス（完全遅延初期化）
_openai_client_instance = None


def get_openai_client():
    """OpenAIクライアントのインスタンスを取得（完全遅延初期化）"""
    global _openai_client_instance
    if _openai_client_instance is None:
        try:
            _openai_client_instance = OpenAIClient()
        except Exception as e:
            # 初期化に失敗した場合のフォールバック
            logger.warning(f"OpenAI client initialization failed: {e}")

            # ダミークライアントを作成（実際の使用時にはエラーが発生）
            class DummyOpenAIClient:
                def __init__(self, error_msg):
                    self.client = None
                    self.model = "whisper-1"
                    self.max_retries = 3
                    self.retry_delay = 1.0
                    self.error_msg = error_msg

                def __getattr__(self, name):
                    raise RuntimeError(
                        f"OpenAI client not properly initialized: {self.error_msg}"
                    )

            _openai_client_instance = DummyOpenAIClient(str(e))
    return _openai_client_instance


# 後方互換性のため（実際の使用時まで初期化を遅延）
def openai_client():
    return get_openai_client()
