# Windows環境でのBridge Line開発環境セットアップ

## 前提条件

### 1. Docker Desktopのインストール
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) をダウンロードしてインストール
- WSL2（Windows Subsystem for Linux 2）が有効になっていることを確認
- Docker Desktopを起動して、Docker Engineが動作していることを確認

### 2. 必要なツール
- **PowerShell**（Windows 10/11に標準搭載）
- **コマンドプロンプト**（Windowsに標準搭載）

## セットアップ方法

### 方法1: PowerShellスクリプトを使用（推奨）

1. **PowerShellを管理者として実行**
   - Windowsキー + X → "Windows PowerShell (管理者)" を選択

2. **スクリプトの実行権限を設定**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **セットアップスクリプトを実行**
   ```powershell
   .\scripts\dev-setup.ps1
   ```

### 方法2: バッチファイルを使用

1. **コマンドプロンプトを管理者として実行**
   - Windowsキー + R → "cmd" と入力 → Ctrl + Shift + Enter

2. **セットアップスクリプトを実行**
   ```cmd
   scripts\dev-setup.bat
   ```

### 方法3: 手動でコマンドを実行

1. **PowerShellまたはコマンドプロンプトを開く**

2. **データベースサービスを起動**
   ```cmd
   docker compose up -d postgres redis
   ```

3. **少し待ってからバックエンドサービスを起動**
   ```cmd
   docker compose up -d backend
   ```

4. **サービスの状態を確認**
   ```cmd
   docker compose ps
   ```

## トラブルシューティング

### よくある問題と解決方法

#### 1. "make"コマンドが見つからない
**問題**: Windowsでは`make`コマンドが標準でインストールされていません。

**解決方法**: 
- 上記のPowerShellスクリプトまたはバッチファイルを使用
- または、[Chocolatey](https://chocolatey.org/)を使用してMakeをインストール：
  ```cmd
  choco install make
  ```

#### 2. Dockerが起動していない
**問題**: Docker Desktopが起動していない、またはDocker Engineが動作していない。

**解決方法**:
- Docker Desktopを起動
- システムトレイのDockerアイコンが緑色になっていることを確認
- 必要に応じてDocker Desktopを再起動

#### 3. ポートが既に使用されている
**問題**: 8000番ポートが他のアプリケーションで使用されている。

**解決方法**:
- 他のアプリケーションを停止
- または、`compose.yaml`でポート番号を変更

#### 4. WSL2の問題
**問題**: WSL2が有効になっていない、または更新が必要。

**解決方法**:
```cmd
wsl --update
wsl --shutdown
```
その後、Docker Desktopを再起動

## 開発用コマンド

### 基本的な操作

```cmd
# 環境の起動
docker compose up -d

# 環境の停止
docker compose down

# ログの確認
docker compose logs -f

# 特定のサービスのログ
docker compose logs -f backend

# サービスの状態確認
docker compose ps

# 環境の再起動
docker compose restart
```

### データベース関連

```cmd
# マイグレーションの実行
docker exec bridge_line_backend alembic upgrade head

# データベースの状態確認
docker exec bridge_line_postgres psql -U bridge_user -d bridge_line_db -c "\dt"
```

### バックエンド関連

```cmd
# バックエンドサービスの再起動
docker compose restart backend

# バックエンドのシェルアクセス
docker exec -it bridge_line_backend /bin/bash

# テストの実行
docker exec bridge_line_backend pytest
```

## アクセスURL

環境が正常に起動したら、以下のURLでアクセスできます：

- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **データベース**: localhost:5432
- **Redis**: localhost:6379

## サポート

問題が解決しない場合は、以下を確認してください：

1. Docker Desktopのバージョン（最新版を推奨）
2. Windowsのバージョン（Windows 10 1903以降を推奨）
3. WSL2のバージョン
4. ファイアウォールの設定

詳細なログは以下で確認できます：
```cmd
docker compose logs --tail=100
```
