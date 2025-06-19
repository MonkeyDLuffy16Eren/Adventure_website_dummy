from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'contact.db')

# --- Initialize all tables ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Contact form
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    # Destination form
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destinations TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            persons INTEGER NOT NULL
        )
    ''')

    # User login table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# -------------------packages---------------
@app.route('/packages')
def packages():
    # Connect to the adventure_packages.db
    conn = sqlite3.connect('adventure_packages.db')
    conn.row_factory = sqlite3.Row  # ✅ ADD THIS LINE
    c = conn.cursor()
    c.execute("SELECT * FROM packages")
    packages = c.fetchall()
    conn.close()

    return render_template('packages.html', packages=packages)




# ---------- CONTACT FORM ----------

@app.route('/submit', methods=['POST'])
def submit():
    print("Form submitted!") 
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return "<h3>Please fill all fields.</h3><a href='/contact'>Go Back</a>"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

    return f"<h3>Thank you, {name}! Your message has been saved.</h3><a href='/'>Go Back</a>"

# ---------- DESTINATIONS ----------

@app.route('/destination', methods=['GET', 'POST'])
def destination():
    if request.method == 'POST':
        destinations = ', '.join(request.form.getlist('destinations'))
        travel_date = request.form['travel_date']
        persons = request.form['persons']

        if not destinations or not travel_date or not persons:
            return "<h3>Please fill all fields.</h3><a href='/destination'>Go Back</a>"

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO bookings (destinations, travel_date, persons) VALUES (?, ?, ?)",
                  (destinations, travel_date, persons))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    conn.close()

    return render_template('destination.html', bookings=bookings)

# ---------- USER LOGIN ----------

@app.route('/login')
def login():
    return render_template('userlogin.html')  # login page template

@app.route('/do_login', methods=['POST'])
def do_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return "<h3>All fields are required.</h3><a href='/login'>Go Back</a>"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        return f"<h3>Welcome back, {email}!</h3><a href='/'>Go Home</a>"
    else:
        return "<h3>Invalid credentials.</h3><a href='/login'>Try Again</a>"

# Run
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
