from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for
from flask_cors import CORS
import sqlite3
import hashlib
import random
import time
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'

DB = 'users.db'
LOCK_DURATION = 300  # 5 minutes

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            failed_attempts INTEGER DEFAULT 0,
            lock_time REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])
    role = data['role']

    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = hash_password(data['password'])

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, password, role, failed_attempts, lock_time FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if not user:
        conn.close()
        return jsonify({'message': 'Invalid username or password'}), 401

    user_id, db_password, role, failed_attempts, lock_time = user

    if lock_time and time.time() < lock_time:
        remaining = int(lock_time - time.time())
        conn.close()
        return jsonify({'message': f'Account locked. Try again in {remaining} seconds'}), 403

    if password != db_password:
        failed_attempts += 1
        if failed_attempts >= 3:
            lock_time = time.time() + LOCK_DURATION
            c.execute("UPDATE users SET failed_attempts=?, lock_time=? WHERE id=?", (failed_attempts, lock_time, user_id))
        else:
            c.execute("UPDATE users SET failed_attempts=? WHERE id=?", (failed_attempts, user_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Incorrect password'}), 401

    c.execute("UPDATE users SET failed_attempts=0, lock_time=0 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['username'] = username
    session['role'] = role
    print(f"OTP for {username}: {otp}")  # In real apps, send via email/SMS

    return jsonify({'message': 'OTP sent. Please verify.', 'redirect_to': '/otp-page'})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    user_otp = data.get('otp')
    real_otp = session.get('otp')
    role = session.get('role')

    if user_otp == real_otp:
        if role == 'borrower':
            return jsonify({'message': 'Welcome Borrower!', 'redirect_to': '/borrower-dashboard'})
        elif role == 'investor':
            return jsonify({'message': 'Welcome Investor!', 'redirect_to': '/investor-dashboard'})
    return jsonify({'message': 'Invalid OTP'}), 401

# Static pages
@app.route('/register-page')
def register_page():
    return send_from_directory('static', 'register.html')

@app.route('/login-page')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/otp-page')
def otp_page():
    return send_from_directory('static', 'verify-otp.html')

@app.route('/borrower-dashboard')
def borrower_dashboard():
    return send_from_directory('static', 'borrower_dashboard.html')

@app.route('/investor-dashboard')
def investor_dashboard():
    return send_from_directory('static', 'investor_dashboard.html')

# Page for impact investor
@app.route('/itsainvest')
def itsainvest_page():
    if os.path.exists('itsainvest.html'):
        return send_from_directory('static', 'static/itsainvest.html')
    else:
        print("itsainvest.html not found.")
        return jsonify({"error": "Page not found"}), 404

# Page for individual commercial investment
@app.route('/individual_investment_page')
def individual_investment_page():
    if os.path.exists('static/commercial-individual.html'):
        return send_from_directory('static', 'commercial-individual.html')
    else:
        print("commercial-individual.html not found.")
        return jsonify({"error": "Page not found"}), 404
    
@app.route('/commercial-individual')
def commercial_individual():
    if os.path.exists('static/commercial-individual.html'):
        return send_from_directory('static', 'commercial-individual.html')
    else:
        print("commercial-individual.html not found.")
        return jsonify({"error": "Page not found"}), 404

@app.route('/commercial-group')
def commercial_group():
    if os.path.exists('static/commercial-group.html'):
        return send_from_directory('static', 'commercial-group.html')
    else:
        print("commercial-group.html not found.")
        return jsonify({"error": "Page not found"}), 404
    
@app.route('/profile')
def profile():
    if os.path.exists('static/profile.html'):
        return send_from_directory('static', 'profile.html')
    else:
        print("profile.html not found.")
        return jsonify({"error": "Page not found"}), 404
    
@app.route('/logout')
def logout():
    session.clear()  # Also clears session data
    if os.path.exists('static/login.html'):
        return send_from_directory('static', 'login.html')
    else:
        print("login not found.")
        return jsonify({"error": "Page not found"}), 404

    
@app.route('/back_dashboard')
def back_dashboard():
    if os.path.exists('static/investor_dashboard.html'):
        return send_from_directory('static', 'investor_dashboard.html')
    else:
        print("investor_dashboard not found.")
        return jsonify({"error": "Page not found"}), 404
  
@app.route('/chatbot')
def chatbot():
    return send_from_directory('static','chatbot.html')        

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
