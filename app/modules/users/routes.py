from datetime import datetime, timedelta
import json
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session,make_response
import pymongo
from ..api.auth import get_access_token
from ..api.client import get_sensor_readings, insert_data_to_mongodb, is_token_valid, load_data_from_file, retrieve_token_from_db, save_to_file, save_to_mongodb, save_token_to_db, insert_data_from_jason
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
            session['name'] = user['Name']  # Store user's name in session
            if username == 'engineer':
                session['user_role'] = 'engineer'
            elif username == 'kabat':
                session['user_role'] = 'securityMan'
            else:
                session['user_role'] = 'resident'
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
        
        user = user_model.find_user(username, old_password)
        
        if user and user['email'] == email:
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
    mac_addresses = ["C8:FD:9D:A5:27:FB"]
    start_date = "2024-08-16T00:00:00.000Z"
    end_date = "2024-08-18T09:50:50.000Z"

    try:
        # token = retrieve_token_from_db(client)
        # if not token or not is_token_valid(token):
        #     token = get_access_token(email, password)
        #     print(token)
        #     save_token_to_db(token, client)
        # sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        # if 'data' in sensor_readings and 'readings_data' in sensor_readings['data']:
        #     sensor_readings = sensor_readings['data']['readings_data']
        #     print(sensor_readings)
        #     save_to_file(sensor_readings, "sensor_readings_aug.json")
        # insert_data_to_mongodb(client, sensor_readings)
        with open('sensor_readings_aug.json', 'r') as file:
            print("im in open the file")
            json_data = json.load(file)
            #readings = json_data['data']['readings_data']  # Access the list of readings
            for reading in json_data:
                print(reading)
        # Insert each reading into MongoDB
        for reading in json_data:
            insert_data_from_jason(client,reading)

        return "Data refresh successful"
    except Exception as e:
        print(e)
        return "Something went wrong"

@users_bp.route('/')
def index():
    return render_template('index.html')

@users_bp.route('/data')
def get_data():
    month = request.args.get('month')
    date = request.args.get('date')
    db = client.get_database("Data")
    collection = db['Sensor_Data']
    
    if date:
        # Handle date filtering
        start_date = f"{date}T00:00:00.000Z"
        end_date = f"{date}T23:59:59.999Z"
        data = list(collection.find(
            {"sample_time_utc": {"$gte": start_date, "$lt": end_date}},
            {'_id': 0, 'Temperature': 1, 'Vibration SD': 1, 'Tilt': 1, 'sample_time_utc': 1}
        ))
        print(f"Retrieved {len(data)} records for date: {date}")
    elif month:
        # Handle month filtering
        year, month = map(int, month.split('-'))
        start_date = f"{year:04d}-{month:02d}-01T00:00:00.000Z"
        if month == 12:
            end_date = f"{year + 1:04d}-01-01T00:00:00.000Z"
        else:
            end_date = f"{year:04d}-{month + 1:02d}-01T00:00:00.000Z"
        
        data = list(collection.find(
            {"sample_time_utc": {"$gte": start_date, "$lt": end_date}},
            {'_id': 0, 'Temperature': 1, 'Vibration SD': 1, 'Tilt': 1, 'sample_time_utc': 1}
        ))
        print(f"Retrieved {len(data)} records for month: {month}")
    else:
        data = list(collection.find({}, {'_id': 0, 'Temperature': 1, 'Vibration SD': 1, 'Tilt': 1, 'sample_time_utc': 1}))

    return jsonify(data)



@users_bp.route('/logout', methods=['GET'], endpoint='logout_user')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    response = make_response(redirect(url_for('users.login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
