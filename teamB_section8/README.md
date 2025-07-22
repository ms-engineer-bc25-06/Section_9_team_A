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

## ディレクトリ構成

```
（省略：docs/api-reference.md参照）
```

---

## セットアップ手順

### 1. リポジトリをクローン
```
git clone <このリポジトリのURL>
cd linebot-project
```

### 2. 環境変数ファイルを作成
```
# .env.example をコピーして .env を作成
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows（PowerShell）
```

### 3. 自動セットアップスクリプトを実行
- **Windows**
  - PowerShellで `./setup.ps1` を実行
- **Mac/Linux**
  - ターミナルで `chmod +x setup.sh && ./setup.sh`

### 4. サービス起動
```
docker compose up --build
```

---

## 動作確認
- http://localhost:8000/health で "ok" が返ること
- LINE Webhook/DB/OpenAI連携が正常に動作すること

---

## トラブルシューティング
- Windows: [docs/troubleshooting-windows.md](docs/troubleshooting-windows.md)
- Mac: [docs/troubleshooting-mac.md](docs/troubleshooting-mac.md)

---

## チーム開発ルール
- [docs/team-rules.md](docs/team-rules.md)

---

## 重要
- **Windowsは必ずPowerShell構文で操作してください（`&&`やbash構文禁止）**
- **.envファイルは絶対にGit管理しないでください**
- **困ったら必ずドキュメントを参照してください** 