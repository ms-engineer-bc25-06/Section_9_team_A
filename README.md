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

### 3. 開発方法の選択

#### **方法A: Docker環境での開発（推奨）**
```bash
# Docker環境でバックエンドを起動
docker-compose up backend

# 別ターミナルでフロントエンド開発
cd frontend
npm run dev
```

#### **方法B: ローカル環境での開発（オプション）**
```bash
# Python 3.11以上がインストールされていることを確認
python --version

# 仮想環境の作成（ローカル開発のみ）
python -m venv .venv311

# 仮想環境の有効化
# Windows
.venv311\Scripts\activate

# macOS/Linux
source .venv311/bin/activate

# 依存関係のインストール
pip install -r backend/requirements.txt

# バックエンドのローカル実行
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 環境変数の設定

#### **Docker環境の場合**
```bash
# 環境変数はdocker-compose.ymlで管理
# 必要に応じて.envファイルを作成
cp backend/env.example backend/.env
# backend/.envファイルを編集
```

#### **ローカル環境の場合**
```bash
# バックエンド環境変数の設定
cp backend/env.example backend/.env
# backend/.envファイルを編集してFirebase設定などを追加

# フロントエンド環境変数の設定
cp frontend/env.example frontend/.env.local
# frontend/.env.localファイルを編集してFirebase設定などを追加
```

### 5. 開発用コマンド

#### **Docker環境での開発**
```bash
# バックエンドの再起動
docker-compose restart backend

# バックエンドのログ確認
docker-compose logs backend

# データベースマイグレーション
docker exec bridge_line_backend alembic upgrade head

# 新しいマイグレーション作成
docker exec bridge_line_backend alembic revision --autogenerate -m "マイグレーション名"

# テストの実行
docker exec bridge_line_backend pytest
```

#### **ローカル環境での開発**
```bash
# 仮想環境の有効化（毎回必要）
# Windows
.venv311\Scripts\activate

# macOS/Linux
source .venv311/bin/activate

# バックエンドのローカル実行
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# データベースマイグレーション
alembic upgrade head

# 新しいマイグレーション作成
alembic revision --autogenerate -m "マイグレーション名"

# テストの実行
pytest
```

#### **フロントエンド開発**
```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

### 6. アクセスURL
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **フロントエンド**: http://localhost:3000
- **データベース**: localhost:5432
- **Redis**: localhost:6379

## 開発環境

### Docker環境（推奨）
- **PostgreSQL**: データベース（ポート5432）
- **Redis**: キャッシュ・セッション管理（ポート6379）
- **Backend**: FastAPIアプリケーション（ポート8000）
- **Python環境**: Dockerコンテナ内で管理

### ローカル開発環境（オプション）
- **Python**: 3.11以上
- **仮想環境**: `.venv311/`（ローカル開発のみ）
- **Node.js**: 18以上（フロントエンド用）

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
├── .venv311/        # Python仮想環境（ローカル開発のみ、.gitignoreに含まれる）
└── README.md        # このファイル
```

## チーム開発のベストプラクティス

### 開発方法の選択

#### **Docker環境での開発（推奨）**
- **メリット**: 環境の統一、依存関係の管理が簡単
- **デメリット**: 初回のビルド時間が長い
- **対象**: チーム全体で推奨

#### **ローカル環境での開発（オプション）**
- **メリット**: 高速な開発、IDEとの連携が良い
- **デメリット**: 環境構築が複雑、依存関係の管理が必要
- **対象**: 上級者、IDEでのデバッグが必要な場合

### 仮想環境の管理（ローカル開発のみ）

#### **Docker環境では不要**
- Dockerコンテナ内でPython環境が完結
- ホストのPython環境に依存しない
- `.venv`はローカル開発のみで使用

#### **ローカル開発の場合**
- **共有しない**: `.venv311/`ディレクトリは`.gitignore`に含まれており、リポジトリにコミットされません
- **各自で作成**: 各チームメンバーが自分の環境で仮想環境を作成してください
- **バージョン統一**: Python 3.11以上を使用してください

### 仮想環境の使用タイミング（ローカル開発のみ）

#### **開発時（推奨）**
```bash
# 毎回の開発開始時に仮想環境を有効化
# Windows
.venv311\Scripts\activate

# macOS/Linux
source .venv311/bin/activate

# その後、開発を開始
cd backend
uvicorn app.main:app --reload
```

#### **テスト実行時のみ（最小限）**
```bash
# テスト実行時のみ仮想環境を使用する場合
# Windows
.venv311\Scripts\activate && pytest

# macOS/Linux
source .venv311/bin/activate && pytest
```

#### **なぜ開発時も.venvが必要か？（ローカル開発のみ）**
1. **依存関係の競合防止**: システムのPythonパッケージと競合を避ける
2. **バージョン統一**: チーム全体で同じバージョンを使用
3. **環境の再現性**: 本番環境と同じ条件で開発
4. **デバッグの精度**: 正確な環境でデバッグが可能

### Mac OSでのPython環境管理（ローカル開発のみ）

#### **Mac OSでのpipについて**
```bash
# Mac OSでもpipは使用可能です
# ただし、システムPythonを使用する場合は注意が必要

# 推奨: HomebrewでPythonをインストール
brew install python@3.11

# または: pyenvを使用
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### **Mac OSでのセットアップ手順（ローカル開発のみ）**
```bash
# 1. HomebrewでPython 3.11をインストール
brew install python@3.11

# 2. Python 3.11のパスを確認
which python3.11

# 3. 仮想環境の作成
python3.11 -m venv .venv311

# 4. 仮想環境の有効化
source .venv311/bin/activate

# 5. 依存関係のインストール
pip install -r backend/requirements.txt
```

#### **Mac OSでのトラブルシューティング（ローカル開発のみ）**
```bash
# pipが見つからない場合
# 1. HomebrewでPythonを再インストール
brew uninstall python
brew install python@3.11

# 2. パスを確認
echo $PATH
which python3.11

# 3. pipの確認
python3.11 -m pip --version

# 4. 仮想環境内でpipを使用
source .venv311/bin/activate
pip --version
```

### 環境変数の管理
- **テンプレート使用**: `backend/env.example`と`frontend/env.example`をコピーして使用
- **機密情報**: APIキーなどの機密情報は`.env`ファイルに保存し、コミットしない
- **チーム共有**: 非機密の設定値はチーム内で共有

### 開発ワークフロー
1. **環境構築**: Docker環境の起動またはローカル環境のセットアップ
2. **環境変数設定**: Firebase設定などの必要な環境変数を設定
3. **開発開始**: Docker環境またはローカル環境で開発を開始
4. **テスト実行**: 変更前にテストを実行して品質を確保

## トラブルシューティング

### よくある問題と解決方法

#### 1. 仮想環境の問題
```bash
# 仮想環境が有効になっていない場合
# Windows
.venv311\Scripts\activate

# macOS/Linux
source .venv311/bin/activate

# 仮想環境を再作成する場合
rm -rf .venv311
python -m venv .venv311
# 上記の有効化コマンドを実行後
pip install -r backend/requirements.txt
```

#### 2. 依存関係の問題
```bash
# 依存関係を更新
pip install --upgrade -r backend/requirements.txt

# キャッシュをクリア
pip cache purge
```

#### 3. 環境変数の問題
```bash
# 環境変数ファイルが存在することを確認
ls -la backend/.env
ls -la frontend/.env.local

# テンプレートから再作成
cp backend/env.example backend/.env
cp frontend/env.example frontend/.env.local
```

#### 4. Docker Desktopが起動していない
```bash
# Docker Desktopを手動で起動してから
docker-compose up -d
```

#### 5. ポートが既に使用されている
```bash
# 既存のコンテナを停止
docker-compose down

# 再起動
docker-compose up -d
```

#### 6. データベース接続エラー
```bash
# データベースコンテナの状態確認
docker-compose ps postgres

# データベースのログ確認
docker-compose logs postgres
```

#### 7. バックエンドの再ビルドが必要
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
4. 仮想環境が有効になっているか

それでも解決しない場合は、チームリーダーに相談してください。

## 各OSでの使用方法

### **Windows**
```powershell
# PowerShellで実行
.\scripts\dev-setup.ps1

# 仮想環境の有効化
.venv311\Scripts\activate

# または Makefile使用
make setup
```

### **Mac**
```bash
# Mac専用スクリプトで実行（推奨）
chmod +x scripts/dev-setup-mac.sh
./scripts/dev-setup-mac.sh

# 仮想環境の有効化
source .venv311/bin/activate

# または Makefile使用
make setup
```

### **Linux**
```bash
# Bashで実行
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh

# 仮想環境の有効化
source .venv311/bin/activate

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

3. **仮想環境の設定**
   ```bash
   # Python仮想環境の作成
   python -m venv .venv311
   
   # 仮想環境の有効化
   # Windows: .venv311\Scripts\activate
   # macOS/Linux: source .venv311/bin/activate
   
   # 依存関係のインストール
   pip install -r backend/requirements.txt
   ```

4. **環境変数の設定**
   ```bash
   # バックエンド環境変数
   cp backend/env.example backend/.env
   # backend/.envを編集してFirebase設定などを追加
   
   # フロントエンド環境変数
   cp frontend/env.example frontend/.env.local
   # frontend/.env.localを編集してFirebase設定などを追加
   ```

5. **開発開始**
   ```bash
   # 仮想環境を有効化してから
   # バックエンド開発
   cd backend
   uvicorn app.main:app --reload
   
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

# 仮想環境の有効化（毎回必要）
# Windows: .venv311\Scripts\activate
# macOS/Linux: source .venv311/bin/activate
```

### トラブルシューティング
```bash
# 環境の完全リセット
make reset

# 依存関係の確認
make deps-check

# 環境変数の確認
make env-check

# 仮想環境の再作成
rm -rf .venv311
python -m venv .venv311
# 有効化後
pip install -r backend/requirements.txt
```
