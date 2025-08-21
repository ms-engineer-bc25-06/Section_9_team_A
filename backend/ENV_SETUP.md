# 環境変数設定ガイド

## 概要
BridgeLINEアプリケーションの環境変数設定方法について説明します。

## 必要な環境変数

### 1. 基本設定
```bash
# 環境設定
ENVIRONMENT=development  # development または production
DEBUG=true              # development: true, production: false
```

### 2. OpenAI API設定
```bash
# 個人APIキー（推奨）
OPENAI_PERSONAL_API_KEY=sk-...

# 従来のAPIキー（後方互換性のため）
OPENAI_API_KEY=sk-...
```

### 3. データベース設定
```bash
# 開発環境
DATABASE_URL=postgresql+asyncpg://bridge_user:bridge_password@postgres:5432/bridge_line_db

# 本番環境
DATABASE_URL=postgresql+asyncpg://bridge_user:${POSTGRES_PASSWORD}@postgres:5432/bridge_line_db
```

### 4. Redis設定
```bash
# 開発環境
REDIS_URL=redis://redis:6379

# 本番環境
REDIS_URL=redis://redis:6379
```

## 環境別設定

### 開発環境 (.env)
```bash
ENVIRONMENT=development
DEBUG=true
OPENAI_PERSONAL_API_KEY=your_personal_api_key_here
```

### 本番環境 (環境変数)
```bash
ENVIRONMENT=production
DEBUG=false
OPENAI_PERSONAL_API_KEY=your_personal_api_key_here
```

## APIキーの優先順位

### 全環境共通
1. `OPENAI_PERSONAL_API_KEY` (優先)
2. `OPENAI_API_KEY` (フォールバック)

## 設定方法

### 1. 開発環境
```bash
# backend/.env ファイルを作成
cp backend/.env.example backend/.env

# ファイルを編集して実際の値を設定
nano backend/.env
```

### 2. 本番環境
```bash
# 環境変数を直接設定
export ENVIRONMENT=production
export DEBUG=false
export OPENAI_PERSONAL_API_KEY=your_personal_api_key_here

# または、.envファイルを使用
cp backend/.env.example backend/.env
# 本番環境用の値を設定
```

### 3. Docker Compose
```bash
# 開発環境
docker compose up --build

# 本番環境
docker compose -f compose.prod.yaml up --build
```

## 注意事項

1. **APIキーの管理**: APIキーは機密情報です。`.env`ファイルをGitにコミットしないでください。
2. **環境の分離**: 開発環境と本番環境で異なるAPIキーを使用してください。
3. **フォールバック**: 適切なAPIキーが設定されていない場合、アプリケーションは起動しません。

## トラブルシューティング

### よくあるエラー

#### OpenAI APIキーエラー
```
ValueError: OpenAI API key not found for environment: production
```
**解決方法**: 適切な環境変数を設定してください。

#### Firebase認証エラー
```
Firebase initialization failed: Failed to initialize a certificate credential
```
**解決方法**: Firebase設定ファイルの設定を確認してください。

## サポート

環境変数の設定で問題が発生した場合は、以下を確認してください：
1. 環境変数名のスペル
2. 値の形式
3. ファイルの権限
4. Docker Composeの設定
