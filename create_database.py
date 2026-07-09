import sqlite3

# Create a new database
conn = sqlite3.connect("hostel_production.db")
cursor = conn.cursor()

# ---------------- Students ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    rollno TEXT UNIQUE NOT NULL,

    department TEXT NOT NULL,

    year TEXT NOT NULL,

    gender TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    phone TEXT NOT NULL,

    hashed_password TEXT NOT NULL
)
""")

# ---------------- Hostels ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS hostels(

    hostel_id INTEGER PRIMARY KEY AUTOINCREMENT,

    hostel_name TEXT UNIQUE NOT NULL,

    gender TEXT NOT NULL
)
""")

# ---------------- Rooms ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms(

    room_id INTEGER PRIMARY KEY AUTOINCREMENT,

    hostel_id INTEGER NOT NULL,

    room_number TEXT NOT NULL,

    capacity INTEGER NOT NULL,

    occupied INTEGER DEFAULT 0,

    FOREIGN KEY(hostel_id)
        REFERENCES hostels(hostel_id)
)
""")

# ---------------- Allocations ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS allocations(

    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    rollno TEXT NOT NULL,

    hostel_id INTEGER NOT NULL,

    room_number TEXT NOT NULL,

    FOREIGN KEY(rollno)
        REFERENCES students(rollno),

    FOREIGN KEY(hostel_id)
        REFERENCES hostels(hostel_id)
)
""")

conn.commit()
conn.close()

print("✅ hostel_production.db created successfully!")