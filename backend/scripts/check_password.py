"""Check user's stored password hash"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def check_user_password(email: str):
    print(f"Checking password hash for: {email}")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT id, email, metadata 
                FROM users 
                WHERE email = :email
            """), {"email": email})
            user = result.fetchone()
            
            if user:
                print(f"\n✅ User found: {user[1]}")
                metadata = user[2]
                if metadata:
                    print(f"   Metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")
                    if isinstance(metadata, dict) and 'hashed_password' in metadata:
                        hash_val = metadata['hashed_password']
                        print(f"   Password hash exists: {'Yes' if hash_val else 'No'}")
                        print(f"   Hash preview: {hash_val[:30]}..." if hash_val else "   No hash!")
                    else:
                        print("   ⚠️ No hashed_password in metadata!")
                else:
                    print("   ⚠️ User has no metadata!")
            else:
                print(f"\n⚠️ User NOT found")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_password("nihalpardeshi12344@gmail.com"))
