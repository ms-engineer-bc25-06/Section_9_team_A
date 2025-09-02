"""
テスト用の共通ヘルパー関数
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 既存のヘルパー関数
def format_datetime(dt: datetime) -> str:
    """日時をISO形式の文字列に変換"""
    return dt.isoformat()

def validate_email(email: str) -> bool:
    """メールアドレスの形式を検証"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_random_string(length: int = 10) -> str:
    """ランダムな文字列を生成"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def sanitize_html(html_content: str) -> str:
    """HTMLコンテンツをサニタイズ"""
    import re
    # 基本的なHTMLタグを除去
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_content)

def truncate_text(text: str, max_length: int = 100) -> str:
    """テキストを指定された長さで切り詰め"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

# 新しく追加する共通テストヘルパー関数

def create_mock_user(
    user_id: int = 1,
    email: str = "test@example.com",
    username: str = "testuser",
    full_name: str = "Test User",
    firebase_uid: str = "test_firebase_uid",
    is_admin: bool = False,
    is_active: bool = True
) -> MagicMock:
    """モックユーザーオブジェクトを作成"""
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = email
    mock_user.username = username
    mock_user.full_name = full_name
    mock_user.firebase_uid = firebase_uid
    mock_user.is_admin = is_admin
    mock_user.is_active = is_active
    mock_user.is_premium = False
    mock_user.is_verified = True
    return mock_user

def create_mock_team(
    team_id: int = 1,
    name: str = "Test Team",
    description: str = "A test team",
    owner_id: int = 1,
    is_active: bool = True
) -> MagicMock:
    """モックチームオブジェクトを作成"""
    mock_team = MagicMock()
    mock_team.id = team_id
    mock_team.name = name
    mock_team.description = description
    mock_team.owner_id = owner_id
    mock_team.is_active = is_active
    return mock_team

def create_mock_voice_session(
    session_id: int = 1,
    title: str = "Test Session",
    description: str = "A test voice session",
    team_id: int = 1,
    host_id: int = 1,
    status: str = "active",
    is_recording: bool = False
) -> MagicMock:
    """モック音声セッションオブジェクトを作成"""
    mock_session = MagicMock()
    mock_session.id = session_id
    mock_session.title = title
    mock_session.description = description
    mock_session.team_id = team_id
    mock_session.host_id = host_id
    mock_session.status = status
    mock_session.is_recording = is_recording
    mock_session.created_at = datetime.utcnow()
    mock_session.updated_at = datetime.utcnow()
    return mock_session

def create_mock_transcription(
    transcription_id: int = 1,
    voice_session_id: int = 1,
    speaker_id: int = 1,
    text_content: str = "これはテスト用の転写テキストです。",
    confidence_score: float = 0.95,
    language: str = "ja",
    is_final: bool = True
) -> MagicMock:
    """モック転写オブジェクトを作成"""
    mock_transcription = MagicMock()
    mock_transcription.id = transcription_id
    mock_transcription.voice_session_id = voice_session_id
    mock_transcription.speaker_id = speaker_id
    mock_transcription.text_content = text_content
    mock_transcription.start_time_seconds = 0.0
    mock_transcription.end_time_seconds = 5.0
    mock_transcription.confidence_score = confidence_score
    mock_transcription.language = language
    mock_transcription.is_final = is_final
    mock_transcription.is_processed = False
    return mock_transcription

def create_mock_billing(
    billing_id: int = 1,
    user_id: int = 1,
    amount: float = 1000.0,
    currency: str = "JPY",
    status: str = "pending",
    payment_method: str = "credit_card"
) -> MagicMock:
    """モック請求オブジェクトを作成"""
    mock_billing = MagicMock()
    mock_billing.id = billing_id
    mock_billing.billing_id = f"bill_{billing_id}"
    mock_billing.invoice_number = f"INV-2024-{billing_id:03d}"
    mock_billing.amount = amount
    mock_billing.currency = currency
    mock_billing.tax_amount = amount * 0.1
    mock_billing.total_amount = amount * 1.1
    mock_billing.status = status
    mock_billing.payment_method = payment_method
    mock_billing.user_id = user_id
    mock_billing.created_at = datetime.utcnow()
    mock_billing.due_date = datetime.utcnow() + timedelta(days=30)
    return mock_billing

def create_mock_subscription(
    subscription_id: int = 1,
    user_id: int = 1,
    organization_id: int = 1,
    status: str = "active",
    quantity: int = 5
) -> MagicMock:
    """モックサブスクリプションオブジェクトを作成"""
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.user_id = user_id
    mock_subscription.organization_id = organization_id
    mock_subscription.stripe_subscription_id = f"sub_{subscription_id}"
    mock_subscription.stripe_price_id = f"price_{subscription_id}"
    mock_subscription.status = status
    mock_subscription.current_period_start = datetime.utcnow()
    mock_subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
    mock_subscription.quantity = quantity
    mock_subscription.created_at = datetime.utcnow()
    mock_subscription.updated_at = datetime.utcnow()
    return mock_subscription

def create_mock_payment(
    payment_id: int = 1,
    organization_id: int = 1,
    amount: int = 2980,
    currency: str = "jpy",
    status: str = "pending"
) -> MagicMock:
    """モック決済オブジェクトを作成"""
    mock_payment = MagicMock()
    mock_payment.id = payment_id
    mock_payment.organization_id = organization_id
    mock_payment.amount = amount
    mock_payment.currency = currency
    mock_payment.status = status
    mock_payment.stripe_payment_intent_id = f"pi_test_{payment_id}"
    mock_payment.created_at = datetime.utcnow()
    return mock_payment

def create_mock_organization(
    org_id: int = 1,
    name: str = "Test Organization",
    owner_id: int = 1
) -> MagicMock:
    """モック組織オブジェクトを作成"""
    mock_org = MagicMock()
    mock_org.id = org_id
    mock_org.name = name
    mock_org.owner_id = owner_id
    mock_org.created_at = datetime.utcnow()
    return mock_org

def create_mock_websocket():
    """モックWebSocketオブジェクトを作成"""
    mock_ws = MagicMock()
    mock_ws.query_params = {}
    mock_ws.client_state.value = "CONNECTED"
    mock_ws.accept = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.send_text = AsyncMock()
    return mock_ws

def create_mock_audio_data(size: int = 1024) -> bytes:
    """モック音声データを作成"""
    return b"mock_audio_data_" + str(size).encode()

def create_mock_transcription_result(
    text: str = "これはテスト用の転写テキストです。",
    confidence: float = 0.95,
    language: str = "ja"
) -> Dict[str, Any]:
    """モック転写結果を作成"""
    return {
        "text": text,
        "confidence": confidence,
        "language": language,
        "segments": [
            {
                "start": 0.0,
                "end": 5.0,
                "text": text
            }
        ]
    }

def create_mock_checkout_event(
    session_id: str = "cs_test_123",
    amount_total: int = 2980,
    currency: str = "jpy",
    customer_email: str = "test@example.com",
    organization_id: str = "1"
) -> Dict[str, Any]:
    """モックチェックアウト完了イベントを作成"""
    return {
        "id": "evt_1234567890",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "payment_status": "paid",
                "amount_total": amount_total,
                "currency": currency,
                "customer_email": customer_email,
                "metadata": {
                    "organization_id": organization_id,
                    "plan_type": "premium",
                    "user_count": "15"
                }
            }
        }
    }

def create_mock_payment_succeeded_event(
    invoice_id: str = "in_test_123",
    subscription_id: str = "sub_test_123",
    amount_paid: int = 2980,
    currency: str = "jpy"
) -> Dict[str, Any]:
    """モック決済成功イベントを作成"""
    return {
        "id": "evt_1234567891",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": invoice_id,
                "subscription": subscription_id,
                "amount_paid": amount_paid,
                "currency": currency,
                "status": "paid"
            }
        }
    }

def create_mock_payment_failed_event(
    invoice_id: str = "in_test_124",
    subscription_id: str = "sub_test_123",
    amount_due: int = 2980,
    currency: str = "jpy"
) -> Dict[str, Any]:
    """モック決済失敗イベントを作成"""
    return {
        "id": "evt_1234567892",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": invoice_id,
                "subscription": subscription_id,
                "amount_due": amount_due,
                "currency": currency,
                "status": "open"
            }
        }
    }

def create_mock_invoice_data(
    user_id: int = 1,
    amount: float = 2980.0,
    currency: str = "JPY",
    description: str = "Premium Plan - Monthly Subscription"
) -> Dict[str, Any]:
    """モック請求書データを作成"""
    return {
        "user_id": user_id,
        "amount": amount,
        "currency": currency,
        "description": description,
        "due_date": datetime.utcnow() + timedelta(days=30),
        "status": "pending"
    }

def create_mock_subscription_data(
    user_id: int = 1,
    organization_id: int = 1,
    status: str = "trialing",
    quantity: int = 5
) -> Dict[str, Any]:
    """モックサブスクリプションデータを作成"""
    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "stripe_subscription_id": "sub_1234567890",
        "stripe_price_id": "price_1234567890",
        "status": status,
        "current_period_start": datetime.utcnow(),
        "current_period_end": datetime.utcnow() + timedelta(days=30),
        "quantity": quantity,
        "subscription_metadata": {
            "plan_type": "premium",
            "billing_cycle": "monthly"
        }
    }

def create_mock_analysis_data(
    analysis_id: str = "analysis_123",
    analysis_type: str = "personality",
    user_id: int = 1,
    status: str = "completed"
) -> Dict[str, Any]:
    """モック分析データを作成"""
    return {
        "id": 1,
        "analysis_id": analysis_id,
        "analysis_type": analysis_type,
        "content": "テスト用の分析コンテンツ",
        "user_id": user_id,
        "status": status,
        "created_at": datetime.utcnow()
    }

def create_mock_audio_message(
    session_id: str = "test_session_123",
    user_id: int = 1,
    chunk_id: str = "chunk_123",
    data: bytes = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> MagicMock:
    """モック音声メッセージを作成"""
    if data is None:
        data = create_mock_audio_data()
    
    mock_message = MagicMock()
    mock_message.session_id = session_id
    mock_message.user_id = user_id
    mock_message.chunk_id = chunk_id
    mock_message.data = data
    mock_message.sample_rate = sample_rate
    mock_message.channels = channels
    mock_message.timestamp = datetime.utcnow()
    return mock_message

def create_mock_openai_client():
    """モックOpenAIクライアントを作成"""
    mock_client = MagicMock()
    mock_client.transcribe_audio_data = AsyncMock()
    mock_client.transcribe_chunk = AsyncMock()
    mock_client.analyze_text = AsyncMock()
    return mock_client

def create_mock_announcement_manager():
    """モックアナウンスメントマネージャーを作成"""
    mock_manager = MagicMock()
    mock_manager.broadcast_to_session = AsyncMock()
    mock_manager.broadcast_to_user = AsyncMock()
    mock_manager.user_connections = {1: set(), 2: set()}
    return mock_manager

def create_mock_notification_manager():
    """モック通知マネージャーを作成"""
    mock_manager = MagicMock()
    mock_manager.send_personal_message = AsyncMock()
    mock_manager.broadcast_to_session = AsyncMock()
    return mock_manager

# テスト用の共通アサーション関数
def assert_user_data(user: MagicMock, expected_data: Dict[str, Any]):
    """ユーザーデータの検証"""
    assert user.email == expected_data["email"]
    assert user.username == expected_data["username"]
    assert user.full_name == expected_data["full_name"]
    assert user.firebase_uid == expected_data["firebase_uid"]
    assert user.is_active == expected_data["is_active"]
    if "is_admin" in expected_data:
        assert user.is_admin == expected_data["is_admin"]

def assert_team_data(team: MagicMock, expected_data: Dict[str, Any]):
    """チームデータの検証"""
    assert team.name == expected_data["name"]
    assert team.description == expected_data["description"]
    assert team.owner_id == expected_data["owner_id"]
    assert team.is_active == expected_data["is_active"]

def assert_transcription_data(transcription: MagicMock, expected_data: Dict[str, Any]):
    """転写データの検証"""
    assert transcription.voice_session_id == expected_data["voice_session_id"]
    assert transcription.speaker_id == expected_data["speaker_id"]
    assert transcription.text_content == expected_data["text_content"]
    assert transcription.confidence_score == expected_data["confidence_score"]
    assert transcription.language == expected_data["language"]
    assert transcription.is_final == expected_data["is_final"]

def assert_billing_data(billing: MagicMock, expected_data: Dict[str, Any]):
    """請求データの検証"""
    assert billing.user_id == expected_data["user_id"]
    assert billing.amount == expected_data["amount"]
    assert billing.currency == expected_data["currency"]
    assert billing.status == expected_data["status"]

def assert_subscription_data(subscription: MagicMock, expected_data: Dict[str, Any]):
    """サブスクリプションデータの検証"""
    assert subscription.user_id == expected_data["user_id"]
    assert subscription.organization_id == expected_data["organization_id"]
    assert subscription.status == expected_data["status"]
    assert subscription.quantity == expected_data["quantity"]
