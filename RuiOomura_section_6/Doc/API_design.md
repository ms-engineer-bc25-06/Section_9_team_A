API設計書
自己紹介(ポートフォリオ)サイト


API概要
ベースURL：http://localhost:4000
認証：Firebase
データ形式：JSON
バージョン：v1

エンドポイント一覧
ユーザー管理
エンドポイント：
メソッド：
説明：ユーザー情報の登録・取得
リクエスト例：
POST /users
レスポンス例：
{
    "users": [
        {
            "user_id": 1,
            "user_name": "山田　花子",
            "user_nickname": "はなちゃん",
            "user_mailAdress": "hanachan_0101@gmail.com",
            "user_password": "abcd1234"
        }
    ]
    
}

画像管理
エンドポイント：
メソッド：
説明：TOP画像の管理
リクエスト例：
POST /top_images
レスポンス例
{
    "top_image": [
        {
            "id": 1,
            "image_file_path": "https://storage.example.com/images/top_image"
            "register_at": "2025-07-01M08:00+09:00",
            "user_id": 1
        }
        
    ]
}

ポートフォリオ管理
エンドポイント：
メソッド：
説明：実績・スキルの登録・編集・削除
リクエスト例
POST /portfolios
レスポンス例：
{
    "portfolios": [
        {
            "id": 1,
            "result": "家計簿アプリ作成",
            "skill": "JavaScript, TypeScript, HTML, 
        }
    ]
    CSS"
}

入力情報管理(?)



認証
方式：
