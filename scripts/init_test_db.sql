-- Bridge Line Test Database Initialization Script
-- テストデータベースの作成と初期化

-- テストデータベースの作成（既に存在する場合はスキップ）
SELECT 'CREATE DATABASE bridge_line_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bridge_line_test_db')\gexec

-- テストデータベースに接続して拡張機能を有効化
\c bridge_line_test_db;

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 基本的な権限設定
GRANT ALL PRIVILEGES ON DATABASE bridge_line_test_db TO bridge_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bridge_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bridge_user;

-- 将来のテーブルに対する権限も設定
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bridge_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bridge_user;
