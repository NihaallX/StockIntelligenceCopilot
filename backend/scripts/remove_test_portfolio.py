"""Remove test positions from testuser_phase2b@example.com"""
import sys
sys.path.insert(0, 'D:/Stock Intelligence Copilot/backend')

from app.core.database import get_service_db

db = get_service_db()

# Find test user
test_email = "testuser_phase2b@example.com"
print(f"🔍 Looking for test user: {test_email}")

users_result = db.table('users').select('id,email').eq('email', test_email).execute()

if not users_result.data:
    print(f"✅ User not found - nothing to clean up")
    sys.exit(0)

user = users_result.data[0]
user_id = user['id']
print(f"✅ Found: {user['email']} (ID: {user_id[:8]}...)")

# Get current positions
print("\n📊 Current positions:")
portfolio_result = db.table('portfolio_positions').select('*').eq('user_id', user_id).execute()

if not portfolio_result.data:
    print("   ❌ No positions to remove")
    sys.exit(0)

print(f"   Found {len(portfolio_result.data)} positions:")
for pos in portfolio_result.data:
    print(f"   • {pos['ticker']} - {pos['quantity']} shares")

# Delete all positions
print(f"\n🗑️  Deleting {len(portfolio_result.data)} positions...")
result = db.table('portfolio_positions').delete().eq('user_id', user_id).execute()

print(f"✅ Deleted {len(result.data) if result.data else 0} positions")

# Verify
verify_result = db.table('portfolio_positions').select('*').eq('user_id', user_id).execute()
remaining = len(verify_result.data) if verify_result.data else 0

if remaining == 0:
    print("✅ Portfolio cleaned successfully!")
else:
    print(f"⚠️  Warning: {remaining} positions still remain")
