# ngrokセットアップガイド

## ngrokとは？
- ローカルPCのWebサーバー（FastAPIなど）をインターネット経由で一時的に公開できるサービス
- LINE BOT開発ではWebhook受信のために必須

## 仕組み図
```
[LINE] ⇄ [ngrokクラウド] ⇄ [あなたのPC:8000(FastAPI)]
```

## インストール手順
### Windows
1. PowerShellで `./scripts/install-ngrok-windows.ps1` を実行
2. ngrok AuthTokenを https://dashboard.ngrok.com/get-started/your-authtoken で取得し、.envに設定

### Mac/Linux
1. ターミナルで `bash ./scripts/install-ngrok-mac.sh` を実行
2. ngrok AuthTokenを取得し、.envに設定

## AuthTokenの設定
- .envファイルの `NGROK_AUTHTOKEN` に貼り付け
- または `ngrok config add-authtoken <YourToken>` で手動設定

## 開発統合手順
1. `./scripts/start-dev.ps1`（Windows）または `./scripts/start-dev.sh`（Mac）で起動
2. ngrokのURLが自動表示される
3. LINE ConsoleのWebhook URLにコピー

## トラブルシューティング
- ngrokが起動しない → インストール・AuthToken設定を再確認
- URLが表示されない → ファイアウォールやポート競合を確認
- 無料プランはURLが毎回変わる点に注意

## セキュリティ注意
- AuthTokenは絶対にGit管理しない
- 本番運用には利用しない
- 公開URLは一時的なもの 