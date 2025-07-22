# APIリファレンス

## 1. ヘルスチェック
### GET /health
- サーバー稼働確認用
- レスポンス例: `{ "status": "ok" }`

## 2. LINE Webhook
### POST /webhook
- LINEプラットフォームからのWebhookイベント受信
- ヘッダー: `X-Line-Signature` 必須
- リクエストボディ: LINE Messaging API仕様に準拠
- レスポンス例: `{ "result": "OpenAI応答テキスト" }`
- エラー例:
    - 400: 署名検証失敗
    - 500: サーバー内部エラー

## 3. OpenAI連携（内部呼び出し）
- サービス内で `chat_with_openai(prompt: str)` を利用
- レスポンス例: OpenAI APIの応答テキスト

---

## 認証
- LINE Webhookは署名検証必須
- OpenAI APIキーは環境変数で管理

---

## 注意
- すべてのエンドポイントはJSON形式で応答
- 詳細はソースコード・コメント参照 