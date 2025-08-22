# 🚀 BridgeLINE Frontend 環境変数設定ガイド

## 📋 概要
このガイドでは、BridgeLINEフロントエンドアプリケーションの環境変数設定方法を説明します。

## 🔧 ローカル開発環境

### 1. `.env.local`ファイルの作成
フロントエンドディレクトリに`.env.local`ファイルを作成してください：

```bash
# frontendディレクトリで実行
touch .env.local
```

### 2. 必要な環境変数

#### **API関連**
```env
# バックエンドAPIのベースURL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### **Firebase認証**
```env
# Firebase設定（実際の値に置き換えてください）
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key-here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=your-firebase-app-id
```

#### **Stripe決済**
```env
# Stripe公開可能キー（テスト用）
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_test_key_here
```

#### **OpenAI**
```env
# OpenAI APIキー
NEXT_PUBLIC_OPENAI_API_KEY=your-openai-api-key-here
```

#### **WebSocket**
```env
# WebSocket接続URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
```

## 🌐 本番環境（Vercel）

### 1. Vercelダッシュボードでの設定
1. [Vercel](https://vercel.com)にログイン
2. BridgeLINEプロジェクトを選択
3. Settings → Environment Variables に移動
4. 以下の環境変数を追加：

**重要**: 本番環境では必ず本番用のAPIキーとドメインを使用してください。

#### **本番用API設定**
```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

#### **本番用Firebase設定**
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-production-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-production-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-production-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-production-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-production-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-production-app-id
```

#### **本番用Stripe設定**
```env
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_live_key_here
```

#### **本番用OpenAI設定**
```env
NEXT_PUBLIC_OPENAI_API_KEY=your-production-openai-api-key
```

#### **本番用WebSocket設定**
```env
NEXT_PUBLIC_WS_URL=wss://your-backend-domain.com/ws
NEXT_PUBLIC_WS_BASE_URL=wss://your-backend-domain.com
```

### 2. 環境別の設定
Vercelでは、環境別に環境変数を設定できます：

- **Production**: 本番環境
- **Preview**: プレビュー環境（PR時）
- **Development**: 開発環境

## 🔒 セキュリティ注意事項

### ✅ 安全な設定
- `NEXT_PUBLIC_`で始まる環境変数はクライアントサイドで公開されます
- 機密情報（APIキーなど）は適切に管理してください
- 本番環境では本番用のAPIキーを使用してください

### ❌ 避けるべき設定
- 機密情報を`.env.local`にハードコーディングしない
- 環境変数ファイルをGitにコミットしない
- 本番環境でテスト用のAPIキーを使用しない

## 🧪 テスト方法

### 1. ローカル環境でのテスト
```bash
# フロントエンドディレクトリで実行
npm run dev
```

### 2. 環境変数の確認
ブラウザの開発者ツールで以下を確認：
```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
console.log('Firebase Project ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID);
```

## 📚 参考リンク

- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Firebase Configuration](https://firebase.google.com/docs/web/setup)
- [Stripe Configuration](https://stripe.com/docs/keys)

## 🆘 トラブルシューティング

### よくある問題
1. **環境変数が読み込まれない**
   - ファイル名が`.env.local`になっているか確認
   - アプリケーションを再起動

2. **本番環境で環境変数が反映されない**
   - Vercelで環境変数を設定後、再デプロイが必要
   - 環境変数の名前が正しいか確認

3. **Firebase接続エラー**
   - APIキーとプロジェクトIDが正しいか確認
   - Firebaseコンソールで設定を確認

---

**注意**: このガイドは開発環境での設定例です。本番環境では適切なセキュリティ対策を講じてください。
