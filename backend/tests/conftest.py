import asyncio
import pytest
import pytest_asyncio
from typing import Any, Optional, Dict

from httpx import AsyncClient
from httpx import ASGITransport
from starlette.testclient import TestClient

from app.main import app
from app.models.base import Base

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from app.config import settings

# テスト用データベースURL
TEST_DATABASE_URL = (
    "postgresql+asyncpg://bridge_user:bridge_password@postgres:5432/bridge_line_test_db"
)


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
    """テスト用のイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """テスト用データベースエンジン"""
    # テスト環境であることを示す環境変数を設定
    os.environ["TESTING"] = "1"

    # テスト用エンジン作成
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        future=True,
    )

    # テスト用データベースの初期化
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # クリーンアップ
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """テスト用データベースセッション"""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


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
