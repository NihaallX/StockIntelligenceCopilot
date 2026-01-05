import sys
sys.path.insert(0, 'D:/Stock Intelligence Copilot/backend')

from app.main import app

print('✓ App imports successfully')
print('✓ API routes:')
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = ', '.join(route.methods)
        print(f'  [{methods}] {route.path}')
