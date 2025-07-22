# Macトラブルシューティング

## 1. Docker Desktopが起動しない
- 対策: Docker Desktopを手動で起動し、再度 `setup.sh` を実行

## 2. 権限エラー
- 対策: `chmod +x setup.sh` で実行権限を付与

## 3. ポート8000が使えない
- 対策: 他のアプリを停止、または `compose.yml` のポート番号を変更

## 4. .envファイルが見つからない
- 対策: `.env.example` をコピーして `.env` を作成 