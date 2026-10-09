from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# -----------------------------------
# Create Database
# -----------------------------------

def create_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            register_number TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            semester TEXT NOT NULL,
            gender TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------------
# Home Page
# -----------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------------
# Register Student
# -----------------------------------

@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    register_number = request.form["register_number"]
    email = request.form["email"]
    phone = request.form["phone"]
    course = request.form["course"]
    semester = request.form["semester"]
    gender = request.form["gender"]
    address = request.form["address"]

    try:

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (
                name,
                register_number,
                email,
                phone,
                course,
                semester,
                gender,
                address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            register_number,
            email,
            phone,
            course,
            semester,
            gender,
            address
        ))

        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            name=name
        )

    except sqlite3.IntegrityError:

        return """
        <h2>Registration Failed</h2>
        <p>This register number is already registered.</p>
        <a href="/">Go back to Registration</a>
        """


# -----------------------------------
# View / Search Students
# -----------------------------------

@app.route("/students")
def students():

    search = request.args.get("search", "")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT *
            FROM students
            WHERE name LIKE ?
               OR register_number LIKE ?
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM students
            ORDER BY id DESC
        """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students,
        search=search
    )


# -----------------------------------
# Edit Student
# -----------------------------------

@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        register_number = request.form["register_number"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        semester = request.form["semester"]
        gender = request.form["gender"]
        address = request.form["address"]

        try:

            cursor.execute("""
                UPDATE students
                SET
                    name = ?,
                    register_number = ?,
                    email = ?,
                    phone = ?,
                    course = ?,
                    semester = ?,
                    gender = ?,
                    address = ?
                WHERE id = ?
            """, (
                name,
                register_number,
                email,
                phone,
                course,
                semester,
                gender,
                address,
                student_id
            ))

            conn.commit()
            conn.close()

            return redirect("/students")

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <h2>Update Failed</h2>
            <p>This register number is already used by another student.</p>
            <a href="/students">Go back</a>
            """

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:

        return """
        <h2>Student Not Found</h2>
        <a href="/students">Back to Students</a>
        """

    return render_template(
        "edit.html",
        student=student
    )


# -----------------------------------
# Delete Student
# -----------------------------------

@app.route("/delete/<int:student_id>")
def delete_student(student_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/students")


# -----------------------------------
# Start Application
# -----------------------------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)