# Windows用セットアップガイド

## 必須要件
- Windows 10/11
- Docker Desktop for Windows（WSL2バックエンド有効化）
- PowerShell（管理者権限推奨）
- Git

## セットアップ手順
1. リポジトリをクローン
2. `.env.example` をコピーして `.env` を作成
3. PowerShellで `./setup.ps1` を実行
4. ブラウザで http://localhost:8000/health を確認

## 重要ポイント
- **必ずPowerShell構文で操作（`&&`やbash構文禁止）**
- `.env`ファイルはGit管理しない
- Docker DesktopはWSL2バックエンド推奨
- 権限エラー時は「管理者として実行」

## よくあるトラブル
- Docker Desktopが起動していない → 起動してから再実行
- WSL2が有効でない → Docker Desktop設定でWSL2を有効化
- PowerShell実行ポリシーがRestricted → 管理者で `Set-ExecutionPolicy RemoteSigned` 実行
- ポート8000が使えない → 他のアプリを停止

## 詳細は [docs/troubleshooting-windows.md](troubleshooting-windows.md) 参照 