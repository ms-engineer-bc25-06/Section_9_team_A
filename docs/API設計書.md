# Bridge LINE - API設計書

## **概要**

### システム概要

Bridge LINE BtoB向けチームコミュニケーションアプリケーションのREST API仕様書です。音声チャット、AI分析、チーム管理、決済機能を統合したAPIエンドポイントを定義しています。

### 技術仕様

- **フレームワーク**: FastAPI 0.110.x
- **認証方式**: Firebase Authentication + JWT Bearer Token
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8
- **タイムゾーン**: UTC
- **バージョニング**: URLパス方式 (`/api/v1/`)

### ベースURL

```
開発環境: https://api-dev.bridge-line.com/api/v1
本番環境: https://api.bridge-line.com/api/v1

```

---

## **認証・認可**

### 認証方式

```
CopyAuthorization: Bearer <Firebase_ID_Token>

```

### 権限レベル

| レベル | 説明 | 適用範囲 |
| --- | --- | --- |
| `owner` | チーム所有者 | 全ての操作、決済管理 |
| `admin` | チーム管理者 | メンバー管理、設定変更 |
| `member` | 一般メンバー | セッション参加、分析閲覧 |

### 共通レスポンスヘッダー

```
CopyContent-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200

```

---

## **API エンドポイント一覧**

### **1. 認証 (`/api/v1/auth/`)**

### **POST /auth/login**

Firebase認証後のユーザー登録・ログイン処理

**リクエスト**

```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "display_name": "田中太郎",
  "avatar_url": "https://example.com/avatar.jpg"
}

```

**レスポンス (200)**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "firebase_uid": "firebase_uid_123",
    "email": "tanaka@example.com",
    "display_name": "田中太郎",
    "avatar_url": "https://example.com/avatar.jpg",
    "is_active": true,
    "profile": {
      "bio": null,
      "department": null,
      "position": null,
      "total_chat_sessions": 0
    },
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}

```

### **POST /auth/refresh**

アクセストークンの更新

**リクエスト**

```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}

```

### **POST /auth/logout**

ログアウト処理

**レスポンス (200)**

```json
{
  "message": "Successfully logged out"
}

```

---

### **2. ユーザー管理 (`/api/v1/users/`)**

### **GET /users/me**

現在のユーザー情報取得

**レスポンス (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "firebase_uid": "firebase_uid_123",
  "email": "tanaka@example.com",
  "display_name": "田中太郎",
  "avatar_url": "https://example.com/avatar.jpg",
  "profile": {
    "bio": "プロダクトマネージャーとして5年の経験があります。",
    "department": "プロダクト開発部",
    "position": "プロダクトマネージャー",
    "interests": ["UX/UI", "アジャイル開発", "データ分析"],
    "communication_style": "collaborative",
    "collaboration_score": 8.5,
    "leadership_score": 7.8,
    "empathy_score": 8.2,
    "assertiveness_score": 6.9,
    "creativity_score": 7.5,
    "analytical_score": 8.0,
    "visibility_settings": {
      "bio": true,
      "department": true,
      "position": true,
      "interests": true,
      "scores": true},
    "total_chat_sessions": 45,
    "total_speaking_time_seconds": 18720,
    "last_analysis_at": "2024-01-15T10:30:00Z"
  },
  "teams": [
    {
      "id": "team_id_1",
      "name": "開発チーム",
      "role": "owner"
    }
  ],
  "last_active_at": "2024-01-20T15:30:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}

```

### **PUT /users/me**

ユーザー情報更新

**リクエスト**

```json
{
  "display_name": "田中太郎",
  "avatar_url": "https://example.com/new_avatar.jpg"
}

```

### **GET /users/me/profile**

ユーザープロファイル詳細取得

### **PUT /users/me/profile**

ユーザープロファイル更新

**リクエスト**

```json
{
  "bio": "プロダクトマネージャーとして5年の経験があります。チームビルディングに情熱を注いでいます。",
  "department": "プロダクト開発部",
  "position": "シニアプロダクトマネージャー",
  "interests": ["UX/UI", "アジャイル開発", "データ分析", "チームマネジメント"],
  "visibility_settings": {
    "bio": true,
    "department": true,
    "position": true,
    "interests": true,
    "scores": false}
}

```

### **GET /users/{user_id}**

指定ユーザー情報取得（チームメンバーのみ）

**パラメータ**

- `user_id` (UUID): 取得対象ユーザーID

**レスポンス (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "display_name": "佐藤花子",
  "avatar_url": "https://example.com/avatar2.jpg",
  "profile": {
    "bio": "フロントエンド開発が専門です。",
    "department": "エンジニアリング部",
    "position": "シニアフロントエンドエンジニア",
    "interests": ["React", "TypeScript", "デザインシステム"],
    "communication_style": "analytical",
    "collaboration_score": 7.2,
    "leadership_score": 6.5,
    "total_chat_sessions": 32
  }
}

```

### **DELETE /users/me**

アカウント削除

---

### **3. チーム管理 (`/api/v1/teams/`)**

### **GET /teams**

参加チーム一覧取得

**クエリパラメータ**

- `limit` (int): 取得件数 (default: 20, max: 100)
- `offset` (int): オフセット (default: 0)
- `status` (string): メンバー状態フィルタ (active, inactive, pending)

**レスポンス (200)**

```json
{
  "teams": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "開発チーム",
      "description": "プロダクト開発を担当するメインチーム",
      "member_count": 8,
      "role": "owner",
      "status": "active",
      "owner": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "display_name": "田中太郎",
        "avatar_url": "https://example.com/avatar.jpg"
      },
      "subscription": {
        "plan_type": "premium",
        "status": "active"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "has_more": false}
```

### **POST /teams**

チーム作成

**リクエスト**

```json
{
  "name": "新規開発チーム",
  "description": "新しいプロダクト開発チーム",
  "settings": {
    "auto_transcription": true,
    "ai_analysis": true,
    "max_session_duration": 7200
  }
}

```

**レスポンス (201)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440011",
  "name": "新規開発チーム",
  "description": "新しいプロダクト開発チーム",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "member_count": 1,
  "max_members": 50,
  "settings": {
    "auto_transcription": true,
    "ai_analysis": true,
    "max_session_duration": 7200
  },
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}

```

### **GET /teams/{team_id}**

チーム詳細取得

**レスポンス (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "開発チーム",
  "description": "プロダクト開発を担当するメインチーム",
  "owner": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "田中太郎",
    "avatar_url": "https://example.com/avatar.jpg"
  },
  "members": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "田中太郎",
      "avatar_url": "https://example.com/avatar.jpg",
      "role": "owner",
      "status": "active",
      "profile": {
        "department": "プロダクト開発部",
        "position": "プロダクトマネージャー",
        "communication_style": "collaborative"
      },
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ],
  "member_count": 8,
  "max_members": 50,
  "settings": {
    "auto_transcription": true,
    "ai_analysis": true,
    "max_session_duration": 7200
  },
  "subscription": {
    "plan_type": "premium",
    "status": "active",
    "current_period_end": "2024-02-01T00:00:00Z"
  },
  "analytics": {
    "total_sessions": 156,
    "total_duration_seconds": 450000,
    "avg_session_duration": 2885,
    "last_session_at": "2024-01-19T14:30:00Z"
  },
  "created_at": "2024-01-01T00:00:00Z"
}

```

### **PUT /teams/{team_id}**

チーム情報更新 (owner/admin)

**リクエスト**

```json
{
  "name": "開発チーム（更新）",
  "description": "更新されたチーム説明",
  "settings": {
    "auto_transcription": true,
    "ai_analysis": true,
    "max_session_duration": 9000
  }
}

```

### **DELETE /teams/{team_id}**

チーム削除 (owner)

### **GET /teams/{team_id}/members**

チームメンバー一覧取得

**クエリパラメータ**

- `role` (string): 役割フィルタ (owner, admin, member)
- `status` (string): 状態フィルタ (active, inactive, pending)

### **PUT /teams/{team_id}/members/{user_id}**

メンバー役割・状態更新 (owner/admin)

**リクエスト**

```json
{
  "role": "admin",
  "status": "active"
}

```

### **DELETE /teams/{team_id}/members/{user_id}**

メンバー削除 (owner/admin)

### **GET /teams/{team_id}/analytics**

チーム分析データ取得

**クエリパラメータ**

- `period` (string): 期間 (7d, 30d, 90d, all)
- `metrics` (array): 取得メトリクス指定

**レスポンス (200)**

```json
{
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "period": "30d",
  "summary": {
    "total_sessions": 45,
    "total_duration_seconds": 162000,
    "avg_session_duration": 3600,
    "total_participants": 8,
    "avg_participation_rate": 0.75
  },
  "member_analytics": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "田中太郎",
      "participation_count": 38,
      "total_speaking_time": 28800,
      "avg_speaking_ratio": 0.25,
      "collaboration_score": 8.5,
      "communication_style": "collaborative"
    }
  ],
  "communication_patterns": {
    "dominant_styles": ["collaborative", "analytical"],
    "interaction_balance": 0.82,
    "leadership_distribution": [
      {"user_id": "550e8400-e29b-41d4-a716-446655440000", "leadership_instances": 12}
    ]
  },
  "generated_at": "2024-01-20T10:00:00Z"
}

```

---

### **4. 音声セッション (`/api/v1/voice-sessions/`)**

### **GET /voice-sessions**

音声セッション一覧取得

**クエリパラメータ**

- `team_id` (UUID): チームIDフィルタ
- `status` (string): 状態フィルタ (waiting, active, completed, cancelled)
- `limit` (int): 取得件数 (default: 20)
- `offset` (int): オフセット

**レスポンス (200)**

```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "team_id": "550e8400-e29b-41d4-a716-446655440010",
      "team_name": "開発チーム",
      "title": "週次レビューミーティング",
      "description": "今週のスプリントレビューと来週の計画",
      "status": "completed",
      "started_at": "2024-01-19T14:00:00Z",
      "ended_at": "2024-01-19T15:30:00Z",
      "duration_seconds": 5400,
      "participant_count": 6,
      "has_transcription": true,
      "has_analysis": true,
      "created_at": "2024-01-19T13:45:00Z"
    }
  ],
  "total": 156,
  "has_more": true}

```

### **POST /voice-sessions**

音声セッション作成

**リクエスト**

```json
{
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "緊急ミーティング",
  "description": "システム障害対応について",
  "max_participants": 10,
  "settings": {
    "auto_recording": true,
    "auto_transcription": true,
    "quality": "high"
  }
}

```

**レスポンス (201)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440021",
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "title": "緊急ミーティング",
  "description": "システム障害対応について",
  "status": "waiting",
  "participant_count": 0,
  "max_participants": 10,
  "join_url": "https://app.bridge-line.com/voice-chat/550e8400-e29b-41d4-a716-446655440021",
  "settings": {
    "auto_recording": true,
    "auto_transcription": true,
    "quality": "high"
  },
  "created_at": "2024-01-20T10:15:00Z"
}

```

### **GET /voice-sessions/{session_id}**

音声セッション詳細取得

**レスポンス (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440020",
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "team_name": "開発チーム",
  "title": "週次レビューミーティング",
  "description": "今週のスプリントレビューと来週の計画",
  "status": "completed",
  "started_at": "2024-01-19T14:00:00Z",
  "ended_at": "2024-01-19T15:30:00Z",
  "duration_seconds": 5400,
  "participants": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "田中太郎",
      "avatar_url": "https://example.com/avatar.jpg",
      "role": "owner",
      "joined_at": "2024-01-19T14:00:00Z",
      "left_at": "2024-01-19T15:30:00Z",
      "speaking_time_seconds": 1350
    }
  ],
  "recording": {
    "url": "https://storage.bridge-line.com/recordings/session_20240119_140000.mp3",
    "size_bytes": 25600000,
    "duration_seconds": 5400
  },
  "transcription_count": 847,
  "analysis_count": 5,
  "settings": {
    "auto_recording": true,
    "auto_transcription": true,
    "quality": "high"
  },
  "created_at": "2024-01-19T13:45:00Z"
}

```

### **PUT /voice-sessions/{session_id}**

音声セッション更新

**リクエスト**

```json
{
  "title": "週次レビューミーティング（更新）",
  "description": "更新された説明"
}

```

### **POST /voice-sessions/{session_id}/start**

音声セッション開始

**レスポンス (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440020",
  "status": "active",
  "started_at": "2024-01-20T10:30:00Z",
  "websocket_url": "wss://ws.bridge-line.com/voice-sessions/550e8400-e29b-41d4-a716-446655440020"
}

```

### **POST /voice-sessions/{session_id}/end**

音声セッション終了

### **POST /voice-sessions/{session_id}/join**

音声セッション参加

### **POST /voice-sessions/{session_id}/leave**

音声セッション退出

### **DELETE /voice-sessions/{session_id}**

音声セッション削除 (owner/admin)

---

### **5. 文字起こし (`/api/v1/transcriptions/`)**

### **GET /transcriptions**

文字起こし一覧取得

**クエリパラメータ**

- `session_id` (UUID): セッションIDフィルタ
- `speaker_id` (UUID): 発話者IDフィルタ
- `search` (string): テキスト検索
- `limit` (int): 取得件数
- `offset` (int): オフセット

**レスポンス (200)**

```json
{
  "transcriptions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440030",
      "voice_session_id": "550e8400-e29b-41d4-a716-446655440020",
      "speaker": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "display_name": "田中太郎",
        "avatar_url": "https://example.com/avatar.jpg"
      },
      "text_content": "今週のスプリントでは、ユーザーダッシュボードの機能実装を完了しました。",
      "start_time_seconds": 125.5,
      "end_time_seconds": 132.8,
      "confidence_score": 0.95,
      "language": "ja",
      "processed_at": "2024-01-19T15:35:00Z"
    }
  ],
  "total": 847,
  "has_more": true}

```

### **GET /transcriptions/{session_id}**

指定セッションの文字起こし取得

**クエリパラメータ**

- `format` (string): レスポンス形式 (json, srt, txt)

**レスポンス (200) - format=json**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440020",
  "session_title": "週次レビューミーティング",
  "transcriptions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440030",
      "speaker": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "display_name": "田中太郎"
      },
      "text_content": "今週のスプリントでは、ユーザーダッシュボードの機能実装を完了しました。",
      "start_time_seconds": 125.5,
      "end_time_seconds": 132.8,
      "confidence_score": 0.95
    }
  ],
  "total_count": 847,
  "total_duration_seconds": 5400,
  "generated_at": "2024-01-19T15:35:00Z"
}

```

### **GET /transcriptions/{transcription_id}**

文字起こし詳細取得

### **PUT /transcriptions/{transcription_id}**

文字起こし修正 (発話者のみ)

**リクエスト**

```json
{
  "text_content": "今週のスプリントでは、ユーザーダッシュボードの新機能実装を完了しました。"
}

```

### **POST /transcriptions/search**

文字起こし全文検索

**リクエスト**

```json
Copy{
  "query": "ダッシュボード",
  "team_ids": ["550e8400-e29b-41d4-a716-446655440010"],
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-01-31T23:59:59Z",
  "speaker_ids": [],
  "limit": 50
}

```

---

### **6. AI分析 (`/api/v1/analytics/`)**

### **GET /analytics/sessions/{session_id}**

セッション分析結果取得

**レスポンス (200)**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440020",
  "session_title": "週次レビューミーティング",
  "analyses": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440040",
      "analysis_type": "communication_analysis",
      "result": {
        "speaking_distribution": [
          {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "display_name": "田中太郎",
            "speaking_time_ratio": 0.25,
            "speaking_time_seconds": 1350,
            "interruption_count": 2,
            "question_count": 5
          }
        ],
        "communication_flow": {
          "dominant_speakers": ["550e8400-e29b-41d4-a716-446655440000"],
          "interaction_matrix": {
            "田中太郎_佐藤花子": 12,
            "佐藤花子_鈴木次郎": 8
          },
          "turn_taking_balance": 0.78
        }
      },
      "confidence_score": 0.89,
      "model_version": "gpt-4o-2024-01-15",
      "processing_time_ms": 2450,
      "created_at": "2024-01-19T15:45:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440041",
      "analysis_type": "sentiment_analysis",
      "result": {
        "overall_sentiment": {
          "positive": 0.65,
          "neutral": 0.25,
          "negative": 0.10
        },
        "sentiment_timeline": [
          {
            "time_range": "0-300",
            "sentiment": "positive",
            "confidence": 0.82
          }
        ],
        "participant_sentiments": [
          {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "display_name": "田中太郎",
            "avg_sentiment": "positive",
            "sentiment_score": 0.72
          }
        ]
      },
      "confidence_score": 0.85,
      "created_at": "2024-01-19T15:47:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440042",
      "analysis_type": "personality_analysis",
      "result": {
        "team_dynamics": {
          "collaboration_level": 8.2,
          "leadership_clarity": 7.5,
          "decision_making_style": "collaborative",
          "conflict_resolution": "constructive"
        },
        "individual_insights": [
          {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "display_name": "田中太郎",
            "communication_traits": [
              "facilitator",
              "question_asker",
              "summarizer"
            ],
            "leadership_indicators": {
              "direction_setting": 8.1,
              "consensus_building": 8.7,
              "decision_facilitation": 7.9
            }
          }
        ]
      },
      "personality_insights": {
        "primary_communication_style": "collaborative",
        "secondary_traits": ["analytical", "empathetic"]
      },
      "behavioral_scores": {
        "collaboration": 8.5,
        "leadership": 7.8,
        "empathy": 8.2,
        "assertiveness": 6.9,
        "creativity": 7.5,
        "analytical": 8.0
      },
      "confidence_score": 0.91,
      "created_at": "2024-01-19T15:50:00Z"
    }
  ],
  "summary": {
    "key_insights": [
      "チーム全体のコラボレーション度が高く、建設的な議論が行われました",
      "田中さんがファシリテーター役を担い、効果的に会議を進行しました",
      "技術的な議論において分析的なアプローチが多く見られました"
    ],
    "improvement_suggestions": [
      "発話時間の分散をより均等にすることで、全員の意見をより引き出せます",
      "意思決定プロセスをより明確化することで効率を向上できます"
    ],
    "overall_score": 8.2
  },
  "generated_at": "2024-01-19T15:55:00Z"
}

```

### **GET /analytics/teams/{team_id}**

チーム分析結果取得（上記チーム管理の `/teams/{team_id}/analytics` と同一）

### **GET /analytics/users/{user_id}**

個人分析結果取得

**クエリパラメータ**

- `period` (string): 期間 (7d, 30d, 90d, all)
- `team_id` (UUID): チームIDフィルタ

**レスポンス (200)**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "田中太郎",
  "period": "30d",
  "profile": {
    "current_scores": {
      "collaboration_score": 8.5,
      "leadership_score": 7.8,
      "empathy_score": 8.2,
      "assertiveness_score": 6.9,
      "creativity_score": 7.5,
      "analytical_score": 8.0
    },
    "communication_style": "collaborative",
    "total_chat_sessions": 45,
    "total_speaking_time_seconds": 18720
  },
  "activity_summary": {
    "sessions_participated": 38,
    "avg_speaking_time_per_session": 492,
    "participation_rate": 0.84,
    "initiative_taken": 12,
    "questions_asked": 89,
    "suggestions_made": 34
  },
  "communication_patterns": {
    "preferred_interaction_style": "facilitating",
    "speaking_rhythm": "measured",
    "interruption_tendency": "low",
    "question_frequency": "high",
    "sentiment_trend": "consistently_positive"
  },
  "growth_tracking": {
    "score_changes": {
      "collaboration_score": {
        "previous": 8.2,
        "current": 8.5,
        "change": +0.3
      },
      "leadership_score": {
        "previous": 7.5,
        "current": 7.8,
        "change": +0.3
      }
    },
    "skill_development": [
      {
        "skill": "consensus_building",
        "improvement": 0.4,
        "evidence": "より多くの意見調整を主導"
      }
    ]
  },
  "recommendations": [
    {
      "category": "communication",
      "suggestion": "他のメンバーの発話時間を意識的に確保することで、さらに協調的なリーダーシップを発揮できます",
      "priority": "medium"
    }
  ],
  "generated_at": "2024-01-20T10:00:00Z"
}

```

### **POST /analytics/sessions/{session_id}/generate**

セッション分析実行

**リクエスト**

```json
{
  "analysis_types": ["communication_analysis", "sentiment_analysis", "personality_analysis"]
}

```

### **GET /analytics/reports**

分析レポート一覧取得

### **POST /analytics/reports**

カスタム分析レポート生成

**リクエスト**

```json
{
  "name": "月次チーム分析レポート",
  "team_ids": ["550e8400-e29b-41d4-a716-446655440010"],
  "date_range": {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-31T23:59:59Z"
  },
  "metrics": [
    "communication_patterns",
    "team_dynamics",
    "individual_growth",
    "collaboration_insights"
  ],
  "format": "pdf"
}

```

---

### **7. 決済管理 (`/api/v1/billing/`)**

### **GET /billing/teams/{team_id}**

チーム決済情報取得 (owner/admin)

**レスポンス (200)**

```json
{
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "team_name": "開発チーム",
  "subscription": {
    "id": "550e8400-e29b-41d4-a716-446655440050",
    "stripe_subscription_id": "sub_1234567890",
    "plan_type": "premium",
    "status": "active",
    "current_period_start": "2024-01-01T00:00:00Z",
    "current_period_end": "2024-02-01T00:00:00Z",
    "monthly_price": 2980.00,
    "currency": "JPY",
    "trial_end": null,
    "next_billing_date": "2024-02-01T00:00:00Z"
  },
  "usage": {
    "current_period": {
      "sessions_conducted": 45,
      "total_minutes": 2700,
      "transcription_minutes": 2700,
      "ai_analyses_count": 180,
      "storage_used_mb": 1250
    },
    "plan_limits": {
      "max_sessions_per_month": 200,
      "max_minutes_per_month": 12000,
      "max_transcription_minutes": 12000,
      "max_ai_analyses": 800,
      "max_storage_gb": 10
    }
  },
  "next_invoice": {
    "amount": 2980.00,
    "currency": "JPY",
    "date": "2024-02-01T00:00:00Z"
  }
}

```

### **GET /billing/teams/{team_id}/history**

決済履歴取得 (owner/admin)

**クエリパラメータ**

- `limit` (int): 取得件数 (default: 20)
- `starting_after` (string): ページネーション用カーソル

**レスポンス (200)**

```json
{
  "billing_histories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440060",
      "stripe_invoice_id": "in_1234567890",
      "amount": 2980.00,
      "currency": "JPY",
      "status": "paid",
      "billing_reason": "subscription_cycle",
      "period_start": "2024-01-01T00:00:00Z",
      "period_end": "2024-02-01T00:00:00Z",
      "paid_at": "2024-01-01T09:15:00Z",
      "invoice_pdf_url": "https://pay.stripe.com/invoice/acct_1234/test_1234/pdf",
      "line_items": [
        {
          "description": "Premium Plan - 開発チーム",
          "amount": 2980.00,
          "quantity": 1
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "has_more": false,
  "total_count": 12
}

```

### **GET /billing/teams/{team_id}/usage**

利用状況詳細取得 (owner/admin)

### **POST /billing/teams/{team_id}/payment-method**

支払い方法更新 (owner)

**リクエスト**

```json
{
  "payment_method_id": "pm_1234567890"
}

```

### **GET /billing/invoices/{invoice_id}**

請求書詳細取得

### **POST /billing/invoices/{invoice_id}/pay**

請求書手動支払い

---

### **8. サブスクリプション (`/api/v1/subscriptions/`)**

### **GET /subscriptions/plans**

利用可能プラン一覧取得

**レスポンス (200)**

```json
{
  "plans": [
    {
      "id": "basic",
      "name": "Basic Plan",
      "description": "小規模チーム向けの基本プラン",
      "monthly_price": 980.00,
      "currency": "JPY",
      "features": {
        "max_team_members": 5,
        "max_sessions_per_month": 50,
        "max_minutes_per_month": 3000,
        "transcription_included": true,
        "basic_ai_analysis": true,
        "storage_gb": 2,
        "support_level": "email"
      },
      "trial_days": 14
    },
    {
      "id": "premium",
      "name": "Premium Plan",
      "description": "中規模チーム向けの高機能プラン",
      "monthly_price": 2980.00,
      "currency": "JPY",
      "features": {
        "max_team_members": 20,
        "max_sessions_per_month": 200,
        "max_minutes_per_month": 12000,
        "transcription_included": true,
        "advanced_ai_analysis": true,
        "custom_reports": true,
        "storage_gb": 10,
        "support_level": "chat"
      },
      "trial_days": 14
    },
    {
      "id": "enterprise",
      "name": "Enterprise Plan",
      "description": "大規模組織向けのエンタープライズプラン",
      "monthly_price": 9800.00,
      "currency": "JPY",
      "features": {
        "max_team_members": "unlimited",
        "max_sessions_per_month": "unlimited",
        "max_minutes_per_month": "unlimited",
        "transcription_included": true,
        "advanced_ai_analysis": true,
        "custom_reports": true,
        "api_access": true,
        "sso_integration": true,
        "storage_gb": 100,
        "support_level": "phone"
      },
      "trial_days": 30,
      "custom_pricing": true}
  ]
}

```

### **POST /subscriptions/teams/{team_id}/subscribe**

サブスクリプション開始 (owner)

**リクエスト**

```json
Copy{
  "plan_id": "premium",
  "payment_method_id": "pm_1234567890",
  "trial": true}

```

**レスポンス (201)**

```json
Copy{
  "subscription": {
    "id": "550e8400-e29b-41d4-a716-446655440050",
    "stripe_subscription_id": "sub_1234567890",
    "plan_type": "premium",
    "status": "trialing",
    "current_period_start": "2024-01-20T10:00:00Z",
    "current_period_end": "2024-02-20T10:00:00Z",
    "trial_end": "2024-02-03T10:00:00Z",
    "monthly_price": 2980.00,
    "currency": "JPY"
  },
  "client_secret": "pi_1234567890_secret_abcdef"
}
```

### **PUT /subscriptions/teams/{team_id}**

サブスクリプション変更 (owner)

**リクエスト**

```json
Copy{
  "plan_id": "enterprise",
  "proration_behavior": "create_prorations"
}

```

### **DELETE /subscriptions/teams/{team_id}**

サブスクリプション解約 (owner)

**リクエスト**

```json
Copy{
  "cancel_at_period_end": true,
  "cancellation_reason": "cost_reduction"
}

```

### **POST /subscriptions/teams/{team_id}/reactivate**

サブスクリプション再開 (owner)

---

### **9. 招待管理 (`/api/v1/invitations/`)**

### **GET /invitations**

送信した招待一覧取得

**クエリパラメータ**

- `team_id` (UUID): チームIDフィルタ
- `status` (string): 状態フィルタ (pending, accepted, declined, expired)

**レスポンス (200)**

```json
Copy{
  "invitations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440070",
      "team": {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "name": "開発チーム"
      },
      "email": "yamada@example.com",
      "role": "member",
      "status": "pending",
      "expires_at": "2024-01-27T10:00:00Z",
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 3,
  "has_more": false}

```

### **POST /invitations**

チームメンバー招待 (owner/admin)

**リクエスト**

```json
Copy{
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "email": "yamada@example.com",
  "role": "member",
  "message": "開発チームにご参加いただければと思います。よろしくお願いします。"
}

```

**レスポンス (201)**

```json
Copy{
  "id": "550e8400-e29b-41d4-a716-446655440070",
  "team_id": "550e8400-e29b-41d4-a716-446655440010",
  "email": "yamada@example.com",
  "role": "member",
  "status": "pending",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "invite_url": "https://app.bridge-line.com/invite/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-01-27T10:00:00Z",
  "created_at": "2024-01-20T10:00:00Z"
}

```

### **GET /invitations/{token}**

招待情報取得（トークンベース）

**レスポンス (200)**

```json
Copy{
  "invitation": {
    "id": "550e8400-e29b-41d4-a716-446655440070",
    "team": {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "開発チーム",
      "description": "プロダクト開発を担当するメインチーム",
      "member_count": 8,
      "owner": {
        "display_name": "田中太郎",
        "avatar_url": "https://example.com/avatar.jpg"
      }
    },
    "role": "member",
    "inviter": {
      "display_name": "田中太郎",
      "avatar_url": "https://example.com/avatar.jpg"
    },
    "expires_at": "2024-01-27T10:00:00Z",
    "created_at": "2024-01-20T10:00:00Z"
  },
  "is_valid": true}

```

### **POST /invitations/{token}/accept**

招待承諾

**レスポンス (200)**

```json
Copy{
  "message": "招待を承諾しました",
  "team": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "name": "開発チーム"
  },
  "role": "member"
}

```

### **POST /invitations/{token}/decline**

招待辞退

### **DELETE /invitations/{invitation_id}**

招待取り消し (送信者/owner/admin)

### **POST /invitations/{invitation_id}/resend**

招待再送信 (owner/admin)

---

### **10. Webhook (`/api/v1/webhooks/`)**

### **POST /webhooks/stripe**

Stripe Webhook処理

**リクエストヘッダー**

```
CopyStripe-Signature: t=1640995200,v1=abcdef...

```

**処理対象イベント**

- `invoice.payment_succeeded`: 請求書支払い成功
- `invoice.payment_failed`: 請求書支払い失敗
- `customer.subscription.updated`: サブスクリプション更新
- `customer.subscription.deleted`: サブスクリプション削除

**レスポンス (200)**

```json
Copy{
  "received": true,
  "event_id": "evt_1234567890"
}

```

### **POST /webhooks/firebase**

Firebase Webhook処理

---

## **WebSocket API**

### **接続URL**

```
wss://ws.bridge-line.com/voice-sessions/{session_id}?token={jwt_token}

```

### **メッセージ形式**

### **接続時認証**

```json
Copy{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

```

### **参加者入室通知**

```json
Copy{
  "type": "user_joined",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "display_name": "田中太郎",
    "avatar_url": "https://example.com/avatar.jpg"
  },
  "timestamp": "2024-01-20T10:30:00Z"
}

```

### **音声データ送信**

```json
Copy{
  "type": "audio_data",
  "data": "base64_encoded_audio_data",
  "timestamp": "2024-01-20T10:30:15.123Z",
  "chunk_id": "chunk_001"
}

```

### **リアルタイム文字起こし**

```json
Copy{
  "type": "transcription_partial",
  "speaker_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "今週のスプリントでは",
  "is_final": false,
  "confidence": 0.85,
  "timestamp": "2024-01-20T10:30:15.123Z"
}

```

### **文字起こし確定**

```json
Copy{
  "type": "transcription_final",
  "transcription": {
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "speaker_id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "今週のスプリントでは、ユーザーダッシュボードの機能実装を完了しました。",
    "start_time_seconds": 125.5,
    "end_time_seconds": 132.8,
    "confidence": 0.95
  }
}

```

### **参加者退室通知**

```json
Copy{
  "type": "user_left",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-20T11:30:00Z"
}

```

---

## **エラーハンドリング**

### **標準エラーレスポンス形式**

```json
Copy{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "リクエスト内容に不備があります",
    "details": {
      "field": "email",
      "reason": "無効なメールアドレス形式です"
    },
    "request_id": "req_1234567890",
    "timestamp": "2024-01-20T10:30:00Z"
  }
}

```

### **HTTPステータスコードとエラーコード対応表**

| HTTPコード | エラーコード | 説明 | 例 |
| --- | --- | --- | --- |
| 400 | `INVALID_REQUEST` | リクエスト形式エラー | 必須フィールド不足 |
| 401 | `UNAUTHORIZED` | 認証エラー | トークン無効 |
| 403 | `FORBIDDEN` | 認可エラー | 権限不足 |
| 404 | `NOT_FOUND` | リソース存在しない | チームID不正 |
| 409 | `CONFLICT` | 競合エラー | 重複データ |
| 422 | `VALIDATION_ERROR` | バリデーションエラー | 入力値不正 |
| 429 | `RATE_LIMIT_EXCEEDED` | レート制限超過 | API呼び出し過多 |
| 500 | `INTERNAL_ERROR` | サーバー内部エラー | システム障害 |
| 503 | `SERVICE_UNAVAILABLE` | サービス利用不可 | メンテナンス中 |

### **詳細エラーコード**

### **認証関連**

- `AUTH_TOKEN_EXPIRED`: 認証トークン期限切れ
- `AUTH_TOKEN_INVALID`: 認証トークン不正
- `FIREBASE_AUTH_ERROR`: Firebase認証エラー

### **認可関連**

- `INSUFFICIENT_PERMISSIONS`: 権限不足
- `TEAM_ACCESS_DENIED`: チームアクセス拒否
- `SUBSCRIPTION_REQUIRED`: サブスクリプション必要

### **リソース関連**

- `TEAM_NOT_FOUND`: チーム存在しない
- `USER_NOT_FOUND`: ユーザー存在しない
- `SESSION_NOT_FOUND`: セッション存在しない

### **ビジネスロジック関連**

- `TEAM_MEMBER_LIMIT_EXCEEDED`: チームメンバー数上限
- `SESSION_LIMIT_EXCEEDED`: セッション数上限
- `STORAGE_LIMIT_EXCEEDED`: ストレージ容量上限
- `SUBSCRIPTION_INACTIVE`: サブスクリプション非アクティブ

### **決済関連**

- `PAYMENT_REQUIRED`: 支払い必要
- `PAYMENT_FAILED`: 決済失敗
- `SUBSCRIPTION_PAST_DUE`: サブスクリプション支払い延滞

---

## **レート制限**

### **制限レベル**

| エンドポイントタイプ | 制限 | ウィンドウ | 備考 |
| --- | --- | --- | --- |
| 認証関連 | 10 req/min | ユーザー単位 | ログイン試行制限 |
| 一般API | 1000 req/hour | ユーザー単位 | 通常操作 |
| 音声アップロード | 50 req/hour | チーム単位 | 音声データ処理 |
| AI分析要求 | 100 req/day | チーム単位 | 処理コスト制限 |
| Webhook | 10000 req/hour | IP単位 | 外部サービス連携 |

### **レート制限ヘッダー**

```
CopyX-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60

```

---

## **APIパフォーマンス**

### **レスポンス時間目標**

| エンドポイントタイプ | 目標レスポンス時間 | 最大許容時間 |
| --- | --- | --- |
| 認証 | < 200ms | 1s |
| データ取得 | < 500ms | 2s |
| データ更新 | < 1s | 3s |
| AI分析 | < 30s | 60s |
| ファイルアップロード | < 10s | 30s |

### **ペイロードサイズ制限**

- **通常API**: 1MB
- **音声ファイル**: 100MB
- **画像ファイル**: 10MB
- **テキストデータ**: 1MB

---

## **セキュリティ対策**

### **認証・認可**

- Firebase Authentication による OAuth2.0/OIDC
- JWT Bearer Token による API認証
- ロールベースアクセス制御 (RBAC)
- セッション管理とトークンローテーション

### **データ保護**

- HTTPS強制 (TLS 1.3)
- SQLインジェクション対策 (SQLAlchemy ORM)
- XSS対策 (入力値サニタイズ)
- CSRF対策 (トークンベース)

### **レート制限・監視**

- IP・ユーザー・チーム単位でのレート制限
- 異常アクセスパターンの検出
- 監査ログの保存
- リアルタイム監視とアラート