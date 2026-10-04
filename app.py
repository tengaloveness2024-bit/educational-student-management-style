from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for secure sessions
app.secret_key = "change-this-secret-key"

DATABASE = "database.db"


# ---------------- DATABASE ----------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Students table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            program TEXT NOT NULL,
            marks REAL NOT NULL
        )
    """)

    # Create default administrator
    user = connection.execute(
        "SELECT id FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if user is None:
        connection.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123"))
        )

    connection.commit()
    connection.close()


# ---------------- LOGIN SECURITY ----------------

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)

    return decorated_function


# ---------------- LOGIN ----------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Simple login
        if username == "admin" and password == "admin123":
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.")
            return render_template("login.html")

        connection = get_db()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    search = request.args.get("q", "").strip()

    connection = get_db()

    if search:

        students = connection.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ?
               OR full_name LIKE ?
               OR program LIKE ?
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()

    else:

        students = connection.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        students=students,
        search=search
    )


# ---------------- VALIDATION ----------------

def validate_student_form(form):

    student_id = form.get("student_id", "").strip()
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip()
    program = form.get("program", "").strip()
    marks_text = form.get("marks", "").strip()

    if not student_id or not full_name or not email or not program or not marks_text:
        return None, "All fields are required."

    if "@" not in email:
        return None, "Please enter a valid email address."

    try:
        marks = float(marks_text)
    except ValueError:
        return None, "Marks must be a number."

    if marks < 0 or marks > 100:
        return None, "Marks must be between 0 and 100."

    student = {
        "student_id": student_id,
        "full_name": full_name,
        "email": email,
        "program": program,
        "marks": marks
    }

    return student, None


# ---------------- ADD STUDENT ----------------

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        student, error = validate_student_form(request.form)

        if error:
            flash(error)
            return render_template(
                "student_form.html",
                student=request.form,
                action="Add"
            )

        connection = get_db()

        try:

            connection.execute("""
                INSERT INTO students
                (student_id, full_name, email, program, marks)
                VALUES (?, ?, ?, ?, ?)
            """, (
                student["student_id"],
                student["full_name"],
                student["email"],
                student["program"],
                student["marks"]
            ))

            connection.commit()

            flash("Student added successfully.")

            return redirect(url_for("dashboard"))

        except sqlite3.IntegrityError:

            flash("Student ID already exists.")

        finally:

            connection.close()

    return render_template(
        "student_form.html",
        student={},
        action="Add"
    )


# ---------------- EDIT STUDENT ----------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    connection = get_db()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if student is None:

        connection.close()

        return "Student not found", 404

    if request.method == "POST":

        updated_student, error = validate_student_form(request.form)

        if error:

            connection.close()

            flash(error)

            return render_template(
                "student_form.html",
                student=request.form,
                action="Edit"
            )

        try:

            connection.execute("""
                UPDATE students
                SET student_id = ?,
                    full_name = ?,
                    email = ?,
                    program = ?,
                    marks = ?
                WHERE id = ?
            """, (
                updated_student["student_id"],
                updated_student["full_name"],
                updated_student["email"],
                updated_student["program"],
                updated_student["marks"],
                id
            ))

            connection.commit()

            flash("Student updated successfully.")

            return redirect(url_for("dashboard"))

        except sqlite3.IntegrityError:

            flash("Student ID already exists.")

        finally:

            connection.close()

    else:

        connection.close()

    return render_template(
        "student_form.html",
        student=student,
        action="Edit"
    )


# ---------------- DELETE STUDENT ----------------

@app.post("/delete/<int:id>")
@login_required
def delete_student(id):

    connection = get_db()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    flash("Student deleted successfully.")

    return redirect(url_for("dashboard"))


# ---------------- START APPLICATION ----------------

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,
    debug=False)
