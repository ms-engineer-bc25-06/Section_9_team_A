# =============================
# Windows用セットアップスクリプト（PowerShell専用）
# =============================
# 実行方法: PowerShellで ./setup.ps1

Write-Host "[1/5] Docker Desktopの起動確認..."
$dockerInfo = docker info 2>$null
if (-not $dockerInfo) {
  Write-Host "Docker Desktopが起動していません。起動してから再実行してください。" -ForegroundColor Red
  exit 1
}

Write-Host "[2/5] WSL2バックエンド有効化確認..."
$wslCheck = wsl -l -v 2>$null
if ($wslCheck -notmatch "Running") {
  Write-Host "WSL2が有効化されていません。Docker Desktopの設定を確認してください。" -ForegroundColor Red
  exit 1
}

Write-Host "[3/5] PowerShell実行ポリシー確認..."
$policy = Get-ExecutionPolicy
if ($policy -eq "Restricted") {
  Write-Host "実行ポリシーがRestrictedです。管理者権限で 'Set-ExecutionPolicy RemoteSigned' を実行してください。" -ForegroundColor Yellow
  exit 1
}

Write-Host "[4/5] .envファイル存在確認..."
if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host ".envファイルを .env.example から自動生成しました。"
}

Write-Host "[5/5] Docker Compose起動テスト..."
docker compose up --build 