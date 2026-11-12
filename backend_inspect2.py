import sqlite3
conn = sqlite3.connect(r'c:\Users\Pavan Kumar P\OneDrive\Desktop\5TH SEM\el\InfraSense_Production.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("---district_rankings full cols---")
cur.execute("SELECT * FROM district_rankings LIMIT 1")
r = cur.fetchone()
if r:
    print(list(r.keys()))
    print(dict(r))

print("---dimension_rankings sample---")
cur.execute("SELECT * FROM dimension_rankings LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("---indicator_descriptive_stats sample---")
cur.execute("SELECT * FROM indicator_descriptive_stats LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("---indicator_regional_disparity sample---")
cur.execute("SELECT * FROM indicator_regional_disparity LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("---indicator_outliers sample---")
cur.execute("SELECT * FROM indicator_outliers LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("---development_unevenness sample---")
cur.execute("SELECT * FROM development_unevenness LIMIT 2")
for r in cur.fetchall():
    print(dict(r))

print("---district_master sample---")
cur.execute("SELECT * FROM district_master LIMIT 3")
for r in cur.fetchall():
    print(dict(r))

print("---district_scores sample---")
cur.execute("SELECT * FROM district_scores LIMIT 5")
for r in cur.fetchall():
    print(dict(r))

print("---normalized_indicators for one district---")
cur.execute("SELECT * FROM normalized_indicators WHERE district_id='KA-01' LIMIT 5")
for r in cur.fetchall():
    print(dict(r))

print("---district_clusters sample---")
cur.execute("SELECT * FROM district_clusters LIMIT 3")
for r in cur.fetchall():
    print(dict(r))

conn.close()
