"""Remove US stocks from ticker_metadata table"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Bypass RLS

if not url or not service_key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(url, service_key)


def remove_us_stocks():
    """Delete all US stocks from ticker_metadata"""
    
    print("🗑️  Removing US stocks from database...")
    
    # First, count how many US stocks exist
    result = supabase.table("ticker_metadata").select("ticker", count="exact").eq("country", "US").execute()
    count = result.count if hasattr(result, 'count') else len(result.data)
    
    if count == 0:
        print("✅ No US stocks found in database")
        return
    
    print(f"   Found {count} US stocks to remove")
    
    # Delete all US stocks
    delete_result = supabase.table("ticker_metadata").delete().eq("country", "US").execute()
    
    print(f"✅ Deleted {count} US stocks")
    
    # Verify only Indian stocks remain
    indian_count = supabase.table("ticker_metadata").select("ticker", count="exact").eq("country", "IN").execute()
    indian_total = indian_count.count if hasattr(indian_count, 'count') else len(indian_count.data)
    
    print(f"\n📊 Summary:")
    print(f"   Removed: {count} US stocks")
    print(f"   Remaining: {indian_total} Indian stocks")


if __name__ == "__main__":
    remove_us_stocks()
