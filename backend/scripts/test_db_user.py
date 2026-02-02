"""Test database and user lookup"""
import asyncio
from app.core.database import async_session_maker
from sqlmodel import select
from app.models.sql_tables import User

async def test():
    async with async_session_maker() as session:
        stmt = select(User).limit(1)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user:
            print(f'Found user: {user.email}')
            print(f'Has metadata: {bool(user.meta_data)}')
            if user.meta_data:
                key_check = 'hashed_password' in user.meta_data
                print(f'Has password hash: {key_check}')
                if key_check:
                    print(f'Hash prefix: {user.meta_data["hashed_password"][:20]}...')
        else:
            print('No users found')

if __name__ == "__main__":
    asyncio.run(test())
