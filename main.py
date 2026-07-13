import sqlite3
import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_here_change_in_production")
app.config["UPLOAD_FOLDER"] = "static/uploads"

# ========== DATABASE INITIALIZATION ==========
def init_db():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    
    # Create properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            price REAL,
            location TEXT,
            area TEXT,
            property_type TEXT,
            image TEXT,
            status TEXT
        )
    ''')
    
    # Check if admin exists, if not create default admin
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )
        print("✅ Default admin created: admin/admin123")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# ========== HOME ==========
@app.route("/")
def home():
    return render_template("login.html")

# ========== LOGIN ==========
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("prop.db")
        cursor = conn.cursor()
        
        # Remove debug print statement
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["user"] = username
            session["role"] = user[3]  # role is at index 3
            if user[3] == "admin":
                return redirect("/admin")
            else:
                return redirect("/index")
        else:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )
    
    return render_template("login.html")

# ========== ADMIN DASHBOARD ==========
@app.route("/admin")
def admin():
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    
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
    conn.close()
    
    return render_template(
        "admin.html",
        properties=properties,
        total_properties=total_properties,
        total_users=total_users,
        available=available,
        sold=sold
    )

# ========== ADD PROPERTY ==========
@app.route("/property", methods=["GET", "POST"])
def add_property():
    # Check if user is logged in
    if "user" not in session:
        return redirect("/login")
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    
    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        price = request.form["price"]
        area = request.form["area"]
        property_type = request.form["property_type"]
        description = request.form["description"]
        
        # Handle image upload
        if "image" in request.files and request.files["image"].filename:
            image = request.files["image"]
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = "default.jpg"  # Default image if none uploaded
        
        cursor.execute("""
            INSERT INTO properties
            (title, description, price, location, area, property_type, image, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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

# ========== VIEW PROPERTIES ==========
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

# ========== ABOUT ==========
@app.route("/about")
def about():
    return render_template("about.html")

# ========== CONTACT ==========
@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")

# ========== LOGOUT ==========
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ========== REGISTER ==========
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
        
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()   
        conn.close()
        return redirect("/login")
    
    return render_template("register.html")

# ========== DELETE PROPERTY ==========
@app.route("/delete/<int:id>")
def delete(id):
    # Check if user is logged in as admin
    if "user" not in session or session.get("role") != "admin":
        return redirect("/login")
    
    conn = sqlite3.connect("prop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM properties WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ========== INDEX ==========
@app.route("/index")
def index():
    return render_template("index.html")

# Initialize database whenever the app starts
init_db()

# ========== RUN THE APP ==========
if __name__ == "__main__":
    # Get port from environment (Railway provides this)
    port = int(os.environ.get("PORT", 5000))

    # Run the app
    app.run(host="0.0.0.0", port=port, debug=False)
