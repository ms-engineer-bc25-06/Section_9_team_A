#!/usr/bin/env python3
"""
WebSocket接続テストスクリプト
音声セッションのWebSocket機能をテストします
"""

import asyncio
import json
import websockets
import base64
import time
from datetime import datetime
from typing import Optional


class WebSocketTestClient:
    """WebSocketテストクライアント"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.session_id = None
        self.user_id = None

    async def connect(self, session_id: str, token: str):
        """WebSocket接続を確立"""
        url = f"{self.base_url}/api/v1/ws/voice-sessions/{session_id}?token={token}"

        try:
            self.websocket = await websockets.connect(url)
            self.connected = True
            self.session_id = session_id
            print(f"✅ WebSocket接続成功: {session_id}")

            # 接続確認メッセージを受信
            await self.receive_messages()

        except Exception as e:
            print(f"❌ WebSocket接続失敗: {e}")
            self.connected = False

    async def send_message(self, message: dict):
        """メッセージを送信"""
        if not self.connected or not self.websocket:
            print("❌ WebSocketが接続されていません")
            return

        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 メッセージ送信: {message['type']}")
        except Exception as e:
            print(f"❌ メッセージ送信失敗: {e}")

    async def receive_messages(self):
        """メッセージを受信"""
        if not self.connected or not self.websocket:
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"📥 メッセージ受信: {data['type']}")

                # 接続確立メッセージの処理
                if data["type"] == "connection_established":
                    self.user_id = data.get("user_id")
                    print(f"👤 ユーザーID: {self.user_id}")

                # 参加者一覧の処理
                elif data["type"] == "session_participants":
                    participants = data.get("participants", [])
                    print(f"👥 参加者一覧: {participants}")

                # ユーザー参加通知の処理
                elif data["type"] == "user_joined":
                    user = data.get("user", {})
                    print(f"👋 ユーザー参加: {user.get('display_name')}")

                # ユーザー退出通知の処理
                elif data["type"] == "user_left":
                    user = data.get("user", {})
                    print(f"👋 ユーザー退出: {user.get('display_name')}")

                # 音声データの処理
                elif data["type"] == "audio_data":
                    user_id = data.get("user_id")
                    print(f"🎵 音声データ受信: ユーザー {user_id}")

                # エラーメッセージの処理
                elif data["type"] == "error":
                    error_msg = data.get("message", "Unknown error")
                    print(f"❌ エラー: {error_msg}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket接続が切断されました")
            self.connected = False
        except Exception as e:
            print(f"❌ メッセージ受信エラー: {e}")
            self.connected = False

    async def join_session(self):
        """セッションに参加"""
        message = {
            "type": "join_session",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_message(message)

    async def leave_session(self):
        """セッションから退出"""
        message = {
            "type": "leave_session",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self.send_message(message)

    async def send_audio_data(self, audio_data: str = "test_audio_data"):
        """音声データを送信"""
        message = {
            "type": "audio_data",
            "session_id": self.session_id,
            "user_id": self.user_id,
            "data": base64.b64encode(audio_data.encode()).decode(),
            "timestamp": datetime.now().isoformat(),
            "chunk_id": f"chunk_{int(time.time())}",
            "sample_rate": 16000,
            "channels": 1,
        }
        await self.send_message(message)

    async def send_ping(self):
        """Pingメッセージを送信"""
        message = {"type": "ping", "timestamp": datetime.now().isoformat()}
        await self.send_message(message)

    async def close(self):
        """接続を閉じる"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        print("🔌 WebSocket接続を閉じました")


async def test_websocket_connection():
    """WebSocket接続テスト"""
    # テスト用の設定
    session_id = "test-session-123"
    token = "your-jwt-token-here"  # 実際のJWTトークンに置き換えてください

    client = WebSocketTestClient()

    try:
        # 接続
        await client.connect(session_id, token)

        if not client.connected:
            print("❌ 接続に失敗しました")
            return

        # セッション参加
        await client.join_session()
        await asyncio.sleep(1)

        # Ping送信
        await client.send_ping()
        await asyncio.sleep(1)

        # 音声データ送信（複数回）
        for i in range(3):
            await client.send_audio_data(f"test_audio_chunk_{i}")
            await asyncio.sleep(0.5)

        # 少し待機
        await asyncio.sleep(2)

        # セッション退出
        await client.leave_session()
        await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 テストを中断しました")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    finally:
        await client.close()


async def test_multiple_clients():
    """複数クライアントのテスト"""
    session_id = "test-session-multi"
    token = "your-jwt-token-here"

    clients = []

    try:
        # 3つのクライアントを作成
        for i in range(3):
            client = WebSocketTestClient()
            await client.connect(session_id, token)
            clients.append(client)

            if client.connected:
                await client.join_session()
                await asyncio.sleep(0.5)

        # 全クライアントで音声データ送信
        for i, client in enumerate(clients):
            if client.connected:
                await client.send_audio_data(f"audio_from_client_{i}")
                await asyncio.sleep(0.3)

        # 少し待機
        await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 テストを中断しました")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    finally:
        # 全クライアントを閉じる
        for client in clients:
            await client.close()


if __name__ == "__main__":
    print("🚀 WebSocketテストを開始します")
    print("=" * 50)

    # 単一クライアントテスト
    print("📡 単一クライアントテスト")
    asyncio.run(test_websocket_connection())

    print("\n" + "=" * 50)

    # 複数クライアントテスト
    print("📡 複数クライアントテスト")
    asyncio.run(test_multiple_clients())

    print("\n✅ テスト完了")
