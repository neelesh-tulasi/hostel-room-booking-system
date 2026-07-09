import sqlite3
from werkzeug.security import generate_password_hash

# Create / Connect Database
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

# ---------------- Admins ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(

    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    username TEXT UNIQUE NOT NULL,

    email TEXT UNIQUE NOT NULL,

    hashed_password TEXT NOT NULL,

    role TEXT NOT NULL

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

# ---------------- Default Super Admin ----------------

cursor.execute("""
SELECT *
FROM admins
WHERE username=?
""", ("admin",))

admin = cursor.fetchone()

if admin is None:

    cursor.execute("""
    INSERT INTO admins
    (name, username, email, hashed_password, role)

    VALUES (?, ?, ?, ?, ?)
    """,
    (
        "Administrator",
        "admin",
        "admin@gmail.com",
        generate_password_hash("admin123"),
        "Super Admin"
    ))

conn.commit()
conn.close()

print("✅ hostel_production.db created successfully!")