import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing app.main...")
    import app.main
    print("Success!")
except Exception as e:
    import traceback
    with open("debug_traceback.log", "w") as f:
        traceback.print_exc(file=f)
    print("Traceback written to debug_traceback.log")
