# Makeコマンドインストール・運用ガイド

## 概要

このガイドでは、Windows環境でMakeコマンドをインストールし、Bridge Line開発環境で使用する方法を説明します。

## 前提条件

- Windows 10/11
- Docker Desktopがインストール済み
- PowerShellまたはコマンドプロンプトが使用可能

## インストール方法

### 方法1: Chocolateyを使用（推奨）

#### 1. Chocolateyのインストール

**PowerShellを管理者として実行**し、以下のコマンドを実行：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 2. Makeのインストール

```cmd
choco install make
```

#### 3. インストール確認

```cmd
make --version
```

### 方法2: MSYS2を使用

#### 1. MSYS2のインストール

1. [MSYS2公式サイト](https://www.msys2.org/)からインストーラーをダウンロード
2. インストーラーを実行
3. MSYS2ターミナルを開く

#### 2. Makeのインストール

```bash
pacman -S make
```

#### 3. 環境変数の設定

MSYS2のbinディレクトリをPATHに追加（例：`C:\msys64\usr\bin`）

### 方法3: WSL2を使用

#### 1. WSL2のインストール

```cmd
wsl --install
```

#### 2. UbuntuでMakeをインストール

```bash
sudo apt update
sudo apt install make
```

## 使用方法

### 基本的なコマンド

```cmd
# ヘルプの表示
make help

# 環境の起動
make start

# 環境の停止
make stop

# 環境の再起動
make restart

# ログの確認
make logs

# バックエンドの状態確認
make backend-status

# テストの実行
make test

# データベースマイグレーション
make migrate
```

### 開発用コマンド

```cmd
# バックエンドサービスのみ起動
make backend-start

# バックエンドサービスのみ再起動
make backend-restart

# バックエンドのデバッグ情報
make backend-debug

# バックエンドのシェルアクセス
make backend-shell

# データベースのシェルアクセス
make db-shell
```

### データベース関連

```cmd
# データベース接続テスト
make db-test-connection

# マイグレーション状況確認
make db-check-migrations

# データベースリセット
make db-reset
```

## トラブルシューティング

### よくある問題

#### 1. "make"コマンドが見つからない

**原因**: Makeがインストールされていない、またはPATHが通っていない

**解決方法**:
```cmd
# インストール確認
choco list --local-only make

# 再インストール
choco uninstall make
choco install make

# PATH確認
echo %PATH%
```

#### 2. Makefileの構文エラー

**原因**: Windows環境での改行コードの問題

**解決方法**:
```cmd
# Git設定で改行コードを統一
git config --global core.autocrlf true

# ファイルの改行コードを確認
file Makefile
```

#### 3. Dockerコマンドが実行できない

**原因**: Docker Desktopが起動していない

**解決方法**:
- Docker Desktopを起動
- システムトレイのDockerアイコンが緑色になっていることを確認

### エラーログの確認

```cmd
# 詳細なエラー情報を表示
make start 2>&1

# Dockerログの確認
docker compose logs --tail=50
```

## 代替手段

### Makeコマンドが使えない場合

#### 1. PowerShellスクリプトを使用

```powershell
# 実行権限を設定
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# スクリプトを実行
.\scripts\dev-setup.ps1
```

#### 2. バッチファイルを使用

```cmd
scripts\dev-setup.bat
```

#### 3. 手動でコマンドを実行

```cmd
# データベースサービスを起動
docker compose up -d postgres redis

# 少し待ってからバックエンドサービスを起動
timeout /t 20 /nobreak
docker compose up -d backend

# サービスの状態を確認
docker compose ps
```

## 運用のベストプラクティス

### 1. 日常的な操作

```cmd
# 開発開始時
make start

# 開発終了時
make stop

# 問題が発生した場合
make restart
```

### 2. デバッグ時

```cmd
# バックエンドの状態確認
make backend-status

# 詳細なログ確認
make backend-debug

# 特定のサービスのログ
docker compose logs -f backend
```

### 3. テスト実行時

```cmd
# 全テストの実行
make test

# データベーステストのみ
make test-db

# ユニットテストのみ
make test-db-unit
```

## サポート情報

### 参考資料

- [Windows-Setup-Guide.md](./Windows-Setup-Guide.md) - Windows環境でのセットアップ詳細
- [README.md](../README.md) - プロジェクト全体の概要

### 問題が解決しない場合

1. **ログの確認**: `docker compose logs --tail=100`
2. **Dockerの状態確認**: `docker info`
3. **Makefileの構文チェック**: `make -n start`（実際には実行せずに構文チェック）
4. **チーム内での共有**: エラーメッセージとログを共有

### 連絡先

技術的な問題が解決しない場合は、以下を確認の上、チーム内で共有してください：

- エラーメッセージの全文
- 実行したコマンド
- 環境情報（Windowsバージョン、Dockerバージョン、Makeバージョン）
- ログファイルの内容
