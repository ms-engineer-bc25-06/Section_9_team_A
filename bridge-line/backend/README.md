# Bridge Line Backend

AI音声チャットアプリケーションのバックエンドAPI

## 技術スタック

- **FastAPI**: Webフレームワーク
- **SQLAlchemy 2.0**: ORM（非同期対応）
- **PostgreSQL**: データベース
- **Alembic**: データベースマイグレーション
- **Pydantic**: データバリデーション
- **Firebase Admin**: 認証
- **Stripe**: 決済処理
- **OpenAI**: AI分析
- **Redis**: キャッシュ・メッセージキュー
- **JWT**: トークン認証

## セットアップ

### 1. 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、必要な環境変数を設定してください：

```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

### 3. データベースのセットアップ

```bash
# PostgreSQLを起動
# データベースを作成
createdb bridge_line

# マイグレーションを実行
alembic upgrade head
```

### 4. アプリケーションの起動

```bash
# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# または
python -m app.main
```

## API ドキュメント

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## プロジェクト構造

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # 認証API
│   │       ├── users.py         # ユーザー管理API
│   │       ├── teams.py         # チーム管理API
│   │       ├── voice_sessions.py # 音声セッションAPI
│   │       ├── transcriptions.py # 文字起こしAPI
│   │       ├── analytics.py     # AI分析API
│   │       ├── billing.py       # 決済API
│   │       ├── subscriptions.py # サブスクリプションAPI
│   │       ├── invitations.py   # 招待API
│   │       └── webhooks.py      # Webhook API
│   ├── core/
│   │   ├── auth.py             # 認証コア
│   │   └── database.py         # データベース設定
│   ├── models/
│   │   └── user.py             # ユーザーモデル
│   ├── schemas/
│   │   └── auth.py             # Pydanticスキーマ
│   ├── services/
│   │   └── auth_service.py     # 認証サービス
│   ├── config.py               # 設定管理
│   └── main.py                 # アプリケーションエントリーポイント
├── alembic/                    # データベースマイグレーション
├── requirements.txt            # Python依存関係
├── alembic.ini               # Alembic設定
└── README.md                 # このファイル
```

## 主要機能

### 認証・認可
- JWTトークン認証
- Firebase認証統合
- パスワードハッシュ化（bcrypt）

### ユーザー管理
- ユーザー登録・ログイン
- プロフィール管理
- アカウント削除

### 音声処理
- 音声セッション管理
- リアルタイム音声処理
- WebSocket通信

### AI分析
- OpenAI統合
- 音声分析
- 感情分析
- 要約生成

### 決済・サブスクリプション
- Stripe統合
- サブスクリプション管理
- 使用量制限

### チーム機能
- チーム作成・管理
- メンバー招待
- 権限管理

## 開発ガイド

### 新しいAPIエンドポイントの追加

1. `app/api/v1/`に新しいルーターファイルを作成
2. `app/api/v1/api.py`にルーターを追加
3. 必要に応じてモデル、スキーマ、サービスを作成

### データベースマイグレーション

```bash
# 新しいマイグレーションを作成
alembic revision --autogenerate -m "Description"

# マイグレーションを適用
alembic upgrade head

# マイグレーションをロールバック
alembic downgrade -1
```

### テスト

```bash
# テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app

# 特定のテストファイル
pytest tests/test_auth.py
```

## デプロイメント

### Docker

```bash
# イメージビルド
docker build -t bridge-line-backend .

# コンテナ実行
docker run -p 8000:8000 bridge-line-backend
```

### 本番環境

1. 環境変数を本番用に設定
2. データベース接続を本番用に設定
3. SSL証明書を設定
4. リバースプロキシ（Nginx）を設定

## トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   - PostgreSQLが起動しているか確認
   - データベースURLが正しいか確認

2. **認証エラー**
   - Firebase設定が正しいか確認
   - JWTシークレットキーが設定されているか確認

3. **CORSエラー**
   - `ALLOWED_HOSTS`にフロントエンドのURLが含まれているか確認

## ライセンス

MIT License 