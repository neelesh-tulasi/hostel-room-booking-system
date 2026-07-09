import sqlite3

conn = sqlite3.connect("hostel.db")
cursor = conn.cursor()


# --------------------------------
# Students Table
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (

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


# --------------------------------
# Hostels Table
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS hostels (

hostel_id INTEGER PRIMARY KEY AUTOINCREMENT,

hostel_name TEXT UNIQUE NOT NULL,

gender TEXT NOT NULL

)
""")


# --------------------------------
# Rooms Table
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (

room_id INTEGER PRIMARY KEY AUTOINCREMENT,

hostel_id INTEGER NOT NULL,

room_number TEXT NOT NULL,

capacity INTEGER NOT NULL,

occupied INTEGER DEFAULT 0,


FOREIGN KEY(hostel_id) REFERENCES hostels(hostel_id)

)
""")


# --------------------------------
# Allocations Table
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS allocations (

allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,

rollno TEXT UNIQUE NOT NULL,

hostel_id INTEGER NOT NULL,

room_number TEXT NOT NULL,


FOREIGN KEY(rollno) REFERENCES students(rollno),

FOREIGN KEY(hostel_id) REFERENCES hostels(hostel_id)

)
""")


# --------------------------------
# Insert Hostels
# --------------------------------

cursor.execute("""
INSERT OR IGNORE INTO hostels
(hostel_name, gender)

VALUES
('Boys Hostel','Male')
""")


cursor.execute("""
INSERT OR IGNORE INTO hostels
(hostel_name, gender)

VALUES
('Girls Hostel','Female')
""")


# --------------------------------
# Insert Rooms
# --------------------------------

cursor.execute("""
INSERT OR IGNORE INTO rooms
(hostel_id, room_number, capacity, occupied)

VALUES
(1,'101',3,0)
""")


cursor.execute("""
INSERT OR IGNORE INTO rooms
(hostel_id, room_number, capacity, occupied)

VALUES
(1,'102',3,3)
""")


cursor.execute("""
INSERT OR IGNORE INTO rooms
(hostel_id, room_number, capacity, occupied)

VALUES
(1,'103',2,1)
""")


cursor.execute("""
INSERT OR IGNORE INTO rooms
(hostel_id, room_number, capacity, occupied)

VALUES
(2,'201',3,0)
""")


# Save changes

conn.commit()

conn.close()


print("Database created successfully!")