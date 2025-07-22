# LINE BOT 開発環境（Windows/Mac両対応・初学者向け）

## 概要
このプロジェクトは、Windows/Mac混合チームでLINE BOT（FastAPI＋OpenAI＋SQLite）を安全・簡単に開発できる環境を提供します。

- **バックエンド**: Python FastAPI
- **DB**: SQLite（永続化）
- **AI連携**: OpenAI API
- **コンテナ**: Docker Compose V2
- **クロスプラットフォーム**: Windows/Mac両対応
- **初学者向け**: コメント・手順・エラー対策充実

---

## ngrokによるWebhook開発の自動化

### 1. ngrokインストール
- Windows: `./scripts/install-ngrok-windows.ps1` をPowerShellで実行
- Mac: `bash ./scripts/install-ngrok-mac.sh` をターミナルで実行
- AuthTokenは https://dashboard.ngrok.com/get-started/your-authtoken で取得し、.envに設定

### 2. 統合起動
- Windows: `./scripts/start-dev.ps1`
- Mac: `./scripts/start-dev.sh`
- ngrokのURLが自動表示されるので、LINE ConsoleのWebhook URLにコピー

### 3. 統合停止
- Windows: `./scripts/stop-dev.ps1`
- Mac: `./scripts/stop-dev.sh`

---

## Webhook設定ガイド
- [docs/webhook-guide.md](docs/webhook-guide.md) を参照

---

## 詳細なngrokセットアップ・トラブル対応
- [docs/ngrok-setup.md](docs/ngrok-setup.md) を参照

---

## 旧来の手動起動手順
（ngrokを使わない場合）
```
docker compose up --build
```

---

## その他のセットアップ・運用手順
（省略：docs/api-reference.md参照） 