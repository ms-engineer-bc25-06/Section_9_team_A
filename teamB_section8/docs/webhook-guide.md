# LINE Webhook設定ガイド

## 1. Webhookとは？
- LINEプラットフォームからのイベント（メッセージ受信など）を自動で受け取る仕組み
- ngrokでローカル開発サーバーを一時的に外部公開し、LINEからアクセス可能にする

## 2. Webhook URLの取得
- `./scripts/start-dev.ps1` または `./scripts/start-dev.sh` を実行
- 表示された `https://xxxx.ngrok.io/webhook` をコピー

## 3. LINE Developers Consoleでの設定
1. https://developers.line.biz/console/ へアクセス
2. 対象のプロバイダ・チャネルを選択
3. 「Messaging API」設定画面で「Webhook送信」→「利用する」にON
4. 「Webhook URL」欄にコピーしたURLを貼り付け
5. 「検証」ボタンで正常応答（200/OK）を確認

## 4. QRコードで友だち追加
- チャネルのQRコードをスマホで読み取り、BOTを友だち追加

## 5. 注意点
- ngrok無料プランはURLが毎回変わるため、起動ごとに再設定が必要
- Webhook URLは `/webhook` で終わることを確認
- テスト時はngrok・FastAPI両方が起動していること

## 6. トラブル時
- 200以外の応答 → FastAPIアプリ・ngrokのログを確認
- URL貼り間違い → `/webhook` 付きURLか再確認 