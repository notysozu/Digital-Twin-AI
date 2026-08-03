from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) as count FROM financial_records WHERE user_id = 1;")
print("Financial records for user 1:", cur.fetchone()["count"])

cur.execute("SELECT COUNT(*) as count FROM study_activities WHERE user_id = 1;")
print("Study records for user 1:", cur.fetchone()["count"])

cur.execute("SELECT user_id FROM users LIMIT 5;")
print("Existing user_ids:", [r["user_id"] for r in cur.fetchall()])

cur.close()
conn.close()