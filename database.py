import sqlite3

conn = sqlite3.connect("hostel.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    rollno TEXT,
    department TEXT,
    year TEXT,
    gender TEXT,
    email TEXT,
    phone TEXT,
    password TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")