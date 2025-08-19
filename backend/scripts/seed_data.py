import sys
import os

# backend ディレクトリを sys.path に追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.config import settings  # DATABASE_URL が含まれている前提

# DATABASE_URL を async ではなく sync に変換
# asyncpg -> psycopg2 に置換
sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "")

# 通常のエンジン & セッションを定義（非async用）
engine = create_engine(sync_database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin_user():
    db = SessionLocal()

    firebase_uid = "YOUR_FIREBASE_UID"
    email = "admin@example.com"

    existing = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if existing:
        print("ユーザーはすでに存在します")
        return

    admin_user = User(
        firebase_uid=firebase_uid,
        email=email,
        is_admin=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("管理者ユーザーを作成しました:", admin_user.email)

if __name__ == "__main__":
    create_admin_user()