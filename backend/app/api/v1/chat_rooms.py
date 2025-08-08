from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.chat_room_service import ChatRoomService
from app.schemas.chat_room import (
    ChatRoomCreate,
    ChatRoomUpdate,
    ChatRoomResponse,
    ChatRoomListResponse,
    ChatRoomDetailResponse,
    ChatRoomQueryParams,
    ChatRoomStats,
    ChatRoomParticipantCreate,
    ChatRoomParticipantResponse,
    ChatRoomParticipantListResponse,
)
from app.core.exceptions import BridgeLineException
from app.api.deps import handle_bridge_line_exceptions

router = APIRouter()


def get_chat_room_service(db: AsyncSession = Depends(get_db)) -> ChatRoomService:
    """チャットルームサービスの依存性注入"""
    return ChatRoomService(db)


@router.get("/", response_model=ChatRoomListResponse)
async def get_user_rooms(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ルームステータス"),
    room_type: Optional[str] = Query(None, description="ルームタイプ"),
    is_public: Optional[bool] = Query(None, description="公開フラグ"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """ユーザーのチャットルーム一覧を取得"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        query_params = ChatRoomQueryParams(
            page=page,
            size=size,
            status=status,
            room_type=room_type,
            is_public=is_public,
            search=search,
        )

        return await service.get_user_rooms(user_id, query_params)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get("/public", response_model=ChatRoomListResponse)
async def get_public_rooms(
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    status: Optional[str] = Query(None, description="ルームステータス"),
    room_type: Optional[str] = Query(None, description="ルームタイプ"),
    search: Optional[str] = Query(None, description="検索キーワード"),
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """公開チャットルーム一覧を取得"""
    try:
        query_params = ChatRoomQueryParams(
            page=page,
            size=size,
            status=status,
            room_type=room_type,
            search=search,
        )

        return await service.get_public_rooms(query_params)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post("/", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: ChatRoomCreate,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルームを作成"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.create_room(user_id, room_data)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get("/{room_id}", response_model=ChatRoomDetailResponse)
async def get_room(
    room_id: int,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルーム詳細を取得"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.get_room_by_id(room_id, user_id)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.put("/{room_id}", response_model=ChatRoomResponse)
async def update_room(
    room_id: int,
    update_data: ChatRoomUpdate,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルームを更新"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.update_room(room_id, user_id, update_data)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルームを削除"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        success = await service.delete_room(room_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Chat room not found", "error_code": "NOT_FOUND"},
            )

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post("/{room_id}/join", response_model=ChatRoomParticipantResponse)
async def join_room(
    room_id: int,
    participant_data: ChatRoomParticipantCreate,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """ルームに参加"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.join_room(room_id, user_id, participant_data)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    room_id: int,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """ルームから退出"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        success = await service.leave_room(room_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Chat room not found or user not in room",
                    "error_code": "NOT_FOUND",
                },
            )

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get("/{room_id}/participants", response_model=ChatRoomParticipantListResponse)
async def get_room_participants(
    room_id: int,
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """ルームの参加者一覧を取得"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.get_room_participants(room_id, user_id)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get("/search", response_model=ChatRoomListResponse)
async def search_rooms(
    q: str = Query(..., description="検索キーワード"),
    page: int = Query(1, ge=1, description="ページ番号"),
    size: int = Query(10, ge=1, le=100, description="ページサイズ"),
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルームを検索"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        query_params = ChatRoomQueryParams(
            page=page,
            size=size,
        )

        return await service.search_rooms(user_id, q, query_params)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.get("/stats", response_model=ChatRoomStats)
async def get_room_stats(
    service: ChatRoomService = Depends(get_chat_room_service),
):
    """チャットルーム統計を取得"""
    try:
        # TODO: 実際のユーザーIDを認証から取得
        user_id = 1  # 仮のユーザーID

        return await service.get_room_stats(user_id)

    except BridgeLineException as e:
        raise handle_bridge_line_exceptions(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )
