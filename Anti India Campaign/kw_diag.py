import json, sqlite3
from enhanced_keyword_database import KeywordDatabase
kb = KeywordDatabase()
conn = sqlite3.connect(kb.db_path)
cur = conn.cursor()
cur.execute("SELECT keyword, category, weight FROM keywords WHERE keyword LIKE '%कश्मीर%' LIMIT 50")
rows = cur.fetchall()
conn.close()
with open('kw_diag_out.json','w',encoding='utf-8') as f:
    json.dump(rows,f,ensure_ascii=False,indent=2)
print('wrote kw_diag_out.json')
