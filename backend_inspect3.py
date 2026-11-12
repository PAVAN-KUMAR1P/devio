import sqlite3
conn = sqlite3.connect(r'c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el\InfraSense_Production.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("---normalized_indicators district IDs---")
cur.execute("SELECT DISTINCT district_id FROM normalized_indicators LIMIT 5")
for r in cur.fetchall():
    print(dict(r))

print("---normalized_indicators for KA-001---")
cur.execute("SELECT * FROM normalized_indicators WHERE district_id='KA-001' LIMIT 5")
for r in cur.fetchall():
    print(dict(r))

print("---district_scores overall---")
cur.execute("SELECT * FROM district_scores WHERE score_type='overall' LIMIT 3")
for r in cur.fetchall():
    print(dict(r))

# Check if district_rankings has district_id
print("---district_rankings CREATE---")
cur.execute("SELECT sql FROM sqlite_master WHERE name='district_rankings'")
r = cur.fetchone()
if r:
    print(r['sql'])

# Check dimension_rankings for district_id
print("---dimension_rankings CREATE---")
cur.execute("SELECT sql FROM sqlite_master WHERE name='dimension_rankings'")
r = cur.fetchone()
if r:
    print(r['sql'])

print("---cluster_summary CREATE---")
cur.execute("SELECT sql FROM sqlite_master WHERE name='cluster_summary'")
r = cur.fetchone()
if r:
    print(r['sql'])

conn.close()
