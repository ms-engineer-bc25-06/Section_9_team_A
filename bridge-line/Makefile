# Bridge Line 開発用 Makefile
# Windows/Mac/Linux 共通で使用可能

.PHONY: help setup start stop restart logs clean build test migrate frontend backend

# デフォルトターゲット
help:
	@echo "Bridge Line 開発用コマンド"
	@echo ""
	@echo "環境構築:"
	@echo "  make setup     - 開発環境の初期セットアップ"
	@echo "  make start     - Docker環境の起動"
	@echo "  make stop      - Docker環境の停止"
	@echo "  make restart   - Docker環境の再起動"
	@echo ""
	@echo "開発用:"
	@echo "  make logs      - ログの表示"
	@echo "  make build     - コンテナの再ビルド"
	@echo "  make test      - テストの実行"
	@echo "  make migrate   - データベースマイグレーション"
	@echo ""
	@echo "フロントエンド:"
	@echo "  make frontend  - フロントエンド開発サーバー起動"
	@echo ""
	@echo "バックエンド:"
	@echo "  make backend   - バックエンドのログ表示"
	@echo ""
	@echo "クリーンアップ:"
	@echo "  make clean     - コンテナとボリュームの削除"

# 開発環境の初期セットアップ
setup:
	@echo "🚀 Bridge Line 開発環境セットアップを開始します..."
	@if [ -f "scripts/dev-setup-mac.sh" ]; then \
		chmod +x scripts/dev-setup-mac.sh && ./scripts/dev-setup-mac.sh; \
	elif [ -f "scripts/dev-setup.sh" ]; then \
		chmod +x scripts/dev-setup.sh && ./scripts/dev-setup.sh; \
	elif [ -f "scripts/dev-setup.ps1" ]; then \
		powershell -ExecutionPolicy Bypass -File scripts/dev-setup.ps1; \
	else \
		echo "セットアップスクリプトが見つかりません。"; \
		echo "手動で以下のコマンドを実行してください:"; \
		echo "  docker-compose up --build -d"; \
		echo "  docker exec bridge_line_backend alembic upgrade head"; \
	fi

# Docker環境の起動
start:
	@echo "🐳 Docker環境を起動中..."
	docker-compose up -d
	@echo "✅ 環境が起動しました。"
	@echo "アクセスURL:"
	@echo "  📊 バックエンドAPI: http://localhost:8000"
	@echo "  📚 APIドキュメント: http://localhost:8000/docs"
	@echo "  🎨 フロントエンド: http://localhost:3000"

# Docker環境の停止
stop:
	@echo "🛑 Docker環境を停止中..."
	docker-compose down
	@echo "✅ 環境が停止しました。"

# Docker環境の再起動
restart:
	@echo "🔄 Docker環境を再起動中..."
	docker-compose restart
	@echo "✅ 環境が再起動しました。"

# ログの表示
logs:
	@echo "📝 ログを表示中..."
	docker-compose logs -f

# バックエンドのログ表示
backend:
	@echo "📝 バックエンドのログを表示中..."
	docker-compose logs -f backend

# コンテナの再ビルド
build:
	@echo "🔨 コンテナを再ビルド中..."
	docker-compose build
	@echo "✅ ビルドが完了しました。"

# テストの実行
test:
	@echo "🧪 テストを実行中..."
	docker exec bridge_line_backend pytest
	@echo "✅ テストが完了しました。"

# データベースマイグレーション
migrate:
	@echo "🗄️ データベースマイグレーションを実行中..."
	docker exec bridge_line_backend alembic upgrade head
	@echo "✅ マイグレーションが完了しました。"

# 新しいマイグレーション作成
migrate-create:
	@echo "📝 新しいマイグレーションを作成中..."
	@read -p "マイグレーション名を入力してください: " name; \
	docker exec bridge_line_backend alembic revision --autogenerate -m "$$name"

# フロントエンド開発サーバー起動
frontend:
	@echo "🎨 フロントエンド開発サーバーを起動中..."
	@if [ -d "frontend" ]; then \
		cd frontend && npm run dev; \
	else \
		echo "❌ frontend ディレクトリが見つかりません。"; \
	fi

# フロントエンドの依存関係インストール
frontend-install:
	@echo "📦 フロントエンドの依存関係をインストール中..."
	@if [ -d "frontend" ]; then \
		cd frontend && npm install; \
	else \
		echo "❌ frontend ディレクトリが見つかりません。"; \
	fi

# データベースの状態確認
db-status:
	@echo "🗄️ データベースの状態を確認中..."
	docker-compose ps postgres
	docker-compose logs --tail=10 postgres

# バックエンドの状態確認
backend-status:
	@echo "🔧 バックエンドの状態を確認中..."
	docker-compose ps backend
	docker-compose logs --tail=10 backend

# ヘルスチェック
health:
	@echo "🏥 ヘルスチェックを実行中..."
	@if command -v curl >/dev/null 2>&1; then \
		if curl -f http://localhost:8000/health >/dev/null 2>&1; then \
			echo "✅ バックエンドAPI が正常に動作しています。"; \
		else \
			echo "❌ バックエンドAPI にアクセスできません。"; \
		fi; \
	else \
		echo "⚠️  curl がインストールされていません。"; \
	fi

# クリーンアップ（コンテナとボリュームの削除）
clean:
	@echo "🧹 クリーンアップを実行中..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ クリーンアップが完了しました。"

# 開発環境の完全リセット
reset: clean setup

# データベースのリセット
db-reset:
	@echo "🗄️ データベースをリセット中..."
	docker-compose down -v
	docker-compose up -d postgres
	@echo "データベースが再起動しました。"
	@echo "マイグレーションを実行してください: make migrate"

# バックエンドのシェルアクセス
backend-shell:
	@echo "🐚 バックエンドコンテナにシェルアクセス中..."
	docker exec -it bridge_line_backend /bin/bash

# データベースのシェルアクセス
db-shell:
	@echo "🐚 データベースコンテナにシェルアクセス中..."
	docker exec -it bridge_line_postgres psql -U bridge_user -d bridge_line_db

# 環境変数の確認
env-check:
	@echo "🔍 環境変数を確認中..."
	@if [ -f "backend/.env" ]; then \
		echo "✅ backend/.env が存在します。"; \
	else \
		echo "❌ backend/.env が見つかりません。"; \
		if [ -f "backend/.env.example" ]; then \
			echo "📝 backend/.env.example から .env を作成してください。"; \
		fi; \
	fi

# 依存関係の確認
deps-check:
	@echo "🔍 依存関係を確認中..."
	@echo "Docker: $$(docker --version 2>/dev/null || echo '未インストール')"
	@echo "Docker Compose: $$(docker-compose --version 2>/dev/null || echo '未インストール')"
	@if [ -d "frontend" ]; then \
		echo "Node.js: $$(node --version 2>/dev/null || echo '未インストール')"; \
		echo "npm: $$(npm --version 2>/dev/null || echo '未インストール')"; \
	fi 