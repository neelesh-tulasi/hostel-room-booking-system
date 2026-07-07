from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


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

        conn = sqlite3.connect("hostel.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students
        (name, rollno, department, year, gender, email, phone, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, rollno, department, year, gender, email, phone, password))

        conn.commit()
        conn.close()

        return "<h2>Registration Successful!</h2><a href='/'>Go to Home</a>"

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)