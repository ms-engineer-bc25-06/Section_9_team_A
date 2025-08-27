# 🚀 Bridge Line チーム開発環境セットアップガイド

このガイドに従って、チーム開発環境を構築してください。

## 📋 前提条件

- Docker Desktop がインストールされていること
- Git がインストールされていること
- Node.js 18以上がインストールされていること（フロントエンド用）

## 🛠️ セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd Section_9_team_A
```

### 2. 環境変数の設定

#### バックエンド用
`.env`ファイルを作成（既に存在する場合は編集）：

```env
# データベース設定
DATABASE_URL=postgresql+asyncpg://bridge_user:bridge_password@localhost:5432/bridge_line_db
TEST_DATABASE_URL=postgresql+asyncpg://bridge_user:bridge_password@localhost:5432/bridge_line_test_db

# Redis設定
REDIS_URL=redis://localhost:6379

# セキュリティ設定
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API設定
API_V1_STR=/api/v1
PROJECT_NAME=Bridge Line API

# CORS設定
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# 環境設定
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Firebase設定（必要に応じて）
GOOGLE_APPLICATION_CREDENTIALS=firebase-admin-key.json

# OpenAI設定（必要に応じて）
OPENAI_PERSONAL_API_KEY=your-openai-api-key
```

#### フロントエンド用
`frontend/.env.local`ファイルを作成：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. データベースとバックエンドの起動

#### macOS/Linux の場合：
```bash
chmod +x scripts/team-setup.sh
./scripts/team-setup.sh
```

#### Windows の場合：
```cmd
scripts\team-setup.bat
```

または手動で実行：

```bash
# Dockerコンテナの停止と削除
docker-compose down -v

# データベースボリュームの削除
docker volume rm section_9_team_a_postgres_data

# Dockerコンテナの起動
docker-compose up -d

# データベースの準備完了を待機（30秒）
sleep 30

# マイグレーションの実行
cd backend
docker-compose exec backend alembic upgrade head

# 初期データの投入
docker-compose exec postgres psql -U bridge_user -d bridge_line_db -f /docker-entrypoint-initdb.d/export_current_data.sql
```

### 4. フロントエンドの起動

```bash
cd frontend
npm install
npm run dev
```

## 📊 利用可能なユーザー

セットアップ完了後、以下のユーザーでログインできます：

### 管理者
- **メール**: admin@example.com
- **権限**: 管理者権限

### テストユーザー
- **test-1@example.com** - 宮崎大輝（企画部）
- **test-2@example.com** - 藤井隼人（人事部）
- **test-3@example.com** - 真田梨央（経理部）
- **test-4@example.com** - 橘しおり（経理部）

### チームメンバー
- **kodai@bridgeline.com** - 朝宮優（企画部）
- **ucchi@bridgeline.com** - 加瀬賢一郎（人事部）
- **asuka@bridgeline.com** - 野口 明日香（企画部）
- **rui@bridgeline.com** - 大村 瑠衣（企画部）
- **shizuka@bridgeline.com** - 渡部 志津香（企画部）
- **erika@bridgeline.com** - 中川 えりか（企画部）

> ⚠️ **注意**: パスワードは管理者にお問い合わせください。

## 🌐 アクセスURL

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **データベース**: localhost:5432
  - ユーザー: bridge_user
  - パスワード: bridge_password
  - データベース: bridge_line_db

## 🔧 開発用コマンド

### データベース関連
```bash
# マイグレーションの実行
docker-compose exec backend alembic upgrade head

# マイグレーションの作成
docker-compose exec backend alembic revision --autogenerate -m "description"

# データベースのリセット
docker-compose down -v
docker-compose up -d
```

### ログの確認
```bash
# バックエンドのログ
docker-compose logs -f backend

# データベースのログ
docker-compose logs -f postgres

# Redisのログ
docker-compose logs -f redis
```

### コンテナの管理
```bash
# 全コンテナの停止
docker-compose down

# 全コンテナの停止とボリューム削除
docker-compose down -v

# コンテナの再起動
docker-compose restart
```

## 🐛 トラブルシューティング

### データベース接続エラー
```bash
# データベースコンテナの状態確認
docker-compose ps postgres

# データベースへの接続テスト
docker-compose exec postgres psql -U bridge_user -d bridge_line_db -c "SELECT 1;"
```

### ポート競合エラー
```bash
# 使用中のポートを確認
netstat -an | grep :5432
netstat -an | grep :8000
netstat -an | grep :3000

# 競合するプロセスを停止
# または、compose.yamlでポート番号を変更
```

### マイグレーションエラー
```bash
# マイグレーション履歴の確認
docker-compose exec backend alembic history

# 特定のマイグレーションまで戻す
docker-compose exec backend alembic downgrade <revision>
```

## 📝 注意事項

1. **データベースの永続化**: データベースのデータはDockerボリュームに保存されます
2. **環境変数**: 本番環境では適切な環境変数を設定してください
3. **セキュリティ**: 開発環境用の設定なので、本番環境では変更してください
4. **バックアップ**: 重要なデータは定期的にバックアップを取ってください

## 🤝 チーム開発のベストプラクティス

1. **ブランチ戦略**: feature/機能名 のブランチを作成して開発
2. **コミットメッセージ**: 明確で分かりやすいコミットメッセージを書く
3. **プルリクエスト**: コードレビューを必ず行う
4. **テスト**: 新機能追加時はテストも追加する
5. **ドキュメント**: API変更時はドキュメントも更新する

## 📞 サポート

問題が発生した場合は、チームリーダーまたは管理者にお問い合わせください。
