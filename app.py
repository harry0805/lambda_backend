#!/usr/bin/env python
import os
from flask import Flask, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

if __name__ == '__main__':
    # For local testing
    import json
    with open('env.json') as f:
        env = json.load(f)
        for key, value in env.items():
            os.environ[key] = value

app = Flask(__name__)

# Generate a secret key for the session
app.secret_key = os.urandom(24)

# MongoDB connection string.
# For a production deployment, you might use an Atlas connection string stored in an environment variable.
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise ValueError("You must specify the MONGO_URI environment variable")
client = MongoClient(MONGO_URI)
db = client.get_database('lambda_backend')  # uses the database specified in the URI
users_collection = db.users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Username and password are required."

        # Check if user already exists
        if users_collection.find_one({'username': username}):
            return "User already exists. Please choose a different username."

        # Hash the password for security
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})

        # Store username in session and redirect to the welcome page.
        session['username'] = username
        return redirect(url_for('home'))

    # Simple HTML form for registration
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect to the home page
    if 'username' in session:
        username = session['username']
        # Render the index.html template and pass the username variable
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user.get('password', ''), password):
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid username or password!"

    # Render the login.html template when method is GET
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        # Render the home.html template and pass the username variable
        return render_template('home.html', username=username)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)