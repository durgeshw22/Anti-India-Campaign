import ast
import sys

path = r"d:\worked\sentii\enhanced_dashboard.py"
try:
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    ast.parse(s, path)
    print("OK: parsed successfully")
except Exception as e:
    print("ERROR:", repr(e))
    sys.exit(1)
