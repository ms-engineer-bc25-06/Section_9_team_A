# Bridge Line 開発環境セットアップスクリプト (PowerShell版)
# Windows 用

param(
    [switch]$SkipFrontend
)

# エラー時に停止
$ErrorActionPreference = "Stop"

# 色付きのログ関数
function Write-InfoLog {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-WarnLog {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorLog {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Docker の確認
function Test-Docker {
    Write-InfoLog "Docker の確認中..."
    
    try {
        $dockerVersion = docker --version
        Write-InfoLog "✅ Docker がインストールされています: $dockerVersion"
    }
    catch {
        Write-ErrorLog "Docker がインストールされていません。"
        Write-InfoLog "https://docs.docker.com/get-docker/ からインストールしてください。"
        exit 1
    }
    
    try {
        docker info | Out-Null
        Write-InfoLog "✅ Docker が正常に動作しています。"
    }
    catch {
        Write-ErrorLog "Docker が起動していません。"
        Write-InfoLog "Docker Desktop を起動してください。"
        exit 1
    }
}

# Docker Compose の確認
function Test-DockerCompose {
    Write-InfoLog "Docker Compose の確認中..."
    
    try {
        $composeVersion = docker-compose --version
        Write-InfoLog "✅ Docker Compose が利用可能です: $composeVersion"
    }
    catch {
        Write-ErrorLog "Docker Compose がインストールされていません。"
        exit 1
    }
}

# 環境変数ファイルの確認
function Test-EnvFiles {
    Write-InfoLog "環境変数ファイルの確認中..."
    
    if (-not (Test-Path "backend\.env")) {
        Write-WarnLog "backend\.env ファイルが見つかりません。"
        if (Test-Path "backend\.env.example") {
            Write-InfoLog "backend\.env.example から .env を作成します..."
            Copy-Item "backend\.env.example" "backend\.env"
            Write-InfoLog "✅ backend\.env を作成しました。"
        }
        else {
            Write-WarnLog "backend\.env.example も見つかりません。"
        }
    }
    else {
        Write-InfoLog "✅ backend\.env が存在します。"
    }
}

# Docker 環境の起動
function Start-DockerEnvironment {
    Write-InfoLog "Docker 環境を起動中..."
    
    # 既存のコンテナを停止
    Write-InfoLog "既存のコンテナを停止中..."
    try {
        docker-compose down | Out-Null
    }
    catch {
        # エラーは無視（コンテナが存在しない場合）
    }
    
    # 環境をビルドして起動
    Write-InfoLog "コンテナをビルドして起動中..."
    docker-compose up --build -d
    
    Write-InfoLog "✅ Docker 環境の起動が完了しました。"
}

# サービスの状態確認
function Test-Services {
    Write-InfoLog "サービスの状態を確認中..."
    
    # 少し待ってから状態確認
    Start-Sleep -Seconds 10
    
    docker-compose ps
    
    Write-InfoLog "各サービスのログを確認中..."
    Write-Host "=== Backend Logs ===" -ForegroundColor Cyan
    docker-compose logs --tail=10 backend
    Write-Host ""
    Write-Host "=== PostgreSQL Logs ===" -ForegroundColor Cyan
    docker-compose logs --tail=5 postgres
    Write-Host ""
    Write-Host "=== Redis Logs ===" -ForegroundColor Cyan
    docker-compose logs --tail=5 redis
}

# データベースマイグレーション
function Invoke-Migrations {
    Write-InfoLog "データベースマイグレーションを実行中..."
    
    # マイグレーションの実行
    docker exec bridge_line_backend alembic upgrade head
    
    Write-InfoLog "✅ マイグレーションが完了しました。"
}

# フロントエンドのセットアップ
function Setup-Frontend {
    if ($SkipFrontend) {
        Write-InfoLog "フロントエンドのセットアップをスキップします。"
        return
    }
    
    Write-InfoLog "フロントエンドのセットアップ中..."
    
    if (Test-Path "frontend") {
        Push-Location "frontend"
        
        # node_modules の確認
        if (-not (Test-Path "node_modules")) {
            Write-InfoLog "npm install を実行中..."
            npm install
        }
        else {
            Write-InfoLog "✅ node_modules が存在します。"
        }
        
        Pop-Location
    }
    else {
        Write-WarnLog "frontend ディレクトリが見つかりません。"
    }
}

# ヘルスチェック
function Test-HealthCheck {
    Write-InfoLog "アプリケーションのヘルスチェック中..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-InfoLog "✅ バックエンドAPI が正常に動作しています。"
        }
        else {
            Write-WarnLog "⚠️  バックエンドAPI の応答が異常です。"
        }
    }
    catch {
        Write-WarnLog "⚠️  バックエンドAPI にアクセスできません。"
    }
}

# メイン処理
function Main {
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host "Bridge Line 開発環境セットアップ" -ForegroundColor Magenta
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host ""
    
    Test-Docker
    Test-DockerCompose
    Test-EnvFiles
    Start-DockerEnvironment
    Test-Services
    Invoke-Migrations
    Setup-Frontend
    Test-HealthCheck
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host "🎉 セットアップが完了しました！" -ForegroundColor Magenta
    Write-Host "==========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "アクセスURL:" -ForegroundColor White
    Write-Host "  📊 バックエンドAPI: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  📚 APIドキュメント: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  🎨 フロントエンド: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "開発用コマンド:" -ForegroundColor White
    Write-Host "  🔄 環境の再起動: docker-compose restart" -ForegroundColor Yellow
    Write-Host "  📝 ログの確認: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "  🗄️  マイグレーション: docker exec bridge_line_backend alembic upgrade head" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "フロントエンド開発:" -ForegroundColor White
    Write-Host "  cd frontend && npm run dev" -ForegroundColor Yellow
    Write-Host ""
}

# スクリプトの実行
Main 