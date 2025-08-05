-- Bridge Line Database Initialization Script
-- データベースの作成（既に存在する場合はスキップ）
-- このスクリプトはdocker-entrypoint-initdb.dで実行されるため、
-- データベースは既に作成されている
-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 基本的なテーブル構造の作成
-- 注意: 実際のテーブルはAlembicマイグレーションで作成されます
-- テスト用データベースの作成（開発環境用）
-- このスクリプトは本番データベースでのみ実行されるため、
-- テストデータベースは別途作成が必要
-- 基本的な権限設定
GRANT ALL PRIVILEGES ON DATABASE bridge_line_db TO bridge_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bridge_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bridge_user;

-- 将来のテーブルに対する権限も設定
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bridge_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bridge_user;