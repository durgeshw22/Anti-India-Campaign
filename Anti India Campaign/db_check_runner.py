"""
Diagnostic runner to verify the SQLite DB used by the project and show sample rows.
Run this from the project root using the project's venv Python.
"""
import os, json, sqlite3, sys
from database import debug_db_status, DATABASE_PATH
import pandas as pd

print('PYTHON:', sys.executable)
print('CWD:', os.getcwd())
print('DB_PATH (from database.py):', DATABASE_PATH)
print('debug_db_status():')
print(json.dumps(debug_db_status(), indent=2))

# Check file existence by absolute path and by searching cwd
print('\nFile exists at path?:', os.path.exists(DATABASE_PATH))
search_paths = []
for root, dirs, files in os.walk(os.getcwd()):
    for f in files:
        if f == 'campaign_data.db':
            search_paths.append(os.path.join(root, f))
print('Found campaign_data.db files under project:')
print(json.dumps(search_paths, indent=2))

# Try to read recent articles using pandas
try:
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query('SELECT id,title,source,collected_date,sentiment_score FROM articles ORDER BY collected_date DESC LIMIT 10', conn)
    conn.close()
    print('\nRecent articles (up to 10):')
    print(df.fillna('').to_string(index=False))
except Exception as e:
    print('\nFailed to read articles:', e)

print('\nDone.')
