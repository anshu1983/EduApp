from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import random
import sqlite3
import os

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Secret key for session (replace with a secure key in production)
app.secret_key = "supersecretkey123"

# Sample question banks
maths_questions = [
    {"question": "What is 5 + 3?", "answer": "8"},
    {"question": "What is 10 - 4?", "answer": "6"},
    {"question": "What is 2 x 3?", "answer": "6"}
]

english_questions = [
    {"question": "Spell the word: _pple", "answer": "apple"},
    {"question": "What is the opposite of 'big'?", "answer": "small"},
    {"question": "Complete: The cat ___ on the mat.", "answer": "sat"}
]

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

# Check if user is logged in
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                     (username, generate_password_hash(password)))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Username already exists")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/practice/<subject>')
@login_required
def practice(subject):
    session['score'] = 0  # Reset score per session
    return render_template('practice.html', subject=subject)

@app.route('/get_question', methods=['POST'])
@login_required
def get_question():
    subject = request.json['subject']
    if subject == 'maths':
        question = random.choice(maths_questions)
    elif subject == 'english':
        question = random.choice(english_questions)
    else:
        return jsonify({"error": "Invalid subject"}), 400
    return jsonify({"question": question["question"], "id": id(question)})

@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    subject = request.json['subject']
    user_answer = request.json['answer'].strip().lower()
    question_text = request.json['question']
    
    questions = maths_questions if subject == 'maths' else english_questions
    correct_answer = next(q["answer"] for q in questions if q["question"] == question_text)
    
    if user_answer == correct_answer:
        session['score'] = session.get('score', 0) + 1
        result = "Correct!"
    else:
        result = f"Wrong! Correct answer: {correct_answer}"
    
    return jsonify({"result": result, "score": session['score']})

if __name__ == "__main__":
    init_db()  # Initialize database on startup
    app.run(debug=True)