import sqlite3

conn = sqlite3.connect("hostel_production.db")
cursor = conn.cursor()

print("===== HOSTELS =====")
cursor.execute("SELECT hostel_id, hostel_name, gender FROM hostels")
for row in cursor.fetchall():
    print(row)

conn.close()