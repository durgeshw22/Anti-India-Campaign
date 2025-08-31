import sqlite3
from enhanced_keyword_database import KeywordDatabase

kb = KeywordDatabase()
conn = sqlite3.connect(kb.db_path)
cur = conn.cursor()
keywords = [
    ("कश्मीर", "kashmir_term", 2.5),
    ("कश्मीर आज़ादी", "separatist", 2.3),
    ("कश्मीर स्वतंत्रता", "separatist", 2.3)
]
for kw, cat, w in keywords:
    cur.execute('INSERT OR IGNORE INTO keywords (keyword, category, weight) VALUES (?, ?, ?)', (kw, cat, w))
conn.commit()
# return rows inserted
cur.execute("SELECT keyword, category, weight FROM keywords WHERE keyword LIKE '%कश्मीर%'")
rows = cur.fetchall()
conn.close()
import json
with open('kw_added_out.json','w',encoding='utf-8') as f:
    json.dump(rows,f,ensure_ascii=False,indent=2)
print('wrote kw_added_out.json')
