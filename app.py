from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

app = Flask(__name__)
app.secret_key = "hostel_secret_key"


# ---------------- DATABASE ----------------
def get_connection():
    conn = sqlite3.connect("hostel_production.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- STUDENT REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        rollno = request.form["rollno"]
        department = request.form["department"]
        year = request.form["year"]
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
            INSERT INTO students
            (name, rollno, department, year, gender, email, phone, hashed_password)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                rollno,
                department,
                year,
                gender,
                email,
                phone,
                hashed_password
            ))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()
            return "Email or Roll Number already registered."

    return render_template("register.html")


# ---------------- STUDENT LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT
            name,
            rollno,
            department,
            year,
            gender,
            email,
            phone,
            hashed_password
        FROM students
        WHERE email=?
        """, (email,))

        student = cursor.fetchone()

        conn.close()

        if student and check_password_hash(student["hashed_password"], password):

            session["rollno"] = student["rollno"]
            session["student_name"] = student["name"]

            return redirect("/student_dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")
# ---------------- ADMIN LOGIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin_dashboard")

        return "Invalid Username or Password"

    return render_template("admin_login.html")

# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin"))


    conn = sqlite3.connect("hostel_production.db")
    cursor = conn.cursor()


    # Total Students

    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    """)

    total_students = cursor.fetchone()[0]



    # Total Hostels

    cursor.execute("""
    SELECT COUNT(*)
    FROM hostels
    """)

    total_hostels = cursor.fetchone()[0]



    # Total Rooms

    cursor.execute("""
    SELECT COUNT(*)
    FROM rooms
    """)

    total_rooms = cursor.fetchone()[0]



    # Total Bookings

    cursor.execute("""
    SELECT COUNT(*)
    FROM allocations
    """)

    total_bookings = cursor.fetchone()[0]



    # Available Rooms

    cursor.execute("""
    SELECT COUNT(*)
    FROM rooms
    WHERE occupied < capacity
    """)

    available_rooms = cursor.fetchone()[0]


    conn.close()


    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_hostels=total_hostels,
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        available_rooms=available_rooms
    )
# ---------------- ADD HOSTEL ----------------

@app.route("/add_hostel", methods=["GET", "POST"])
def add_hostel():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        hostel_name = request.form["hostel_name"]
        gender = request.form["gender"]

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
            INSERT INTO hostels(hostel_name, gender)
            VALUES(?, ?)
            """, (hostel_name, gender))

            conn.commit()

            conn.close()

            return redirect("/hostels")

        except sqlite3.IntegrityError:

            conn.close()

            return "Hostel already exists."

    return render_template("add_hostel.html")


# ---------------- VIEW HOSTELS ----------------

@app.route("/hostels")
def hostels():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT hostel_id,
           hostel_name,
           gender
    FROM hostels
    ORDER BY hostel_name
    """)

    hostels = cursor.fetchall()

    conn.close()

    return render_template("hostels.html", hostels=hostels)


# ---------------- EDIT HOSTEL ----------------

@app.route("/edit_hostel/<int:hostel_id>", methods=["GET", "POST"])
def edit_hostel(hostel_id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        hostel_name = request.form["hostel_name"]
        gender = request.form["gender"]

        cursor.execute("""
        UPDATE hostels
        SET hostel_name=?,
            gender=?
        WHERE hostel_id=?
        """, (hostel_name, gender, hostel_id))

        conn.commit()

        conn.close()

        return redirect("/hostels")

    cursor.execute("""
    SELECT *
    FROM hostels
    WHERE hostel_id=?
    """, (hostel_id,))

    hostel = cursor.fetchone()

    conn.close()

    return render_template("edit_hostel.html", hostel=hostel)


# ---------------- DELETE HOSTEL ----------------

@app.route("/delete_hostel/<int:hostel_id>")
def delete_hostel(hostel_id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    # Delete rooms of this hostel first
    cursor.execute("""
    DELETE FROM rooms
    WHERE hostel_id=?
    """, (hostel_id,))

    # Delete hostel
    cursor.execute("""
    DELETE FROM hostels
    WHERE hostel_id=?
    """, (hostel_id,))

    conn.commit()

    conn.close()

    return redirect("/hostels")
# ---------------- ADD ROOM ----------------

@app.route("/add_room", methods=["GET", "POST"])
def add_room():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        hostel_id = request.form["hostel_id"]
        room_number = request.form["room_number"]
        capacity = request.form["capacity"]

        try:

            cursor.execute("""
            INSERT INTO rooms
            (hostel_id, room_number, capacity, occupied)

            VALUES (?, ?, ?, 0)
            """, (hostel_id, room_number, capacity))

            conn.commit()

            conn.close()

            return redirect("/view_rooms")

        except sqlite3.IntegrityError:

            conn.close()

            return "Room already exists."

    cursor.execute("""
    SELECT hostel_id, hostel_name
    FROM hostels
    ORDER BY hostel_name
    """)

    hostels = cursor.fetchall()

    conn.close()

    return render_template("add_room.html", hostels=hostels)


# ---------------- VIEW ROOMS ----------------

@app.route("/view_rooms")
def view_rooms():

    conn = sqlite3.connect("hostel_production.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT
    rooms.room_id,
    hostels.hostel_name,
    rooms.room_number,
    rooms.capacity,
    rooms.occupied,
    rooms.capacity - rooms.occupied AS available
FROM rooms
JOIN hostels
ON rooms.hostel_id = hostels.hostel_id
""")

    rooms = cursor.fetchall()

    conn.close()

    return render_template("view_rooms.html", rooms=rooms)
# ---------------- EDIT ROOM ----------------

@app.route("/edit_room/<int:room_id>", methods=["GET", "POST"])
def edit_room(room_id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        room_number = request.form["room_number"]
        capacity = request.form["capacity"]

        cursor.execute("""
        UPDATE rooms

        SET room_number=?,
            capacity=?

        WHERE room_id=?
        """, (room_number, capacity, room_id))

        conn.commit()

        conn.close()

        return redirect("/view_rooms")

    cursor.execute("""
    SELECT *
    FROM rooms
    WHERE room_id=?
    """, (room_id,))

    room = cursor.fetchone()

    conn.close()

    return render_template("edit_room.html", room=room)


# ---------------- DELETE ROOM ----------------

@app.route("/delete_room/<int:room_id>")
def delete_room(room_id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM rooms
    WHERE room_id=?
    """, (room_id,))

    conn.commit()

    conn.close()

    return redirect("/view_rooms")
# ---------------- BOOK HOSTEL ----------------

@app.route("/book_hostel", methods=["GET", "POST"])
def book_hostel():

    if "rollno" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    # Get logged in student's gender
    cursor.execute("""
        SELECT gender
        FROM students
        WHERE rollno=?
    """, (session["rollno"],))

    student = cursor.fetchone()

    if student is None:
        conn.close()
        return "Student not found."

    student_gender = student["gender"].strip().lower()

    # Show matching hostels only
    cursor.execute("""
        SELECT hostel_id, hostel_name, gender
        FROM hostels
    """)

    all_hostels = cursor.fetchall()

    hostels = []

    for hostel in all_hostels:
        hostel_gender = hostel["gender"].strip().lower()

        if hostel_gender in ["male", "boys"] and student_gender == "male":
            hostels.append(hostel)

        elif hostel_gender in ["female", "girls"] and student_gender == "female":
            hostels.append(hostel)

    if request.method == "POST":

        hostel_id = request.form["hostel_id"]

        conn.close()

        return redirect(url_for("select_room", hostel_id=hostel_id))

    conn.close()

    return render_template("book_hostel.html", hostels=hostels)
@app.route("/rooms/<int:hostel_id>")
def select_room(hostel_id):

    if "rollno" not in session:
        return redirect("/login")

    session["hostel_id"] = hostel_id

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT room_id,
               room_number,
               capacity,
               occupied

        FROM rooms

        WHERE hostel_id=?

        AND occupied < capacity

        ORDER BY room_number
    """, (hostel_id,))

    rooms = cursor.fetchall()

    conn.close()

    return render_template("rooms.html", rooms=rooms)

@app.route("/book_room", methods=["POST"])
def book_room():

    if "rollno" not in session:
        return redirect("/login")

    rollno = session["rollno"]
    hostel_id = session["hostel_id"]

    room_id = request.form["room_id"]
    room_number = request.form["room_number"]

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent duplicate booking
    cursor.execute("""
        SELECT *
        FROM allocations
        WHERE rollno=?
    """, (rollno,))

    if cursor.fetchone():

        conn.close()

        return "You have already booked a room."

    # Check room availability
    cursor.execute("""
        SELECT capacity,
               occupied

        FROM rooms

        WHERE room_id=?
    """, (room_id,))

    room = cursor.fetchone()

    if room["occupied"] >= room["capacity"]:

        conn.close()

        return "Room is already full."

    # Update occupancy
    cursor.execute("""
        UPDATE rooms

        SET occupied = occupied + 1

        WHERE room_id=?
    """, (room_id,))

    # Save allocation
    cursor.execute("""
        INSERT INTO allocations
        (rollno, hostel_id, room_number)

        VALUES (?, ?, ?)
    """, (rollno, hostel_id, room_number))

    conn.commit()

    conn.close()

    return render_template(
        "booking_success.html",
        room_number=room_number
    )
# ---------------- STUDENT DASHBOARD ----------------

@app.route("/student_dashboard")
def student_dashboard():

    if "rollno" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        students.name,
        students.rollno,
        students.department,
        students.year,
        students.gender,
        students.email,
        students.phone,
        hostels.hostel_name,
        allocations.room_number

    FROM students

    LEFT JOIN allocations
        ON students.rollno = allocations.rollno

    LEFT JOIN hostels
        ON allocations.hostel_id = hostels.hostel_id

    WHERE students.rollno=?
    """, (session["rollno"],))

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        name=student["name"],
        rollno=student["rollno"],
        department=student["department"],
        year=student["year"],
        gender=student["gender"],
        email=student["email"],
        phone=student["phone"],
        hostel=student["hostel_name"] if student["hostel_name"] else "Not Allocated",
        room=student["room_number"] if student["room_number"] else "Not Allocated"
    )


# ---------------- VIEW BOOKINGS ----------------

@app.route("/view_bookings")
def view_bookings():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        students.name,
        students.rollno,
        hostels.hostel_name,
        allocations.room_number

    FROM allocations

    JOIN students
        ON allocations.rollno = students.rollno

    JOIN hostels
        ON allocations.hostel_id = hostels.hostel_id

    ORDER BY students.name
    """)

    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )


# ---------------- CANCEL BOOKING ----------------

@app.route("/cancel_booking/<rollno>")
def cancel_booking(rollno):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT room_number
    FROM allocations
    WHERE rollno=?
    """, (rollno,))

    booking = cursor.fetchone()

    if booking:

        room_number = booking["room_number"]

        cursor.execute("""
        UPDATE rooms

        SET occupied = occupied - 1

        WHERE room_number=?
        """, (room_number,))

        cursor.execute("""
        DELETE FROM allocations
        WHERE rollno=?
        """, (rollno,))

        conn.commit()

    conn.close()

    return redirect("/view_bookings")

# ---------------- STUDENT BOOKING HISTORY ----------------

@app.route("/booking_history")
def booking_history():

    if "rollno" not in session:
        return redirect(url_for("login"))


    conn = sqlite3.connect("hostel_production.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    cursor.execute("""
    SELECT
        hostels.hostel_name,
        allocations.room_number

    FROM allocations

    JOIN hostels
        ON allocations.hostel_id = hostels.hostel_id

    WHERE allocations.rollno=?

    """, (session["rollno"],))


    booking = cursor.fetchone()


    conn.close()


    return render_template(
        "booking_history.html",
        booking=booking
    )
# ---------------- EDIT STUDENT PROFILE ----------------

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "rollno" not in session:
        return redirect(url_for("login"))


    conn = sqlite3.connect("hostel_production.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        cursor.execute("""
UPDATE students
SET
    name=?,
    department=?,
    year=?,
    gender=?,
    phone=?,
    email=?
WHERE id=?
""", (
name,
department,
year,
gender,
    phone,
    email,
    id
))


        conn.commit()

        conn.close()


        return redirect(url_for("student_dashboard"))



    cursor.execute("""
    SELECT *
    FROM students
    WHERE rollno=?

    """,
    (session["rollno"],))


    student = cursor.fetchone()


    conn.close()


    return render_template(
        "edit_profile.html",
        student=student
    )
# ---------------- VIEW STUDENTS ----------------

# ---------------- VIEW / SEARCH STUDENTS ----------------

@app.route("/students")
def students():

    if "admin" not in session:
        return redirect(url_for("admin"))


    search = request.args.get("search")


    conn = sqlite3.connect("hostel_production.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    if search:

        cursor.execute("""
        SELECT *
        FROM students
        WHERE name LIKE ?
        OR rollno LIKE ?
        OR department LIKE ?

        """,
        (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))


    else:

        cursor.execute("""
        SELECT *
        FROM students
        """)


    students = cursor.fetchall()


    conn.close()


    return render_template(
        "students.html",
        students=students
    )
# ---------------- EDIT STUDENT ----------------

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "admin" not in session:
        return redirect(url_for("admin"))


    conn = sqlite3.connect("hostel_production.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        email = request.form["email"]


        cursor.execute("""
        UPDATE students

        SET name=?,
            department=?,
            year=?,
            gender=?,
            phone=?,
            email=?

        WHERE id=?

        """,
        (
            name,
            department,
            year,
            gender,
            phone,
            email,
            id
        ))


        conn.commit()
        conn.close()


        return redirect(url_for("students"))



    cursor.execute("""
    SELECT *
    FROM students
    WHERE id=?
    """,(id,))


    student = cursor.fetchone()


    conn.close()


    return render_template(
        "edit_student.html",
        student=student
    )
# ---------------- DELETE STUDENT ----------------

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "admin" not in session:
        return redirect(url_for("admin"))


    conn = sqlite3.connect("hostel_production.db")
    cursor = conn.cursor()


    # Delete booking first

    cursor.execute("""
    DELETE FROM allocations
    WHERE rollno =
    (
        SELECT rollno
        FROM students
        WHERE id=?
    )
    """,(id,))


    # Delete student

    cursor.execute("""
    DELETE FROM students
    WHERE id=?
    """,(id,))


    conn.commit()

    conn.close()


    return redirect(url_for("students"))

@app.route("/download_receipt")
def download_receipt():

    if "rollno" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        students.name,
        students.rollno,
        hostels.hostel_name,
        allocations.room_number
    FROM students
    JOIN allocations
        ON students.rollno = allocations.rollno
    JOIN hostels
        ON allocations.hostel_id = hostels.hostel_id
    WHERE students.rollno=?
    """, (session["rollno"],))

    data = cursor.fetchone()

    conn.close()

    if data is None:
        return "No hostel allocation found."

    pdf_file = "Hostel_Receipt.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>HOSTEL ALLOTMENT RECEIPT</b>", styles["Title"]))
    story.append(Paragraph(f"Student Name: {data['name']}", styles["Normal"]))
    story.append(Paragraph(f"Roll Number: {data['rollno']}", styles["Normal"]))
    story.append(Paragraph(f"Hostel: {data['hostel_name']}", styles["Normal"]))
    story.append(Paragraph(f"Room Number: {data['room_number']}", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)
# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- RUN APP ----------------
    print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True)
   