@echo off
REM チーム開発用セットアップスクリプト（Windows版）
REM このスクリプトを実行することで、他のメンバーも同じ開発環境を構築できます

echo 🚀 Bridge Line チーム開発環境セットアップ開始
echo ================================================

REM 1. Dockerコンテナの停止と削除
echo 📦 既存のDockerコンテナを停止・削除中...
docker-compose down -v

REM 2. データベースボリュームの削除（クリーンな状態から開始）
echo 🗑️  データベースボリュームを削除中...
docker volume rm section_9_team_a_postgres_data 2>nul

REM 3. Dockerコンテナの起動
echo 🐳 Dockerコンテナを起動中...
docker-compose up -d

REM 4. データベースの準備完了を待機
echo ⏳ データベースの準備完了を待機中...
timeout /t 30 /nobreak >nul

REM 5. マイグレーションの実行
echo 🔄 データベースマイグレーションを実行中...
cd backend
docker-compose exec backend alembic upgrade head

REM 6. 初期データの投入
echo 📊 初期データを投入中...
REM データベースが準備完了するまで待機
echo ⏳ データベースの準備完了を待機中...
:wait_loop
docker-compose exec postgres pg_isready -U bridge_user -d bridge_line_db >nul 2>&1
if errorlevel 1 (
    echo   データベースの準備中...
    timeout /t 5 /nobreak >nul
    goto wait_loop
)

REM 初期データを投入
echo 📊 SQLファイルを実行中...
docker-compose exec postgres psql -U bridge_user -d bridge_line_db -f /docker-entrypoint-initdb.d/export_current_data.sql

REM データ投入の確認
echo 🔍 データ投入結果を確認中...
docker-compose exec postgres psql -U bridge_line_db -c "SELECT COUNT(*) as user_count FROM users;"

REM 7. セットアップ完了
echo ✅ セットアップ完了！
echo ================================================
echo 🌐 フロントエンド: http://localhost:3000
echo 🔧 バックエンドAPI: http://localhost:8000
echo 📊 データベース: localhost:5432
echo.
echo 📝 利用可能なユーザー:
echo   管理者: admin@example.com
echo   テストユーザー: test-1@example.com, test-2@example.com, test-3@example.com, test-4@example.com
echo   チームメンバー: kodai@bridgeline.com, ucchi@bridgeline.com, asuka@bridgeline.com, rui@bridgeline.com, shizuka@bridgeline.com, erika@bridgeline.com
echo.
echo 🔑 パスワードは管理者にお問い合わせください
pause
