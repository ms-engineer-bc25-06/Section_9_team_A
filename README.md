# Bridge LINE - AI音声チャットアプリケーション

## 🧩 プロダクト概要

ハイブリッドワーク環境におけるチームコミュニケーションの質を高め、メンバーの隠れた特性を可視化するインテリジェント・コミュニケーションプラットフォームです。  
雑談からチームの深いつながりを生み出し、従業員エンゲージメント向上、離職率低下、生産性改善を実現します。

### 🧭 コンセプト

> **離れていても、つながる力を。**  
> 雑談からチームの深いつながりを生み出し、チーム全体の生産性とエンゲージメントを向上させます。

---

## 🌟 主な特徴

- 雑談ルームを通じて自然な会話を促進
- AIによる会話解析と個人プロファイル自動更新
- チームプロフィール共有機能
- Stripeによる決済機能
- 管理者ダッシュボード（決済管理・ユーザー数追加）

---

## 🍄 コア機能

| 機能名         | 説明 |
|----------------|------|
| ユーザー認証    | Firebase Authentication によるメール/パスワード認証 |
| メンバー一覧 　　| 部署別にメンバーとプロフィールの閲覧 |
| 雑談ルーム     | テーマボタン、ログイン中メンバー表示、音声通話 |
| 会話分析       | OpenAI Whisper で解析し、フィードバック作成 |
| マイプロフィール| 編集可能、公開/非公開設定、分析による特性自動追加 |


## 🎈 その他機能

| 機能名         | 説明 |
|----------------|------|
| 決済           | Stripe APIを利用 |
| 管理者ページ     | ユーザー管理・決済管理・組織運営の統合ダッシュボード |

---

## 🛠️ 技術スタック

| 区分           | 使用技術 |
|----------------|----------|
| フロントエンド | Next.js, TypeScript, Tailwind CSS, MUI |
| バックエンド   | FastAPI（Python）, SQLAlchemy, Alembic |
| DB             | PostgreSQL, Redis |
| AI・分析       | OpenAI Whisper, GPT-4, NumPy, Librosa, SciPy |
| 音声処理       | Web Socket, WebRTC, Pydub, SoundFile |
| 外部API        | OpenAI API, Firebase Authentication, Stripe API |
| 認証           | Firebase Authentication |
| 決済        　　| Stripe |
| テスト         | Vitest（FE）, Pytest（BE） |
| Linter         | ESLint（FE）, PyLint（BE） |
| Formatter      | Prettier（FE）, Black（BE） |
| インフラ       | Docker, Docker Compose |
| デザイン       | Figma, v0 |

---

## 🤝 チーム情報
- るい（リーダー） : 環境構築、雑談ルーム、会話分析
- しづか ： マイプロフィール
- あっすー ： ユーザー認証、メンバー一覧、決済、管理者ページ、UI

---

## 🚀 クイックスタート

### 前提条件
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose（DB・Redis・バックエンド用）
- Git

### 環境起動
```bash
# リポジトリのクローン
git clone <repository-url>
cd bridge-line

# 環境構築（推奨）
make setup

# または手動で
docker-compose up -d
```

### アクセスURL
- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **データベース**: http://localhost:5432
- **Redis**: http://localhost:6379

> 📚 **詳細なセットアップ手順**: [セットアップガイド.md](docs/セットアップガイド.md)



## 📁 プロジェクト構造
```
bridge-line/
├── backend/          # FastAPIバックエンド
├── frontend/         # Next.jsフロントエンド
├── scripts/          # セットアップスクリプト
├── docs/            # ドキュメント
├── compose.yaml     # Docker環境設定
└── README.md        # このファイル
```

> 📚 **詳細な構造説明**: [プロジェクト構造説明書.md](docs/プロジェクト構造説明書.md)



## 🔧 トラブルシューティング

### よくある問題
- Docker Desktopが起動していない
- ポートが既に使用されている
- データベース接続エラー

> 📚 **詳細な解決方法**: [セットアップガイド.md](docs/セットアップガイド.md#-トラブルシューティング)



## 📚 ドキュメント

### 開発関連
- [開発ルール](docs/開発ルール.md) - ブランチ運用、コミット規約、コード品質
- [API設計書](docs/API設計書.md) - REST API仕様
- [DB設計書](docs/DB設計書.md) - データベース設計
- [テスト仕様書](docs/テスト仕様書.md) - テスト実行方法

### セットアップ関連
- [セットアップガイド.md](docs/セットアップガイド.md) - 5分で環境起動
- [Installation-Checklist.md](docs/Installation-Checklist.md) - 詳細インストール手順
- [Windows-Setup-Guide.md](docs/Windows-Setup-Guide.md) - Windows環境セットアップ

### 設計・仕様
- [要件定義書](docs/要件定義書.md) - プロジェクト要件
- [アーキテクチャ図](docs/アーキテクチャ図.md) - システム構成
- [デザイン設計書](docs/デザイン設計書.md) - UI/UX設計



## 🆘 サポート

問題が発生した場合は、以下を確認してください：
1. Docker Desktopが起動しているか
2. ポートが競合していないか
3. 環境変数が正しく設定されているか

それでも解決しない場合は、チームリーダーに相談。


