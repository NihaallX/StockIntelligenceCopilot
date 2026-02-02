try:
    with open("debug_auth.log", "rb") as f:
        try:
            f.seek(-5000, 2)
        except:
            pass
        content = f.read()
        try:
            print(content.decode("utf-16"))
        except:
            print(content.decode("utf-8", errors="ignore"))
except Exception as e:
    print(f"Error: {e}")
