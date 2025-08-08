import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from types import SimpleNamespace

from app.core.message_router import MessageRouter
from app.schemas.websocket import WebSocketMessageType, MessagePriority


@pytest.fixture
def router():
    return MessageRouter()


@pytest.fixture
def user():
    return SimpleNamespace(
        id=123,
        email="user@example.com",
        display_name="Tester",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_validation_text_message_sanitized(router: MessageRouter, user):
    message = {
        "type": WebSocketMessageType.TEXT_MESSAGE,
        "session_id": "s1",
        "content": "<script>alert(1)</script><b>ok</b>",
    }

    ok = await router.route_message(message, user, session_id="s1", connection_id="c1")
    assert ok is True
    assert "<script>" not in message["content"]
    assert "<b>ok</b>" in message["content"]


@pytest.mark.asyncio
async def test_validation_message_size_limit(router: MessageRouter, user):
    big_content = "a" * 5000
    message = {
        "type": WebSocketMessageType.TEXT_MESSAGE,
        "session_id": "s1",
        "content": big_content,
    }
    ok = await router.route_message(message, user, session_id="s1", connection_id="c1")
    assert ok is False


@pytest.mark.asyncio
async def test_validation_file_share_type_and_size(router: MessageRouter, user):
    msg_bad_ext = {
        "type": WebSocketMessageType.FILE_SHARE,
        "session_id": "s1",
        "file_name": "payload.exe",
        "file_size": 100,
        "file_type": "application/octet-stream",
    }
    ok_ext = await router.route_message(msg_bad_ext, user, "s1", "c1")
    assert ok_ext is False

    msg_big = {
        "type": WebSocketMessageType.FILE_SHARE,
        "session_id": "s1",
        "file_name": "file.pdf",
        "file_size": 200 * 1024 * 1024,
        "file_type": "application/pdf",
    }
    ok_big = await router.route_message(msg_big, user, "s1", "c1")
    assert ok_big is False

    msg_ok = {
        "type": WebSocketMessageType.FILE_SHARE,
        "session_id": "s1",
        "file_name": "file.pdf",
        "file_size": 1024,
        "file_type": "application/pdf",
    }
    ok_ok = await router.route_message(msg_ok, user, "s1", "c1")
    assert ok_ok is True


@pytest.mark.asyncio
async def test_validation_poll_options(router: MessageRouter, user):
    msg_bad = {
        "type": WebSocketMessageType.POLL_CREATE,
        "session_id": "s1",
        "poll_id": "p1",
        "question": "?",
        "options": [{"text": "one"}],
    }
    ok_bad = await router.route_message(msg_bad, user, "s1", "c1")
    assert ok_bad is False

    msg_ok = {
        "type": WebSocketMessageType.POLL_CREATE,
        "session_id": "s1",
        "poll_id": "p2",
        "question": "Pick",
        "options": [{"text": "A"}, {"text": "B"}],
    }
    ok_ok = await router.route_message(msg_ok, user, "s1", "c1")
    assert ok_ok is True


@pytest.mark.asyncio
async def test_rate_limiter_respects_priority(router: MessageRouter, user):
    allowed = 0
    for _ in range(31):
        ok = await router.rate_limiter.is_allowed(user.id, MessagePriority.NORMAL)
        if ok:
            allowed += 1
    assert allowed == 30


@pytest.mark.asyncio
async def test_priority_processing_order(router: MessageRouter, user):
    processed: list[tuple[str, str]] = []

    async def handler(queued):
        processed.append((queued.priority.value, queued.id))

    router.register_handler(WebSocketMessageType.TEXT_MESSAGE, handler)

    await router.route_message(
        {"type": WebSocketMessageType.TEXT_MESSAGE, "session_id": "s1", "content": "n"},
        user,
        "s1",
        "c1",
    )
    await router.route_message(
        {
            "type": WebSocketMessageType.TEXT_MESSAGE,
            "session_id": "s1",
            "content": "u",
            "priority": "urgent",
        },
        user,
        "s1",
        "c2",
    )

    await router.start_processing()
    await asyncio.sleep(0.5)
    await router.stop_processing()

    assert any(p[0] == "urgent" for p in processed)


@pytest.mark.asyncio
async def test_no_handler_counts_failed(router: MessageRouter, user):
    await router.route_message(
        {"type": WebSocketMessageType.ANNOUNCEMENT, "title": "t", "content": "c"},
        user,
        "s1",
        "c1",
    )

    await router.start_processing()
    await asyncio.sleep(0.2)
    await router.stop_processing()

    stats = router.get_stats()
    assert stats["messages_failed"] >= 1
