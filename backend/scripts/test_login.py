"""Test login for specific user"""
import asyncio
from app.core.database import async_session_maker
from sqlmodel import select
from app.models.sql_tables import User
from app.core.auth.password import verify_password

async def test():
    email = "nihalpardeshi12344@gmail.com"
    password = "Nihal@2005"
    
    async with async_session_maker() as session:
        stmt = select(User).where(User.email == email.lower().strip())
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            print(f'User not found: {email}')
            # List available users
            all_stmt = select(User.email)
            all_result = await session.execute(all_stmt)
            emails = [r[0] for r in all_result.fetchall()]
            print(f'Available users: {emails}')
            return
            
        print(f'Found user: {user.email}')
        print(f'User active: {user.is_active}')
        
        if user.meta_data and 'hashed_password' in user.meta_data:
            stored_hash = user.meta_data['hashed_password']
            print(f'Hash stored: {stored_hash[:30]}...')
            
            # Test password verification
            is_valid = verify_password(password, stored_hash)
            print(f'Password valid: {is_valid}')
        else:
            print('No password hash found in metadata!')
            print(f'Metadata: {user.meta_data}')

if __name__ == "__main__":
    asyncio.run(test())
