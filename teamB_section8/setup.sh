#!/bin/bash
# =============================
# Mac/Linux用セットアップスクリプト
# =============================
# 実行方法: bash ./setup.sh

set -e

echo "[1/4] Docker Desktopの起動確認..."
docker info > /dev/null 2>&1 || { echo "Docker Desktopが起動していません。起動してから再実行してください。"; exit 1; }

echo "[2/4] .envファイル存在確認..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".envファイルを .env.example から自動生成しました。"
fi

echo "[3/4] ファイル権限設定..."
chmod -R 755 ./app ./data

echo "[4/4] Docker Compose起動テスト..."
docker compose up --build 