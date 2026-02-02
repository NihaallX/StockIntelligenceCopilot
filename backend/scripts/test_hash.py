import sys
import os
sys.path.append(os.getcwd())
try:
    from app.core.auth.password import hash_password
    import hashlib

    password = "Password123!"
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(f"Password: {password}")
    print(f"Prehashed (SHA256 hex): {prehashed}")
    print(f"Prehashed length: {len(prehashed)}")

    print("Attempting to hash...")
    hashed = hash_password(password)
    print(f"Success! Hash: {hashed}")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
