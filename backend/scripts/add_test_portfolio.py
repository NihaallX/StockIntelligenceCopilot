"""Add test portfolio positions for user"""
import sys
sys.path.insert(0, 'D:/Stock Intelligence Copilot/backend')

from app.core.database import get_service_db
from datetime import datetime

db = get_service_db()

# Check for users
print("Checking for users...")
users_result = db.table('users').select('id,email').execute()

if not users_result.data:
    print("❌ No users found. Please register first at /api/v1/auth/register")
    sys.exit(1)

user = users_result.data[0]
user_id = user['id']
print(f"✅ Found user: {user['email']} (ID: {user_id[:8]}...)")

# Check existing portfolio
print("\nChecking existing portfolio...")
portfolio_result = db.table('portfolio_positions').select('*').eq('user_id', user_id).execute()
print(f"Current positions: {len(portfolio_result.data) if portfolio_result.data else 0}")

# Test positions to add
test_positions = [
    {"ticker": "RELIANCE.NS", "quantity": 10, "entry_price": 2800.50},
    {"ticker": "TCS.NS", "quantity": 5, "entry_price": 4100.00},
    {"ticker": "INFY.NS", "quantity": 15, "entry_price": 1650.75},
    {"ticker": "HDFCBANK.NS", "quantity": 8, "entry_price": 1750.25},
    {"ticker": "ICICIBANK.NS", "quantity": 12, "entry_price": 1050.00},
    {"ticker": "SBIN.NS", "quantity": 20, "entry_price": 650.50},
    {"ticker": "ITC.NS", "quantity": 25, "entry_price": 450.00},
]

print(f"\n📊 Adding {len(test_positions)} test positions...")

for pos in test_positions:
    # Check if already exists
    existing = db.table('portfolio_positions').select('id').eq('user_id', user_id).eq('ticker', pos['ticker']).execute()
    
    if existing.data:
        print(f"  ⏭️  {pos['ticker']} - already exists, skipping")
        continue
    
    # Add position
    cost_basis = float(pos['quantity']) * float(pos['entry_price'])
    
    position_data = {
        'user_id': user_id,
        'ticker': pos['ticker'],
        'quantity': pos['quantity'],
        'entry_price': pos['entry_price'],
        'cost_basis': cost_basis,
        'entry_date': datetime.utcnow().isoformat()
    }
    
    result = db.table('portfolio_positions').insert(position_data).execute()
    
    if result.data:
        print(f"  ✅ {pos['ticker']} - {pos['quantity']} shares @ ₹{pos['entry_price']}")
    else:
        print(f"  ❌ {pos['ticker']} - failed to add")

# Show final portfolio
print("\n📈 Final portfolio:")
final_result = db.table('portfolio_positions').select('ticker,quantity,entry_price').eq('user_id', user_id).execute()
for p in (final_result.data or []):
    print(f"  • {p['ticker']}: {p['quantity']} shares @ ₹{p['entry_price']}")

print(f"\n✅ Done! Refresh Today's Watch to see your portfolio.")
