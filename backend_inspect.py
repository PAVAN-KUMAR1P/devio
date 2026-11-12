import sqlite3
conn = sqlite3.connect(r'c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el\InfraSense_Production.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name")
rows = cur.fetchall()
for r in rows:
    print(r['type'], r['name'])
print("---district_master columns---")
cur.execute("PRAGMA table_info(district_master)")
for r in cur.fetchall():
    print(dict(r))
print("---indicator_master columns---")
cur.execute("PRAGMA table_info(indicator_master)")
for r in cur.fetchall():
    print(dict(r))
print("---normalized_indicators columns---")
cur.execute("PRAGMA table_info(normalized_indicators)")
for r in cur.fetchall():
    print(dict(r))
print("---district_scores columns---")
cur.execute("PRAGMA table_info(district_scores)")
for r in cur.fetchall():
    print(dict(r))
print("---district_clusters columns---")
cur.execute("PRAGMA table_info(district_clusters)")
for r in cur.fetchall():
    print(dict(r))
print("---district_recommendations columns---")
try:
    cur.execute("PRAGMA table_info(district_recommendations)")
    for r in cur.fetchall():
        print(dict(r))
except Exception as e:
    print("Error:", e)
print("---district_rankings view sample---")
try:
    cur.execute("SELECT * FROM district_rankings LIMIT 2")
    for r in cur.fetchall():
        print(dict(r))
except Exception as e:
    print("Error:", e)
print("---cluster_summary view sample---")
try:
    cur.execute("SELECT * FROM cluster_summary LIMIT 3")
    for r in cur.fetchall():
        print(dict(r))
except Exception as e:
    print("Error:", e)
print("---analysis_runs---")
cur.execute("SELECT * FROM analysis_runs LIMIT 5")
for r in cur.fetchall():
    print(dict(r))
conn.close()
