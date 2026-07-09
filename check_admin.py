import sqlite3

conn = sqlite3.connect("hostel_production.db")
cursor = conn.cursor()

cursor.execute("""
SELECT username, hashed_password
FROM admins
""")

admins = cursor.fetchall()

for admin in admins:
    print(admin)

conn.close()