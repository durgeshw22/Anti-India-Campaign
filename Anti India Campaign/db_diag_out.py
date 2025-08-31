"""
Diagnostic script: writes DB debug info to diag_out.json so the assistant can read it reliably.
Run with the project's venv Python.
"""
import json
from database import debug_db_status
out = debug_db_status()
with open('diag_out.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print('WROTE diag_out.json')
