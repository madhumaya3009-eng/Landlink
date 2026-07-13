import sqlite3
conn = sqlite3.connect("prop.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
conn = sqlite3.connect("prop.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE if not exists bookings1(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    customer_address TEXT,
    title TEXT,
    location TEXT,
    price TEXT,
    property_type TEXT,
    image TEXT,
    status TEXT DEFAULT 'Pending'
);""")
conn = sqlite3.connect("prop.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS properties(
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
""")
conn = sqlite3.connect("prop.db")
cursor = conn.cursor()
cursor.execute("""INSERT INTO users (id,username,password,role)
VALUES ('1', 'admin', 'admin123', 'admin')""")
conn.commit()
conn.close()
print("Users table created successfully.")