import sqlite3

conn = sqlite3.connect("hostel.db")
cursor = conn.cursor()

tables = ["students", "hostels", "rooms", "allocations"]

for table in tables:
    print(f"\n===== {table.upper()} =====")

    cursor.execute(f"PRAGMA table_info({table})")

    columns = cursor.fetchall()

    for column in columns:
        print(column)

conn.close()