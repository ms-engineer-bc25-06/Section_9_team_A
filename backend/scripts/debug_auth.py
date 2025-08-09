"""
認証フロー詳細デバッグ
"""

print("🔍 認証デバッグ開始")

# まず現在のデータベース状態を確認
try:
    from check_users import *
    print("✅ 既存のチェック機能を使用")
except Exception as e:
    print(f"❌ インポートエラー: {e}")
    print("💡 代替手段で確認します")

print("""
📋 管理者ログイン失敗の原因分析:

🔍 確認すべき項目:
1. バックエンドが正常に起動しているか
2. フロントエンドのFirebase設定
3. IDトークンの生成と送信
4. Custom Claimsの設定

🧪 手動テスト手順:
1. ブラウザでフロントエンドにアクセス
2. admin@example.com でログイン
3. ブラウザ開発者ツール → Console でエラー確認
4. Network タブで API呼び出し確認

💡 よくある問題:
- IDトークンの期限切れ
- フロントエンドとバックエンドのFirebase設定不一致
- トークンヘッダーの形式間違い
""")