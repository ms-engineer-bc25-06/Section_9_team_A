# 🚀 Bridge Line 開発環境 クイックスタートガイド

## 📋 5分で環境を起動！

### 方法1: Makeコマンドを使用（推奨）

#### 1. Makeコマンドをインストール

**PowerShellを管理者として実行**し、以下をコピペ：

```powershell
choco install make
```

#### 2. 環境を起動

```cmd
make start
```

#### 3. 完了！

ブラウザで以下にアクセス：
- **API**: http://localhost:8000
- **ドキュメント**: http://localhost:8000/docs

---

### 方法2: PowerShellスクリプトを使用

#### 1. 実行権限を設定

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. スクリプトを実行

```powershell
.\scripts\dev-setup.ps1
```

---

### 方法3: 手動でコマンド実行

```cmd
docker compose up -d postgres redis
timeout /t 20 /nobreak
docker compose up -d backend
docker compose ps
```

---

## 🔧 日常的な操作

### 開発開始時
```cmd
make start
```

### 開発終了時
```cmd
make stop
```

### 問題が発生した場合
```cmd
make restart
```

### ログを確認
```cmd
make logs
```

---

## ❓ トラブルシューティング

### Makeコマンドが見つからない
```cmd
choco install make
```

### Dockerが起動していない
- Docker Desktopを起動
- システムトレイのアイコンが緑色になっていることを確認

### ポートが使用中
```cmd
netstat -ano | findstr :8000
```

---

## 📚 詳細情報

- **Makeコマンド詳細**: [Make-Installation-Guide.md](./Make-Installation-Guide.md)
- **Windows環境詳細**: [Windows-Setup-Guide.md](./Windows-Setup-Guide.md)
- **プロジェクト概要**: [README.md](../README.md)

---

## 🆘 サポート

問題が解決しない場合は、以下をチーム内で共有：

1. エラーメッセージの全文
2. 実行したコマンド
3. `docker compose ps` の結果
4. `docker compose logs --tail=20` の結果

---

## 💡 便利なコマンド一覧

```cmd
make help          # 全コマンド一覧
make start         # 環境起動
make stop          # 環境停止
make restart       # 環境再起動
make logs          # ログ表示
make test          # テスト実行
make migrate       # DBマイグレーション
make backend-status # バックエンド状態確認
make backend-debug  # バックエンドデバッグ
```
