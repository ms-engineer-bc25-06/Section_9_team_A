# 旧式のトークン検証の依存関数（参考用 - 現在は app/api/deps.py を使用）
# 
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer
# from firebase_admin import auth as firebase_auth
# 
# security = HTTPBearer()
# 
# def verify_firebase_token(credentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         decoded_token = firebase_auth.verify_id_token(token)
#         return decoded_token
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# デバッグ用の認証関数（トラブルシューティング時に参考）
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer
# from firebase_admin import auth as firebase_auth
# 
# security = HTTPBearer()
# 
# def get_current_user(credentials=Depends(security)):
#     token = credentials.credentials
#     print("📥 APIで受信したAuthorizationトークン:", token)
# 
#     try:
#         decoded_token = firebase_auth.verify_id_token(token)
#         print("✅ Firebaseで検証成功:", decoded_token)
#         return decoded_token
#     except Exception as e:
#         print("❌ Firebaseトークン検証エラー:", str(e))
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# 注意: このファイルは現在使用されていません
# 実際の認証は app/api/deps.py の get_current_user を使用
