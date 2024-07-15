# app/modules/users/routes.py

from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import pymongo
from .models import User
import os

users_bp = Blueprint('users', __name__)

db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Cover")

user_model = User(db)

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_model.find_user(username, password)
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('users.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@users_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        # Find the user in the database
        user = user_model.find_user(username, old_password)
        
        if user and user['email'] == email:
            # Update the user's password
            user_model.update_password(username, new_password)
            flash('Password successfully changed!', 'success')
            return redirect(url_for('users.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('change_password.html')


@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_model.find_user_by_username(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('users.register'))
        else:
            user_model.insert_user(username, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('users.login'))
    return render_template('register.html')

@users_bp.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('users.login'))

@users_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('users.login'))

@users_bp.route('/forgot_password')
def forgot_password():
    return "Forgot Password page (to be implemented)"
