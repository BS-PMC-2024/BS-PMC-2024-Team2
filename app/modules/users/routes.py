# app/modules/users/routes.py

from datetime import datetime, timedelta
import json
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
import pymongo
from ..api.auth import get_access_token
from ..api.client import get_sensor_readings, insert_data_to_mongodb, is_token_valid, load_data_from_file, retrieve_token_from_db, save_to_file, save_to_mongodb, save_token_to_db
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
            session['user_role'] = 'engineer' if username == 'engineer' else 'other'  
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

@users_bp.route('/refresh_API_data', methods=['POST'])
def refresh_API_data():
    email = "sce@atomation.net"
    password = "123456"
    mac_addresses = ["F2:25:55:24:54:A6"]
    start_date = "2024-07-06T00:00:00.000Z"
    end_date = "2024-07-07T23:59:59.000Z"

    print("Before try ##################!")
    try:
        token = retrieve_token_from_db(client)
        if not token or not is_token_valid(token):
            token = get_access_token(email, password)
            save_token_to_db(token, client)
            print("i got a new token @@@@@@@@@@@@@@@@@@@@")
        #print(token)
        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        # Inspect the structure of sensor_readings
        print("Sensor readings retrieved:")
        print(sensor_readings)
        print("Type of sensor_readings:", type(sensor_readings))
        # Extract the actual readings data if it's nested
        if 'data' in sensor_readings and 'readings_data' in sensor_readings['data']:
            sensor_readings = sensor_readings['data']['readings_data']
        
        # print("Processed sensor readings:")
        # print(sensor_readings)
        # print("Type of processed sensor_readings:", type(sensor_readings))
        # save_to_file(sensor_readings, 'sensor_readings.json')
        # data = load_data_from_file()
        insert_data_to_mongodb(client, sensor_readings)
        return "i did it"

    except Exception as e:
        print(e)
        return "something went wrong"

@users_bp.route('/')
def index():
    return render_template('index.html')
@users_bp.route('/data')
def get_data():
    db = client.get_database("Data")
    collection = db['Sensor_Data']
    data = list(collection.find({}, {'_id': 0, 'Temperature': 1, 'Vibration SD': 1, 'sample_time_utc': 1}))  # Retrieve necessary fields
    return jsonify(data)