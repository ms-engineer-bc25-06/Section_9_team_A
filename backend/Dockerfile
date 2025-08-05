# Python 3.11 slim imageを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
  gcc \
  g++ \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ヘルスチェックを追加
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# アプリケーションを起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
