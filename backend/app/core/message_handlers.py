"""
WebSocketメッセージハンドラーの初期化とルーター登録
"""

import asyncio
from app.core.message_router import message_router, QueuedMessage
from app.core.websocket import WebSocketMessageHandler, manager
from app.schemas.websocket import WebSocketMessageType
import structlog

logger = structlog.get_logger()


async def initialize_message_handlers():
    """メッセージハンドラーの初期化"""
    logger.info("Initializing message handlers")

    # 基本メッセージハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.JOIN_SESSION, handle_join_session_message
    )
    message_router.register_handler(
        WebSocketMessageType.LEAVE_SESSION, handle_leave_session_message
    )
    message_router.register_handler(
        WebSocketMessageType.AUDIO_DATA, handle_audio_data_message
    )

    # メッセージングハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.TEXT_MESSAGE, handle_text_message
    )
    message_router.register_handler(
        WebSocketMessageType.EMOJI_REACTION, handle_emoji_reaction_message
    )
    message_router.register_handler(
        WebSocketMessageType.EDIT_MESSAGE, handle_edit_message
    )
    message_router.register_handler(
        WebSocketMessageType.DELETE_MESSAGE, handle_delete_message
    )

    # ユーザー状態ハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.TYPING_START, handle_typing_start_message
    )
    message_router.register_handler(
        WebSocketMessageType.TYPING_STOP, handle_typing_stop_message
    )

    # コラボレーションハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.FILE_SHARE, handle_file_share_message
    )
    message_router.register_handler(
        WebSocketMessageType.HAND_RAISE, handle_hand_raise_message
    )
    message_router.register_handler(
        WebSocketMessageType.HAND_LOWER, handle_hand_lower_message
    )

    # 投票ハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.POLL_CREATE, handle_poll_create_message
    )
    message_router.register_handler(
        WebSocketMessageType.POLL_VOTE, handle_poll_vote_message
    )

    # 通知・アナウンスメントハンドラーの登録
    message_router.register_handler(
        WebSocketMessageType.NOTIFICATION, handle_notification_request_message
    )
    message_router.register_handler(
        WebSocketMessageType.ANNOUNCEMENT, handle_announcement_request_message
    )

    # メッセージ処理開始
    await message_router.start_processing()

    logger.info("Message handlers initialized successfully")


async def shutdown_message_handlers():
    """メッセージハンドラーのシャットダウン"""
    logger.info("Shutting down message handlers")
    await message_router.stop_processing()
    logger.info("Message handlers shut down successfully")


# ハンドラー関数の実装
async def handle_join_session_message(queued_message: QueuedMessage):
    """セッション参加メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        # 接続情報からユーザーを取得
        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_join_session(
                queued_message.session_id, connection_id, user
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle join session message: {e}")
        raise


async def handle_leave_session_message(queued_message: QueuedMessage):
    """セッション退出メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_leave_session(
                queued_message.session_id, connection_id, user
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle leave session message: {e}")
        raise


async def handle_audio_data_message(queued_message: QueuedMessage):
    """音声データメッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_audio_data(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle audio data message: {e}")
        raise


async def handle_text_message(queued_message: QueuedMessage):
    """テキストメッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_text_message(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle text message: {e}")
        raise


async def handle_emoji_reaction_message(queued_message: QueuedMessage):
    """絵文字リアクションメッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_emoji_reaction(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle emoji reaction message: {e}")
        raise


async def handle_edit_message(queued_message: QueuedMessage):
    """メッセージ編集処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_edit_message(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle edit message: {e}")
        raise


async def handle_delete_message(queued_message: QueuedMessage):
    """メッセージ削除処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_delete_message(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle delete message: {e}")
        raise


async def handle_typing_start_message(queued_message: QueuedMessage):
    """入力開始メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_typing_start(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle typing start message: {e}")
        raise


async def handle_typing_stop_message(queued_message: QueuedMessage):
    """入力停止メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_typing_stop(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle typing stop message: {e}")
        raise


async def handle_file_share_message(queued_message: QueuedMessage):
    """ファイル共有メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_file_share(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle file share message: {e}")
        raise


async def handle_hand_raise_message(queued_message: QueuedMessage):
    """挙手メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_hand_raise(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle hand raise message: {e}")
        raise


async def handle_hand_lower_message(queued_message: QueuedMessage):
    """挙手解除メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_hand_lower(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle hand lower message: {e}")
        raise


async def handle_poll_create_message(queued_message: QueuedMessage):
    """投票作成メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_poll_create(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle poll create message: {e}")
        raise


async def handle_poll_vote_message(queued_message: QueuedMessage):
    """投票メッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_poll_vote(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle poll vote message: {e}")
        raise


async def handle_notification_request_message(queued_message: QueuedMessage):
    """通知リクエストメッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_notification_request(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle notification request message: {e}")
        raise


async def handle_announcement_request_message(queued_message: QueuedMessage):
    """アナウンスメントリクエストメッセージ処理"""
    try:
        message = queued_message.message
        connection_id = queued_message.metadata.get("connection_id")

        if connection_id and connection_id in manager.connection_info:
            user = manager.connection_info[connection_id]["user"]
            await WebSocketMessageHandler.handle_announcement_request(
                queued_message.session_id, connection_id, user, message
            )
        else:
            logger.warning(f"Connection not found for message: {queued_message.id}")

    except Exception as e:
        logger.error(f"Failed to handle announcement request message: {e}")
        raise
