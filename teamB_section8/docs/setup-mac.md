# Mac用セットアップガイド

## 必須要件
- macOS（Intel/M1/M2対応）
- Docker Desktop for Mac
- ターミナル
- Git

## セットアップ手順
1. リポジトリをクローン
2. `.env.example` をコピーして `.env` を作成
3. ターミナルで `chmod +x setup.sh && ./setup.sh` を実行
4. ブラウザで http://localhost:8000/health を確認

## 重要ポイント
- `.env`ファイルはGit管理しない
- Docker Desktopは最新推奨
- M1/M2チップはRosettaやarm64イメージ推奨
- 権限エラー時は `chmod +x setup.sh` で実行権限付与

## よくあるトラブル
- Docker Desktopが起動していない → 起動してから再実行
- 権限エラー → `chmod +x setup.sh` 実行
- ポート8000が使えない → 他のアプリを停止

## 詳細は [docs/troubleshooting-mac.md](troubleshooting-mac.md) 参照 