"""Check existing tables in Neon database"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def check_tables():
    print("Connecting to Neon database...")
    try:
        async with engine.connect() as conn:
            # Query PostgreSQL system catalog for tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"\n✅ Found {len(tables)} table(s) in database:\n")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n⚠️ No tables found in database.")
                
            print("\n" + "="*50)
            print("Connection successful!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_tables())
