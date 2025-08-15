import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from types import SimpleNamespace

from app.core.message_handlers import (
    handle_typing_start_message,
    handle_typing_stop_message,
    handle_file_share_message,
    handle_poll_create_message,
    handle_hand_raise_message,
)
from app.core.message_router import QueuedMessage
from app.schemas.websocket import WebSocketMessageType, MessagePriority
from app.core.websocket import manager


@pytest.fixture
def user():
    return SimpleNamespace(
        id=42,
        email="u@example.com",
        display_name="U",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_qmsg(
    session_id: str, user_id: int, connection_id: str, message: dict
) -> QueuedMessage:
    return QueuedMessage(
        id="m1",
        message=message,
        priority=MessagePriority.NORMAL,
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now(),
        metadata={"connection_id": connection_id},
    )


@pytest.mark.asyncio
async def test_typing_start_broadcast(user):
    connection_id = "conn-1"
    session_id = "s-typing"
    manager.connection_info[connection_id] = {"user": user}

    q = make_qmsg(
        session_id,
        user.id,
        connection_id,
        {"type": WebSocketMessageType.TYPING_START, "session_id": session_id},
    )

    with patch(
        "app.core.websocket.manager.broadcast_to_session", new_callable=AsyncMock
    ) as mock_bcast:
        await handle_typing_start_message(q)
        mock_bcast.assert_awaited()
        args, kwargs = mock_bcast.await_args
        assert args[0]["type"] == "typing_start"
        assert args[1] == session_id


@pytest.mark.asyncio
async def test_typing_stop_broadcast(user):
    connection_id = "conn-2"
    session_id = "s-typing"
    manager.connection_info[connection_id] = {"user": user}

    q = make_qmsg(
        session_id,
        user.id,
        connection_id,
        {"type": WebSocketMessageType.TYPING_STOP, "session_id": session_id},
    )

    with patch(
        "app.core.websocket.manager.broadcast_to_session", new_callable=AsyncMock
    ) as mock_bcast:
        await handle_typing_stop_message(q)
        mock_bcast.assert_awaited()
        args, kwargs = mock_bcast.await_args
        assert args[0]["type"] == "typing_stop"
        assert args[1] == session_id


@pytest.mark.asyncio
async def test_file_share_sends_message_and_broadcast(user):
    connection_id = "conn-3"
    session_id = "s-file"
    manager.connection_info[connection_id] = {"user": user}

    q = make_qmsg(
        session_id,
        user.id,
        connection_id,
        {
            "type": WebSocketMessageType.FILE_SHARE,
            "session_id": session_id,
            "file_name": "file.pdf",
            "file_size": 100,
            "file_type": "application/pdf",
            "file_url": "https://example.com/file.pdf",
            "description": "desc",
        },
    )

    with (
        patch(
            "app.services.messaging_service.messaging_service.send_text_message",
            new_callable=AsyncMock,
        ) as mock_send,
        patch(
            "app.core.websocket.manager.broadcast_to_session", new_callable=AsyncMock
        ) as mock_bcast,
    ):
        await handle_file_share_message(q)
        mock_send.assert_awaited()
        mock_bcast.assert_awaited()
        args, kwargs = mock_bcast.await_args
        assert args[0]["type"] == "file_share"
        assert args[1] == session_id


@pytest.mark.asyncio
async def test_poll_create_system_message_and_broadcast(user):
    connection_id = "conn-4"
    session_id = "s-poll"
    manager.connection_info[connection_id] = {"user": user}

    q = make_qmsg(
        session_id,
        user.id,
        connection_id,
        {
            "type": WebSocketMessageType.POLL_CREATE,
            "session_id": session_id,
            "poll_id": "p1",
            "question": "Q?",
            "options": [{"text": "A"}, {"text": "B"}],
            "multiple_choice": False,
            "anonymous": False,
            "duration": 30,
        },
    )

    with (
        patch(
            "app.services.messaging_service.messaging_service.send_system_message",
            new_callable=AsyncMock,
        ) as mock_sys,
        patch(
            "app.core.websocket.manager.broadcast_to_session", new_callable=AsyncMock
        ) as mock_bcast,
    ):
        await handle_poll_create_message(q)
        mock_sys.assert_awaited()
        mock_bcast.assert_awaited()
        args, kwargs = mock_bcast.await_args
        assert args[0]["type"] == "poll_create"
        assert args[1] == session_id


@pytest.mark.asyncio
async def test_hand_raise_updates_status_and_broadcast(user):
    connection_id = "conn-5"
    session_id = "s-hr"
    manager.connection_info[connection_id] = {"user": user}

    q = make_qmsg(
        session_id,
        user.id,
        connection_id,
        {
            "type": WebSocketMessageType.HAND_RAISE,
            "session_id": session_id,
            "reason": "q",
        },
    )

    with (
        patch(
            "app.services.participant_management_service.participant_manager.update_participant_status",
            new_callable=AsyncMock,
        ) as mock_update,
        patch(
            "app.core.websocket.manager.broadcast_to_session", new_callable=AsyncMock
        ) as mock_bcast,
    ):
        await handle_hand_raise_message(q)
        mock_update.assert_awaited()
        mock_bcast.assert_awaited()
        args, kwargs = mock_bcast.await_args
        assert args[0]["type"] == "hand_raise"
        assert args[1] == session_id
