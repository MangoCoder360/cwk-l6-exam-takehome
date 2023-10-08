from os import environ as env
import mysql.connector
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

def get_conn():
    conn = mysql.connector.connect(
        host=env.get("DB_HOST"),
        user=env.get("DB_USER"),
        password=env.get("DB_PASSWORD"),
        database=env.get("DB_NAME")
    )
    return conn

def initTable():
    db = get_conn()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS L6TakehomeUsers ( UserID INT AUTO_INCREMENT PRIMARY KEY, Username VARCHAR(255), Password VARCHAR(255) );")
    db.commit()
    print("Database Ready!")

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_conn()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM L6TakehomeUsers WHERE Username = %s AND Password = %s", (username, password))
            result = cursor.fetchone()
            if result:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', message="Invalid username or password!")
        else:
            return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm-password']
            if password != confirm_password:
                return render_template('register.html', message="Passwords do not match!")
            db = get_conn()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM L6TakehomeUsers WHERE Username = %s", (username,))
            result = cursor.fetchone()
            if result:
                return render_template('register.html', message="Username already exists!")
            else:
                cursor.execute("INSERT INTO L6TakehomeUsers (Username, Password) VALUES (%s, %s)", (username, password))
                db.commit()
                return redirect(url_for('login'))
        else:
            return render_template('register.html')
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    initTable()
    app.run(host="0.0.0.0", port=5580)