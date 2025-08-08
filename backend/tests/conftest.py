import asyncio
import pytest
import pytest_asyncio
from typing import Any, Optional, Dict

from httpx import AsyncClient
from httpx import ASGITransport
from starlette.testclient import TestClient

from app.main import app
from app.core.database import Base, engine


class CombinedTestClient:
    """HTTPの非同期呼び出しとWebSocket接続の両方を提供するテストクライアント。

    - HTTP: httpx.AsyncClient (ASGITransport)
    - WebSocket: starlette.testclient.TestClient
    """

    def __init__(self, async_client: AsyncClient, ws_client: TestClient) -> None:
        self._async_client = async_client
        self._ws_client = ws_client

    # ----- HTTP (async) -----
    async def get(self, url: str, **kwargs: Any):
        return await self._async_client.get(url, **kwargs)

    async def post(self, url: str, **kwargs: Any):
        return await self._async_client.post(url, **kwargs)

    async def put(self, url: str, **kwargs: Any):
        return await self._async_client.put(url, **kwargs)

    async def patch(self, url: str, **kwargs: Any):
        return await self._async_client.patch(url, **kwargs)

    async def delete(self, url: str, **kwargs: Any):
        return await self._async_client.delete(url, **kwargs)

    # ----- WebSocket (sync context manager) -----
    def websocket_connect(self, url: str, *args: Any, **kwargs: Any):
        return self._ws_client.websocket_connect(url, *args, **kwargs)

    # ----- Cleanup -----
    async def aclose(self) -> None:
        await self._async_client.aclose()
        self._ws_client.close()


@pytest.fixture(scope="session")
def event_loop():
    """各テストクラスで専用のイベントループを提供。"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_sqlalchemy():
    """SQLAlchemyの設定を初期化"""
    # モデルをインポートしてSQLAlchemyの設定を初期化
    from app.models import (  # noqa
        User,
        Team,
        TeamMember,
        VoiceSession,
        ChatRoom,
        ChatMessage,
        ChatRoomParticipant,
        Transcription,
        Analysis,
        Subscription,
        Billing,
        Invitation,
        AuditLog,
    )

    yield


@pytest_asyncio.fixture
async def client() -> CombinedTestClient:
    """HTTP(Async) + WebSocket を兼ねるクライアント。"""
    transport = ASGITransport(app=app)
    async_client = AsyncClient(transport=transport, base_url="http://test")
    ws_client = TestClient(app)
    combined = CombinedTestClient(async_client, ws_client)
    try:
        yield combined
    finally:
        await combined.aclose()
