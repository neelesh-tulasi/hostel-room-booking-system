import sqlite3

conn = sqlite3.connect("hostel_production.db")
cursor = conn.cursor()

tables = [
    "students",
    "admins",
    "hostels",
    "rooms",
    "allocations"
]

for table in tables:

    print(f"\n===== {table.upper()} =====")

    cursor.execute(f"PRAGMA table_info({table})")

    columns = cursor.fetchall()

    if columns:
        for column in columns:
            print(column)
    else:
        print("Table not found!")

conn.close()