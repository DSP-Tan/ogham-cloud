import sys
import psycopg2

term = sys.argv[1]
conn = psycopg2.connect(dbname="english_exams")
cur = conn.cursor()
cur.execute("""
    SELECT "text"
    FROM english_hl
    WHERE to_tsvector('english', "text") @@ plainto_tsquery('english', %s);
""", (term,))
for row in cur:
    print(row[0])
cur.close()
conn.close()
