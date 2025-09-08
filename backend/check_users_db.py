import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_users():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            print(f'Total users: {len(users)}')
            for user in users:
                print(f'ID: {user.id}, Email: {user.email}, Username: {user.username}, Full Name: {user.full_name}')
                if user.firebase_uid:
                    print(f'  Firebase UID: {user.firebase_uid}')
                else:
                    print(f'  Firebase UID: None')
                print('---')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_users())
