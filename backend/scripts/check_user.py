"""Check if user exists in database"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def check_user(email: str):
    print(f"Checking for user: {email}")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT id, email, full_name, is_active, created_at 
                FROM users 
                WHERE email = :email
            """), {"email": email})
            user = result.fetchone()
            
            if user:
                print(f"\n✅ User found:")
                print(f"   ID: {user[0]}")
                print(f"   Email: {user[1]}")
                print(f"   Name: {user[2]}")
                print(f"   Active: {user[3]}")
                print(f"   Created: {user[4]}")
            else:
                print(f"\n⚠️ User NOT found with email: {email}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user("nihalpardeshi12344@gmail.com"))
