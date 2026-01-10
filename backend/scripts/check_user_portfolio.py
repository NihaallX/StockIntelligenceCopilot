"""Check portfolio for specific user"""
import sys
sys.path.insert(0, 'D:/Stock Intelligence Copilot/backend')

from app.core.database import get_service_db

db = get_service_db()

# Look for user with email
email = "nihalpardeshi12344@gmail.com"
print(f"🔍 Searching for user: {email}")

users_result = db.table('users').select('id,email,full_name,created_at').eq('email', email).execute()

if not users_result.data:
    print(f"❌ User not found: {email}")
    print("\nAll users in database:")
    all_users = db.table('users').select('email').execute()
    for u in (all_users.data or [])[:10]:
        print(f"  - {u['email']}")
    sys.exit(1)

user = users_result.data[0]
print(f"✅ Found user!")
print(f"   Email: {user['email']}")
print(f"   Name: {user.get('full_name', 'N/A')}")
print(f"   ID: {user['id']}")
print(f"   Created: {user.get('created_at', 'N/A')}")

# Get portfolio positions
print(f"\n📊 Portfolio Positions:")
portfolio_result = db.table('portfolio_positions').select('*').eq('user_id', user['id']).execute()

if not portfolio_result.data:
    print("   ❌ No positions found (empty portfolio)")
else:
    print(f"   Found {len(portfolio_result.data)} positions:")
    print()
    total_value = 0
    for pos in portfolio_result.data:
        cost = float(pos.get('cost_basis', 0))
        total_value += cost
        print(f"   • {pos['ticker']}")
        print(f"     Quantity: {pos['quantity']}")
        print(f"     Entry: ₹{pos.get('entry_price', 'N/A')}")
        print(f"     Cost Basis: ₹{cost:,.2f}")
        print(f"     Date: {pos.get('entry_date', 'N/A')[:10]}")
        print()
    
    print(f"   💰 Total Portfolio Value: ₹{total_value:,.2f}")

print("\n" + "="*50)
print("✅ Query complete!")
