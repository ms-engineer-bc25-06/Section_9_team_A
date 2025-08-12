#!/bin/bash

# Bridge Line テスト実行スクリプト
# 使用方法: ./scripts/run-tests.sh [backend|frontend|all]

set -e

# 色付きの出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ヘルプ表示
show_help() {
    echo "Bridge Line テスト実行スクリプト"
    echo ""
    echo "使用方法:"
    echo "  $0 [backend|frontend|all] [options]"
    echo ""
    echo "オプション:"
    echo "  backend    バックエンドのテストのみ実行"
    echo "  frontend   フロントエンドのテストのみ実行"
    echo "  all        全テストを実行（デフォルト）"
    echo "  --quick    クイックテスト（リンターとフォーマッターのみ）"
    echo "  --help     このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0                    # 全テスト実行"
    echo "  $0 backend           # バックエンドテストのみ"
    echo "  $0 frontend --quick  # フロントエンドのクイックチェック"
}

# バックエンドテスト実行
run_backend_tests() {
    log_info "バックエンドテストを実行中..."
    
    cd backend
    
    # 依存関係のインストール確認
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        log_warning "仮想環境が見つかりません。requirements-dev.txtをインストールします..."
        pip install -r requirements-dev.txt
    fi
    
    # リンター実行
    log_info "Flake8でコード品質チェック中..."
    if python -m flake8 app/ --max-line-length=88 --extend-ignore=E203,W503; then
        log_success "Flake8チェック完了"
    else
        log_error "Flake8チェックでエラーが発生しました"
        return 1
    fi
    
    # フォーマッター実行
    log_info "Blackでコードフォーマット中..."
    if python -m black app/ --line-length=88 --check; then
        log_success "Blackチェック完了"
    else
        log_warning "Blackフォーマットが必要です。実行しますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            python -m black app/ --line-length=88
            log_success "Blackフォーマット完了"
        fi
    fi
    
    # インポート整理
    log_info "isortでインポート整理中..."
    if python -m isort app/ --profile=black --check-only; then
        log_success "isortチェック完了"
    else
        log_warning "isort整理が必要です。実行しますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            python -m isort app/ --profile=black
            log_success "isort整理完了"
        fi
    fi
    
    # 型チェック
    log_info "mypyで型チェック中..."
    if python -m mypy app/ --ignore-missing-imports; then
        log_success "mypyチェック完了"
    else
        log_warning "mypyチェックで警告が発生しました"
    fi
    
    # テスト実行
    log_info "pytestでテスト実行中..."
    if python -m pytest tests/ -v --cov=app --cov-report=term-missing; then
        log_success "バックエンドテスト完了"
    else
        log_error "バックエンドテストでエラーが発生しました"
        return 1
    fi
    
    cd ..
}

# フロントエンドテスト実行
run_frontend_tests() {
    log_info "フロントエンドテストを実行中..."
    
    cd frontend
    
    # 依存関係のインストール確認
    if [ ! -d "node_modules" ]; then
        log_warning "node_modulesが見つかりません。npm installを実行します..."
        npm install
    fi
    
    # リンター実行
    log_info "ESLintでコード品質チェック中..."
    if npm run lint; then
        log_success "ESLintチェック完了"
    else
        log_error "ESLintチェックでエラーが発生しました"
        return 1
    fi
    
    # フォーマッター実行
    log_info "Prettierでコードフォーマット中..."
    if npm run format:check; then
        log_success "Prettierチェック完了"
    else
        log_warning "Prettierフォーマットが必要です。実行しますか？ (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            npm run format
            log_success "Prettierフォーマット完了"
        fi
    fi
    
    # 型チェック
    log_info "TypeScriptで型チェック中..."
    if npm run type-check; then
        log_success "TypeScriptチェック完了"
    else
        log_error "TypeScriptチェックでエラーが発生しました"
        return 1
    fi
    
    # テスト実行
    log_info "Jestでテスト実行中..."
    if npm run test:ci; then
        log_success "フロントエンドテスト完了"
    else
        log_error "フロントエンドテストでエラーが発生しました"
        return 1
    fi
    
    cd ..
}

# クイックチェック実行
run_quick_check() {
    log_info "クイックチェックを実行中..."
    
    # バックエンドのクイックチェック
    cd backend
    log_info "バックエンドのクイックチェック中..."
    python -m flake8 app/ --max-line-length=88 --extend-ignore=E203,W503 --count --statistics
    cd ..
    
    # フロントエンドのクイックチェック
    cd frontend
    log_info "フロントエンドのクイックチェック中..."
    npm run quality:quick
    cd ..
    
    log_success "クイックチェック完了"
}

# メイン処理
main() {
    local target="all"
    local quick_mode=false
    
    # 引数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            backend|frontend|all)
                target="$1"
                shift
                ;;
            --quick)
                quick_mode=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "不明なオプション: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "Bridge Line テスト実行開始"
    log_info "対象: $target"
    
    if [ "$quick_mode" = true ]; then
        run_quick_check
        exit 0
    fi
    
    case $target in
        backend)
            run_backend_tests
            ;;
        frontend)
            run_frontend_tests
            ;;
        all)
            run_backend_tests
            run_frontend_tests
            ;;
    esac
    
    log_success "全テスト完了！🎉"
}

# スクリプト実行
main "$@"
