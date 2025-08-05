# Bridge Line - AI音声チャットアプリケーション

## クイックスタート（チーム開発用）

### 前提条件
- Docker Desktop がインストールされていること
- Git がインストールされていること

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd bridge-line
```

### 2. 環境構築（全OS共通）

#### 自動セットアップ（推奨）
```bash
# セットアップスクリプトの実行
make setup
```

#### 手動セットアップ
```bash
# Docker環境の起動
docker-compose up --build -d

# サービスの状態確認
docker-compose ps

# ログの確認
docker-compose logs -f backend
```

### 3. 開発用コマンド

#### バックエンド関連
```bash
# バックエンドの再起動
docker-compose restart backend

# バックエンドのログ確認
docker-compose logs backend

# データベースマイグレーション
docker exec bridge_line_backend alembic upgrade head

# 新しいマイグレーション作成
docker exec bridge_line_backend alembic revision --autogenerate -m "マイグレーション名"
```

#### フロントエンド開発
```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

### 4. アクセスURL
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **フロントエンド**: http://localhost:3000
- **データベース**: localhost:5432
- **Redis**: localhost:6379

## 開発環境

### Docker環境
- **PostgreSQL**: データベース（ポート5432）
- **Redis**: キャッシュ・セッション管理（ポート6379）
- **Backend**: FastAPIアプリケーション（ポート8000）

### 技術スタック
- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose

## プロジェクト構造
```
bridge-line/
├── backend/          # FastAPIバックエンド
├── frontend/         # Next.jsフロントエンド
├── scripts/          # データベース初期化スクリプト
├── docs/            # ドキュメント
├── docker-compose.yml # Docker環境設定
└── README.md        # このファイル
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. Docker Desktopが起動していない
```bash
# Docker Desktopを手動で起動してから
docker-compose up -d
```

#### 2. ポートが既に使用されている
```bash
# 既存のコンテナを停止
docker-compose down

# 再起動
docker-compose up -d
```

#### 3. データベース接続エラー
```bash
# データベースコンテナの状態確認
docker-compose ps postgres

# データベースのログ確認
docker-compose logs postgres
```

#### 4. バックエンドの再ビルドが必要
```bash
# バックエンドの再ビルド
docker-compose build backend

# 再起動
docker-compose up -d backend
```

## 本番環境デプロイ

### 環境変数の設定
本番環境では、以下の環境変数を適切に設定してください：

```bash
# データベース
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# セキュリティ
SECRET_KEY=your-secret-key-here

# 外部サービス
OPENAI_API_KEY=your-openai-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
STRIPE_SECRET_KEY=your-stripe-secret-key
```

## 開発ガイドライン

### コミットメッセージの規約
```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメントの更新
style: コードスタイルの修正
refactor: リファクタリング
test: テストの追加・修正
chore: その他の変更
```

### ブランチ戦略
- `main`: 本番環境用
- `develop`: 開発環境用
- `feature/*`: 機能開発用
- `hotfix/*`: 緊急修正用

## チーム開発のベストプラクティス

### 1. 環境の統一
- Docker Composeを使用して全員が同じ環境で開発
- 環境変数は`.env.example`を参考に設定
- OS別のセットアップスクリプトを用意：
  - **Mac**: `scripts/dev-setup-mac.sh` (Homebrew対応)
  - **Windows**: `scripts/dev-setup.ps1` (PowerShell対応)
  - **Linux**: `scripts/dev-setup.sh` (汎用)

### 2. コードレビュー
- プルリクエストを作成してコードレビューを実施
- 自動テストの追加を推奨

### 3. ドキュメント
- API仕様書の更新
- データベース設計書の管理
- セットアップ手順の文書化

## サポート

問題が発生した場合は、以下を確認してください：
1. Docker Desktopが起動しているか
2. ポートが競合していないか
3. 環境変数が正しく設定されているか

それでも解決しない場合は、チームリーダーに相談してください。

## 各OSでの使用方法

### **Windows**
```powershell
# PowerShellで実行
.\scripts\dev-setup.ps1

# または Makefile使用
make setup
```

### **Mac**
```bash
# Mac専用スクリプトで実行（推奨）
chmod +x scripts/dev-setup-mac.sh
./scripts/dev-setup-mac.sh

# または Makefile使用
make setup
```

### **Linux**
```bash
# Bashで実行
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh

# または Makefile使用
make setup
```

### **共通コマンド**
```bash
# 環境の起動
make start

# 環境の停止
make stop

# ログの確認
make logs

# ヘルスチェック
make health
```

## チームメンバー向けセットアップ手順

### 新規参加者の場合
1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd bridge-line
   ```

2. **環境構築**
   ```bash
   # 全OS共通（推奨）
   make setup
   
   # またはOS別
   # Windows: .\scripts\dev-setup.ps1
   # Mac: ./scripts/dev-setup-mac.sh
   # Linux: ./scripts/dev-setup.sh
   ```

3. **開発開始**
   ```bash
   # バックエンド開発
   make logs backend
   
   # フロントエンド開発
   cd frontend
   npm run dev
   ```

### 既存メンバーの場合
```bash
# 最新コードの取得
git pull origin main

# 環境の再起動
make restart

# マイグレーションの実行（必要に応じて）
make migrate
```

### トラブルシューティング
```bash
# 環境の完全リセット
make reset

# 依存関係の確認
make deps-check

# 環境変数の確認
make env-check
```
