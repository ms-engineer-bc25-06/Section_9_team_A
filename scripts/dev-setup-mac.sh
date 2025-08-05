#!/bin/bash

# Bridge Line 開発環境セットアップスクリプト (Mac専用版)
# macOS 用

set -e

echo "🍎 Bridge Line 開発環境セットアップ (Mac版) を開始します..."

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

log_success() {
    echo -e "\033[36m[SUCCESS]\033[0m $1"
}

# Homebrew の確認とインストール
check_homebrew() {
    log_info "Homebrew の確認中..."
    if ! command -v brew &> /dev/null; then
        log_warn "Homebrew がインストールされていません。"
        echo "Homebrew をインストールしますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            log_info "Homebrew をインストール中..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            log_success "Homebrew のインストールが完了しました。"
        else
            log_error "Homebrew が必要です。手動でインストールしてください。"
            log_info "https://brew.sh/ からインストールできます。"
            exit 1
        fi
    else
        log_success "✅ Homebrew が利用可能です。"
    fi
}

# Docker の確認とインストール
check_docker() {
    log_info "Docker の確認中..."
    if ! command -v docker &> /dev/null; then
        log_warn "Docker がインストールされていません。"
        echo "Docker Desktop をインストールしますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            log_info "Docker Desktop をインストール中..."
            brew install --cask docker
            log_success "Docker Desktop のインストールが完了しました。"
            log_info "Docker Desktop を起動してください。"
            open -a Docker
            echo "Docker Desktop が起動したら、Enter キーを押してください..."
            read -r
        else
            log_error "Docker が必要です。手動でインストールしてください。"
            log_info "https://docs.docker.com/desktop/install/mac/ からインストールできます。"
            exit 1
        fi
    fi

    # Docker の起動確認
    if ! docker info &> /dev/null; then
        log_error "Docker が起動していません。"
        log_info "Docker Desktop を起動してください。"
        open -a Docker
        echo "Docker Desktop が起動したら、Enter キーを押してください..."
        read -r
    fi

    log_success "✅ Docker が正常に動作しています。"
}

# Docker Compose の確認
check_docker_compose() {
    log_info "Docker Compose の確認中..."
    if ! command -v docker-compose &> /dev/null; then
        log_warn "Docker Compose がインストールされていません。"
        log_info "Docker Compose をインストール中..."
        brew install docker-compose
        log_success "✅ Docker Compose のインストールが完了しました。"
    else
        log_success "✅ Docker Compose が利用可能です。"
    fi
}

# Node.js の確認とインストール
check_nodejs() {
    log_info "Node.js の確認中..."
    if ! command -v node &> /dev/null; then
        log_warn "Node.js がインストールされていません。"
        echo "Node.js をインストールしますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            log_info "Node.js をインストール中..."
            brew install node
            log_success "✅ Node.js のインストールが完了しました。"
        else
            log_warn "Node.js がインストールされていません。フロントエンド開発に影響する可能性があります。"
        fi
    else
        log_success "✅ Node.js が利用可能です: $(node --version)"
    fi
}

# Git の確認
check_git() {
    log_info "Git の確認中..."
    if ! command -v git &> /dev/null; then
        log_warn "Git がインストールされていません。"
        log_info "Git をインストール中..."
        brew install git
        log_success "✅ Git のインストールが完了しました。"
    else
        log_success "✅ Git が利用可能です: $(git --version)"
    fi
}

# 環境変数ファイルの確認
check_env_files() {
    log_info "環境変数ファイルの確認中..."
    
    if [ ! -f "backend/.env" ]; then
        log_warn "backend/.env ファイルが見つかりません。"
        if [ -f "backend/.env.example" ]; then
            log_info "backend/.env.example から .env を作成します..."
            cp backend/.env.example backend/.env
            log_success "✅ backend/.env を作成しました。"
        else
            log_warn "backend/.env.example も見つかりません。"
        fi
    else
        log_success "✅ backend/.env が存在します。"
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
    
    log_success "✅ Docker 環境の起動が完了しました。"
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
    
    log_success "✅ マイグレーションが完了しました。"
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
            log_success "✅ フロントエンドの依存関係をインストールしました。"
        else
            log_success "✅ node_modules が存在します。"
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
        log_success "✅ バックエンドAPI が正常に動作しています。"
    else
        log_warn "⚠️  バックエンドAPI にアクセスできません。"
    fi
}

# 開発用ツールのインストール
install_dev_tools() {
    log_info "開発用ツールの確認中..."
    
    # curl の確認
    if ! command -v curl &> /dev/null; then
        log_info "curl をインストール中..."
        brew install curl
    fi
    
    # jq の確認（JSON処理用）
    if ! command -v jq &> /dev/null; then
        log_info "jq をインストール中..."
        brew install jq
    fi
    
    log_success "✅ 開発用ツールが利用可能です。"
}

# メイン処理
main() {
    echo "=========================================="
    echo "🍎 Bridge Line 開発環境セットアップ (Mac版)"
    echo "=========================================="
    
    check_homebrew
    check_docker
    check_docker_compose
    check_nodejs
    check_git
    install_dev_tools
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
    echo "  🔄 環境の再起動: make restart"
    echo "  📝 ログの確認: make logs"
    echo "  🗄️  マイグレーション: make migrate"
    echo ""
    echo "フロントエンド開発:"
    echo "  make frontend"
    echo ""
    echo "便利なコマンド:"
    echo "  make help      - 利用可能なコマンド一覧"
    echo "  make health    - ヘルスチェック"
    echo "  make clean     - 環境のクリーンアップ"
    echo ""
}

# スクリプトの実行
main "$@" 