# ベースイメージ（Python 3.11）
FROM python:3.11-slim

# 作業ディレクトリ作成
WORKDIR /app

# OSパッケージ更新・必要ツールインストール（dos2unix含む）
RUN apt-get update && \
  apt-get install -y --no-install-recommends dos2unix build-essential && \
  rm -rf /var/lib/apt/lists/*

# 依存関係ファイルコピー
COPY requirements.txt ./

# 依存関係インストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードコピー
COPY . .

# 行末文字（CRLF→LF）変換（Windows/Mac混在対策）
RUN find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.env" \) -exec dos2unix {} +

# ポート開放
EXPOSE 8000

# 環境変数（例：Pythonのバッファリング無効化）
ENV PYTHONUNBUFFERED=1

# 実行コマンド（uvicornでFastAPI起動・ホットリロード）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 