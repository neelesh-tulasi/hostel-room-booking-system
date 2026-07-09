import sqlite3

conn = sqlite3.connect("hostel_production.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE admins
ADD COLUMN reset_request INTEGER DEFAULT 0
""")

conn.commit()
conn.close()

print("Column added successfully")