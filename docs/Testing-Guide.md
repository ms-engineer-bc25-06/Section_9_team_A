# 🧪 Bridge Line テスト実行ガイド

## 📋 概要

このガイドでは、Bridge Lineプロジェクトのテスト実行方法について説明します。フロントエンド（Next.js）とバックエンド（FastAPI）両方のテスト環境が整備されています。

## 🚀 クイックスタート

### 全テストを実行
```bash
# Makefileを使用
make test

# スクリプトを使用
./scripts/run-tests.sh

# 個別実行
make test-backend
make test-frontend
```

### 品質チェック
```bash
# 全体的な品質チェック
make quality

# クイックチェック（テストなし）
make quality-quick
```

## 🔧 フロントエンドテスト（Next.js）

### テスト環境
- **Jest**: ユニットテスト
- **Testing Library**: Reactコンポーネントテスト
- **Cypress**: E2Eテスト
- **ESLint**: コード品質チェック
- **Prettier**: コードフォーマット

### テスト実行
```bash
cd frontend

# 全テスト実行
npm test

# ウォッチモード
npm run test:watch

# カバレッジ付きテスト
npm run test:coverage

# CI用テスト
npm run test:ci

# E2Eテスト
npm run cypress:open  # インタラクティブ
npm run cypress:run   # ヘッドレス
```

### リンターとフォーマッター
```bash
# ESLint
npm run lint
npm run lint:fix

# Prettier
npm run format
npm run format:check

# 型チェック
npm run type-check
```

## 🐍 バックエンドテスト（FastAPI）

### テスト環境
- **Pytest**: テストフレームワーク
- **Pytest-asyncio**: 非同期テスト
- **Pytest-cov**: カバレッジ測定
- **Flake8**: Pythonリンター
- **Black**: コードフォーマッター
- **isort**: インポート整理
- **mypy**: 型チェック

### テスト実行
```bash
cd backend

# 全テスト実行
python -m pytest tests/ -v

# カバレッジ付きテスト
python -m pytest tests/ -v --cov=app --cov-report=html

# 特定のマーカーでテスト
python -m pytest tests/ -m "unit" -v
python -m pytest tests/ -m "integration" -v
python -m pytest tests/ -m "not slow" -v

# 並列実行
python -m pytest tests/ -n auto
```

### リンターとフォーマッター
```bash
# Flake8（コード品質チェック）
python -m flake8 app/ --max-line-length=88

# Black（コードフォーマット）
python -m black app/ --line-length=88
python -m black app/ --line-length=88 --check

# isort（インポート整理）
python -m isort app/ --profile=black
python -m isort app/ --profile=black --check-only

# mypy（型チェック）
python -m mypy app/ --ignore-missing-imports
```

## 📊 テストマーカー

### バックエンドテストマーカー
```bash
# ユニットテスト（高速、分離）
python -m pytest tests/ -m "unit"

# 統合テスト（中程度の速度、外部依存）
python -m pytest tests/ -m "integration"

# E2Eテスト（低速、全システム）
python -m pytest tests/ -m "e2e"

# データベーステスト
python -m pytest tests/ -m "database"

# 認証テスト
python -m pytest tests/ -m "auth"

# WebSocketテスト
python -m pytest tests/ -m "websocket"
```

### テストの実行順序
```bash
# 高速テストのみ
python -m pytest tests/ -m "not slow"

# 特定の層のテスト
python -m pytest tests/ -m "repository"
python -m pytest tests/ -m "service"
python -m pytest tests/ -m "api"
```

## 🎯 テスト戦略

### 1. ユニットテスト
- **対象**: 個別の関数、クラス、メソッド
- **特徴**: 高速、分離、モック使用
- **実行時間**: < 1秒

### 2. 統合テスト
- **対象**: 複数のコンポーネント間の連携
- **特徴**: 中程度の速度、外部依存あり
- **実行時間**: 1-10秒

### 3. E2Eテスト
- **対象**: 全システムの動作
- **特徴**: 低速、実際のブラウザ/API使用
- **実行時間**: > 10秒

## 📈 カバレッジ

### カバレッジ要件
- **全体**: 80%以上
- **重要モジュール**: 90%以上
- **新機能**: 90%以上

### カバレッジレポート
```bash
# ターミナル出力
python -m pytest tests/ --cov=app --cov-report=term-missing

# HTMLレポート
python -m pytest tests/ --cov=app --cov-report=html
# ブラウザで htmlcov/index.html を開く

# XMLレポート（CI用）
python -m pytest tests/ --cov=app --cov-report=xml
```

## 🚨 よくある問題と対処法

### フロントエンド
```bash
# 依存関係の問題
rm -rf node_modules package-lock.json
npm install

# Jest設定の問題
npm run test -- --verbose

# TypeScriptエラー
npm run type-check
```

### バックエンド
```bash
# 仮想環境の問題
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r requirements-dev.txt

# テストデータベースの問題
python -m pytest tests/ -m "not database"
```

## 🔄 CI/CD統合

### GitHub Actions
```yaml
# .github/workflows/test.yml の例
- name: Run Backend Tests
  run: |
    cd backend
    python -m pytest tests/ --cov=app --cov-report=xml

- name: Run Frontend Tests
  run: |
    cd frontend
    npm run test:ci
```

### ローカルCI
```bash
# コミット前の品質チェック
make quality-quick

# 全体的な品質チェック
make quality

# 特定のテストのみ
make test-backend-unit
make test-frontend-unit
```

## 📚 参考資料

- [Jest公式ドキュメント](https://jestjs.io/)
- [Testing Library公式ドキュメント](https://testing-library.com/)
- [Pytest公式ドキュメント](https://docs.pytest.org/)
- [ESLint公式ドキュメント](https://eslint.org/)
- [Black公式ドキュメント](https://black.readthedocs.io/)

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. **ログの確認**: エラーメッセージの詳細
2. **依存関係**: 必要なパッケージがインストールされているか
3. **環境設定**: 仮想環境、Node.jsバージョンなど
4. **チーム内共有**: エラーの詳細と環境情報

---

**🎉 テストを実行して、コードの品質を保ちましょう！**
