# GitHub設定ガイド

## CI/CD設定の反映について

### 自動反映される設定
- `.github/workflows/` 内のYAMLファイル
- プッシュ時に自動的にGitHub Actionsが認識

### 手動設定が必要な項目

## 1. GitHub Secrets の設定

### リポジトリの設定方法
1. GitHubリポジトリページにアクセス
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** をクリック

### 必要なシークレット

#### **Docker Hub認証情報**
```
DOCKER_USERNAME: Docker Hubのユーザー名
DOCKER_PASSWORD: Docker Hubのパスワードまたはアクセストークン
```

#### **Vercel認証情報（フロントエンドデプロイ用）**
```
VERCEL_TOKEN: Vercelのアクセストークン
VERCEL_ORG_ID: Vercelの組織ID
VERCEL_PROJECT_ID: VercelのプロジェクトID
```

#### **Codecov認証情報（テストカバレッジ用）**
```
CODECOV_TOKEN: Codecovのアクセストークン
```

## 2. GitHub Actions の有効化

### 確認方法
1. GitHubリポジトリページにアクセス
2. **Actions** タブをクリック
3. ワークフローが表示されることを確認

### 権限設定
1. **Settings** → **Actions** → **General**
2. **Actions permissions** で以下を設定：
   - **Allow all actions and reusable workflows**
   - **Allow GitHub Actions to create and approve pull requests**

## 3. ブランチ保護ルール（推奨）

### 設定方法
1. **Settings** → **Branches**
2. **Add rule** をクリック
3. 以下の設定を追加：

#### **mainブランチの保護**
```
Branch name pattern: main
Require a pull request before merging: ✅
Require status checks to pass before merging: ✅
Require branches to be up to date before merging: ✅
Status checks that are required:
- Backend CI/CD / test
- Frontend CI/CD / test
- E2E Tests / e2e-tests
```

#### **developブランチの保護**
```
Branch name pattern: develop
Require a pull request before merging: ✅
Require status checks to pass before merging: ✅
Require branches to be up to date before merging: ✅
Status checks that are required:
- Backend CI/CD / test
- Frontend CI/CD / test
```

## 4. プルリクエストテンプレート

### 自動反映される設定
- `.github/pull_request_template.md` が自動的に使用される
- プルリクエスト作成時にテンプレートが表示される

### テンプレートの内容
```markdown
# プルリクエスト

## 概要
## 変更内容
## 関連Issue
## テスト
## チェックリスト
## デプロイ
## スクリーンショット
## 技術的な詳細
## 注意事項
## 参考資料
```

## 5. 外部サービスとの連携

### Codecov設定
1. [Codecov](https://codecov.io) にアクセス
2. GitHubアカウントでログイン
3. リポジトリを追加
4. トークンを取得してGitHub Secretsに追加

### Vercel設定
1. [Vercel](https://vercel.com) にアクセス
2. GitHubアカウントでログイン
3. プロジェクトを作成
4. 認証情報を取得してGitHub Secretsに追加

## 6. 設定確認手順

### 初回プッシュ後の確認
```bash
# 1. GitHubリポジトリのActionsタブを確認
# 2. ワークフローが実行されているかチェック
# 3. エラーがないかログを確認
```

### テスト実行の確認
```bash
# プルリクエストを作成して以下を確認：
- Backend CI/CD が実行される
- Frontend CI/CD が実行される
- E2E Tests が実行される
```

### テンプレートの確認
```bash
# 1. プルリクエスト作成時にテンプレートが表示されるか確認
```

## 7. トラブルシューティング

### よくある問題

#### **ワークフローが実行されない**
- GitHub Actionsが有効になっているか確認
- `.github/workflows/` 内のファイルが正しい形式か確認

#### **シークレットが見つからないエラー**
- GitHub Secretsが正しく設定されているか確認
- シークレット名がYAMLファイルと一致しているか確認

#### **Docker認証エラー**
- Docker Hubの認証情報が正しいか確認
- アクセストークンが有効か確認

#### **Vercelデプロイエラー**
- Vercelプロジェクトが正しく設定されているか確認
- 認証情報が正しいか確認

#### **テンプレートが表示されない**
- ファイル名が正しいか確認
- ファイルの場所が正しいか確認

## 8. 段階的な設定

### Phase 1: 基本的なCI/CD（今すぐ）
```bash
# 必要な設定
- GitHub Actions の有効化
- 基本的なシークレット設定（DOCKER_USERNAME, DOCKER_PASSWORD）
```

### Phase 2: テストカバレッジ（開発が進んでから）
```bash
# 追加設定
- Codecov設定
- カバレッジレポートの確認
```

### Phase 3: プレビューデプロイ（機能が安定してから）
```bash
# 追加設定
- Vercel設定
- プレビュー環境の構築
```

## 9. チーム向け設定

### チームメンバー向けガイド
```bash
# 新規メンバーが追加された場合
1. GitHubリポジトリへのアクセス権限付与
2. ブランチ保護ルールの確認
3. CI/CDの動作確認
4. テンプレートの使用方法説明
```

### 開発フロー
```bash
# 推奨フロー
1. featureブランチで開発
2. プルリクエスト作成（テンプレート使用）
3. CI/CDテストの実行確認
4. レビュー・マージ
```

### テンプレートの活用
```bash
# プルリクエスト作成時
1. テンプレートに従って情報を記載
2. チェックリストを確認
3. 関連Issueをリンク
``` 