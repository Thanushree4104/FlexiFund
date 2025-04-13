from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for, render_template, flash
from flask_cors import CORS
import sqlite3
import hashlib
import random
import time
from datetime import datetime

from algorithm import calculate_match_score, find_matches
from sample_users import users

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

def init_credit_db():
    conn = sqlite3.connect('credit.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS credit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monthly_surplus REAL,
            financial_diversity INTEGER,
            merchant_txns INTEGER,
            geo_stability INTEGER,
            business_docs INTEGER,
            score REAL,
            last_updated TEXT,
            FOREIGN KEY (id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_and_calculate_credit_score(user_id):
    # Start tracking the function execution
    print(f"Starting credit score calculation for user_id: {user_id}")

    try:
        # Connect to the database
        conn = sqlite3.connect('credit.db')
        cursor = conn.cursor()
        print("Database connection established.")

        # Query to get user data and last calculated date
        cursor.execute("SELECT monthly_surplus, financial_diversity, merchant_txns, geo_stability, business_docs, last_updated, score FROM credit WHERE id = ?", (user_id,))
        data = cursor.fetchone()

        if not data:
            print(f"No data found for user_id: {user_id}")
            conn.close()
            return None  # No data found for user

        # If data exists, unpack it
        monthly_surplus, financial_diversity, merchant_txns, geo_stability, business_docs, last_calculated, current_credit_score = data
        print(f"Data retrieved for user_id {user_id}: {data}")

        # Recalculate the score every time the user logs in
        weights = {
            "monthly_surplus": 0.3,
            "financial_diversity": 0.2,
            "merchant_txns": 0.2,
            "geo_stability": 0.15,
            "business_docs": 0.15
        }

        # Calculate individual scores
        monthly_surplus_score = min(monthly_surplus / 10000, 1.0) * 100
        financial_diversity_score = financial_diversity * 20
        merchant_txns_score = min(merchant_txns / 20, 1.0) * 100
        geo_stability_score = min(geo_stability / 5, 1.0) * 100
        business_docs_score = 100 if business_docs == 1 else 50

        # Calculate the final score
        final_score = (
            monthly_surplus_score * weights["monthly_surplus"]
            + financial_diversity_score * weights["financial_diversity"]
            + merchant_txns_score * weights["merchant_txns"]
            + geo_stability_score * weights["geo_stability"]
            + business_docs_score * weights["business_docs"]
        )
        print(f"Calculated final score: {final_score}")

        # Update the credit score and last calculated date in the database
        today = datetime.today().date()
        print(f"Updating score and last_updated for user_id {user_id} in the database...")

        conn = sqlite3.connect('credit.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE credit SET score = ?, last_updated = ? WHERE id = ?",
                       (round(final_score, 2), today, user_id))
        conn.commit()
        print(f"Score for user_id {user_id} updated successfully.")

        conn.close()
        return round(final_score, 2)

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

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

    session['user_id'] = user_id
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
    user_id = session.get('user_id')

    if user_otp == real_otp:
        if role == 'borrower':
            return jsonify({'message': f'Welcome Borrower! Your user ID is {user_id}', 'redirect_to': '/borrower-dashboard'})
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
    user_id = session.get('user_id')  # Get the user_id stored in the session after login

    if user_id:
        print(f"User ID: {user_id} found in session.")  # Logging the user_id
        credit_score = get_and_calculate_credit_score(user_id)
        
        if credit_score is not None:
            print(f"Credit score calculated: {credit_score}")  # Logging the credit score
            return render_template('borrower-dashboard.html', credit_score=credit_score)
        else:
            print("No credit score data available.")  # Logging when no credit score is available
            return render_template('borrower-dashboard.html', credit_score="Data not available.")
    else:
        print("User not logged in.")  # Logging if the user is not logged in
        return "User not logged in"

@app.route('/investor-dashboard')
def investor_dashboard():
    return render_template('investor_dashboard.html')

@app.route('/impact_dashboard')
def impact_dashboard():
    return render_template('impact_dashboard.html')

@app.route('/commercial_dashboard')
def commercial_dashboard():
    return render_template('commercial_dashboard.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/royalty')
def royalty():
    return render_template('royalty.html')

@app.route('/community-loan')
def community_loan():
    return render_template("community-loan.html")




@app.route('/matchmaking', methods=['GET'])
def matchmaking():
    current_user = users[0]
    all_values = set()
    all_industries = set()
    all_skills = set()
    all_goals = set()

    for user in users:
        all_values.update(user['values'])
        all_industries.update(user['industry'])
        all_skills.update(user['skills'])
        all_goals.update(user['goals'])

    return render_template(
        'matchmaking.html',
        current_user=current_user,
        all_values=sorted(list(all_values)),
        all_industries=sorted(list(all_industries)),
        all_skills=sorted(list(all_skills)),
        all_goals=sorted(list(all_goals))
    )

@app.route('/find_matches', methods=['POST'])
def find_matches_route():
    current_user = users[0]
    role = request.form.get('role')
    values = request.form.getlist('values')
    industries = request.form.getlist('industry')
    skills = request.form.getlist('skills')
    goals = request.form.getlist('goals')
    experience_min = int(request.form.get('experience_min', 0))
    experience_max = int(request.form.get('experience_max', 30))

    criteria = {
        'role': role,
        'values': values,
        'industry': industries,
        'skills': skills,
        'goals': goals,
        'experience_min': experience_min,
        'experience_max': experience_max
    }

    matches = find_matches(current_user, criteria, users)

    return render_template(
        'matches.html',
        matches=matches,
        criteria=criteria,
        current_user=current_user
    )

@app.route('/match-results')
def match_results():
    matches = [
        {
            'borrower_name': 'Jane Doe',
            'investor_name': 'John Smith',
            'shared_vision': 'Sustainable Agriculture',
            'match_score': 92
        },
        {
            'borrower_name': 'Ali Khan',
            'investor_name': 'Lena Wong',
            'shared_vision': 'Green Energy',
            'match_score': 88
        }
    ]
    return render_template('matches.html', matches=matches)

if __name__ == '__main__':
    init_db()
    init_credit_db()
    app.run(debug=True)
