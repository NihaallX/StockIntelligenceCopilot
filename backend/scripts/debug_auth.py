import asyncio
import sys
import os
sys.path.append(os.getcwd())

from sqlmodel import select
from app.core.database import async_session_maker
from app.models.sql_tables import User, UserRiskProfile
from app.api.v1.auth import RiskTolerance, hash_password
from datetime import datetime
import uuid

async def main():
    print("Starting debug_auth...")
    async with async_session_maker() as session:
        try:
            print("Session created.")
            email = f"debug_{uuid.uuid4().hex[:8]}@example.com"
            print(f"Creating user {email}")
            
            new_user = User(
                email=email,
                full_name="Debug User",
                terms_accepted_at=datetime.utcnow(),
                terms_version="1.0",
                risk_acknowledgment_at=datetime.utcnow(),
                is_active=True,
                meta_data={"hashed_password": hash_password("Password123!")}
            )
            
            print("Adding user to session...")
            session.add(new_user)
            print("Committing user...")
            await session.commit()
            print("Refreshing user...")
            await session.refresh(new_user)
            print(f"User created with ID: {new_user.id}")
            
            print("Creating risk profile...")
            rp = UserRiskProfile(
                user_id=new_user.id,
                risk_tolerance=RiskTolerance.CONSERVATIVE.value
            )
            session.add(rp)
            print("Committing risk profile...")
            await session.commit()
            print("Risk profile created.")
            
            print("✅ SUCCESS: Auth flow simulated correctly.")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
