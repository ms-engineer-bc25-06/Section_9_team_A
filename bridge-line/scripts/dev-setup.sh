#!/bin/bash

# Bridge Line 開発環境セットアップスクリプト
# Windows/Mac/Linux 共通で使用可能

set -e

echo "🚀 Bridge Line 開発環境セットアップを開始します..."

# 色付きのログ関数
log_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# Docker の確認
check_docker() {
    log_info "Docker の確認中..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker がインストールされていません。"
        log_info "https://docs.docker.com/get-docker/ からインストールしてください。"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker が起動していません。"
        log_info "Docker Desktop を起動してください。"
        exit 1
    fi

    log_info "✅ Docker が正常に動作しています。"
}

# Docker Compose の確認
check_docker_compose() {
    log_info "Docker Compose の確認中..."
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose がインストールされていません。"
        exit 1
    fi
    log_info "✅ Docker Compose が利用可能です。"
}

# 環境変数ファイルの確認
check_env_files() {
    log_info "環境変数ファイルの確認中..."
    
    if [ ! -f "backend/.env" ]; then
        log_warn "backend/.env ファイルが見つかりません。"
        if [ -f "backend/.env.example" ]; then
            log_info "backend/.env.example から .env を作成します..."
            cp backend/.env.example backend/.env
            log_info "✅ backend/.env を作成しました。"
        else
            log_warn "backend/.env.example も見つかりません。"
        fi
    else
        log_info "✅ backend/.env が存在します。"
    fi
}

# Docker 環境の起動
start_docker_environment() {
    log_info "Docker 環境を起動中..."
    
    # 既存のコンテナを停止
    log_info "既存のコンテナを停止中..."
    docker-compose down 2>/dev/null || true
    
    # 環境をビルドして起動
    log_info "コンテナをビルドして起動中..."
    docker-compose up --build -d
    
    log_info "✅ Docker 環境の起動が完了しました。"
}

# サービスの状態確認
check_services() {
    log_info "サービスの状態を確認中..."
    
    # 少し待ってから状態確認
    sleep 10
    
    docker-compose ps
    
    log_info "各サービスのログを確認中..."
    echo "=== Backend Logs ==="
    docker-compose logs --tail=10 backend
    echo ""
    echo "=== PostgreSQL Logs ==="
    docker-compose logs --tail=5 postgres
    echo ""
    echo "=== Redis Logs ==="
    docker-compose logs --tail=5 redis
}

# データベースマイグレーション
run_migrations() {
    log_info "データベースマイグレーションを実行中..."
    
    # マイグレーションの実行
    docker exec bridge_line_backend alembic upgrade head
    
    log_info "✅ マイグレーションが完了しました。"
}

# フロントエンドのセットアップ
setup_frontend() {
    log_info "フロントエンドのセットアップ中..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # node_modules の確認
        if [ ! -d "node_modules" ]; then
            log_info "npm install を実行中..."
            npm install
        else
            log_info "✅ node_modules が存在します。"
        fi
        
        cd ..
    else
        log_warn "frontend ディレクトリが見つかりません。"
    fi
}

# ヘルスチェック
health_check() {
    log_info "アプリケーションのヘルスチェック中..."
    
    # バックエンドのヘルスチェック
    if curl -f http://localhost:8000/health &>/dev/null; then
        log_info "✅ バックエンドAPI が正常に動作しています。"
    else
        log_warn "⚠️  バックエンドAPI にアクセスできません。"
    fi
}

# メイン処理
main() {
    echo "=========================================="
    echo "Bridge Line 開発環境セットアップ"
    echo "=========================================="
    
    check_docker
    check_docker_compose
    check_env_files
    start_docker_environment
    check_services
    run_migrations
    setup_frontend
    health_check
    
    echo ""
    echo "=========================================="
    echo "🎉 セットアップが完了しました！"
    echo "=========================================="
    echo ""
    echo "アクセスURL:"
    echo "  📊 バックエンドAPI: http://localhost:8000"
    echo "  📚 APIドキュメント: http://localhost:8000/docs"
    echo "  🎨 フロントエンド: http://localhost:3000"
    echo ""
    echo "開発用コマンド:"
    echo "  🔄 環境の再起動: docker-compose restart"
    echo "  📝 ログの確認: docker-compose logs -f"
    echo "  🗄️  マイグレーション: docker exec bridge_line_backend alembic upgrade head"
    echo ""
    echo "フロントエンド開発:"
    echo "  cd frontend && npm run dev"
    echo ""
}

# スクリプトの実行
main "$@" 