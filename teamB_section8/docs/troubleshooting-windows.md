# Windowsトラブルシューティング

## 1. Docker Desktopが起動しない
- 対策: Docker Desktopを手動で起動し、再度 `setup.ps1` を実行

## 2. WSL2が有効でない
- 対策: Docker Desktopの設定でWSL2バックエンドを有効化

## 3. PowerShell実行ポリシーエラー
- 対策: 管理者権限でPowerShellを開き `Set-ExecutionPolicy RemoteSigned` を実行

## 4. ポート8000が使えない
- 対策: 他のアプリを停止、または `compose.yml` のポート番号を変更

## 5. .envファイルが見つからない
- 対策: `.env.example` をコピーして `.env` を作成

## 6. 権限エラー
- 対策: PowerShellを「管理者として実行」 