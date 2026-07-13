import sqlite3
import os
print(os.getcwd())
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "static/uploads"
@app.route("/")
def home():
    return render_template("login.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("prop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        print(cursor.fetchall())
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            role = user[3]
            if role == "admin":
                return redirect("/admin")
            elif role == "user":
                return redirect("/index")
        else:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )
    return render_template("login.html")
@app.route("/admin")
def admin():
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties")
    properties = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM properties")
    total_properties = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM properties WHERE status='Available'")
    available = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM properties WHERE status='Sold'")
    sold = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM bookings1")
    bookings = cursor.fetchall()
    conn.close()
    return render_template(
        "admin.html",
        properties=properties,
        total_properties=total_properties,
        total_users=total_users,
        available=available,
        sold=sold,bookings=bookings
    )
@app.route("/property", methods=["GET", "POST"])
def add_property():
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        price = request.form["price"]
        area = request.form["area"]
        property_type = request.form["property_type"]
        description = request.form["description"]
        image = request.files["image"]
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        cursor.execute("""
            INSERT INTO properties
            (title,description,price,location,area,property_type,image,status)
            VALUES(?,?,?,?,?,?,?,?)
        """,
        (
            title,
            description,
            price,
            location,
            area,
            property_type,
            filename,
            "Available"
        ))
        conn.commit()
    cursor.execute("SELECT * FROM properties")
    properties = cursor.fetchall()
    conn.close()
    return render_template(
        "property.html",
        properties=properties
    )
@app.route("/properties")
def properties():
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE status='Available'")
    properties = cursor.fetchall()
    conn.close()
    return render_template(
        "properties.html",
        properties=properties
    )
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        conn = sqlite3.connect("prop.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()
        if user:
            conn.close()
            return render_template(
                "register.html",
                error="Username already exists"
            )
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",(username, password, role))
        conn.commit()   
        conn.close()
        return redirect("/login")
    return render_template("register.html")
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")
@app.route("/index")
def index():
    return render_template("index.html")
@app.route("/confirm_booking", methods=["POST"])
def confirm_booking():

    property_id = request.form["property_id"]
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]

    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title,location,price,property_type,image
        FROM properties
        WHERE id=?
    """, (property_id,))

    p = cursor.fetchone()

    cursor.execute("""
        INSERT INTO bookings1(
            property_id,
            customer_name,
            customer_email,
            customer_phone,
            customer_address,
            title,
            location,
            price,
            property_type,
            image
        )
        VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
        property_id,
        name,
        email,
        phone,
        address,
        p[0],
        p[1],
        p[2],
        p[3],
        p[4]
    ))

    conn.commit()
    conn.close()

    return redirect("/properties")
@app.route("/book/<int:id>")
def book(id):

    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM properties WHERE id=?", (id,))
    property = cursor.fetchone()

    conn.close()

    return render_template("booking.html", property=property)
@app.route("/book", methods=["GET","POST"])
def book_property():
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    property = cursor.fetchone()
    if property:
        cursor.execute("""
            INSERT INTO bookings1
            (property_id,title,location,price,property_type,image)
            VALUES(?,?,?,?,?,?)
        """,
        (
            property[0],
            property[1],
            property[3],
            property[2],
            property[4],
            property[5]
        ))

        conn.commit()

    conn.close()

    return render_template("booking.html")
if __name__ == "__main__":
    app.run(debug=True)