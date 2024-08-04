from flask import Blueprint, jsonify, redirect, request, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
import os

resident_bp = Blueprint('resident', __name__)

# Assuming the database connection is established in Cover.py
db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Data")
sensors_collection = db['Sensor_Data']

@resident_bp.route('/monthly_snapshot', methods=['GET'])
def monthly_snapshot():
    month = request.args.get('month', default=7, type=int)  # Default to July if no month is selected
    year = 2024

    # Calculate the date range for the selected month
    start_date = datetime(year, month, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = (datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    print(f"Querying data from {start_date} to {end_date}")

    # Fetch sensor data for the specified building within the date range
    sensor_data = list(sensors_collection.find({
        'sample_time_utc': {
            '$gte': start_date,
            '$lt': end_date
        }
    }))

    #print(f"Fetched sensor data: {sensor_data}")

    # Process the data to create a snapshot (e.g., average values, alerts)
    snapshot = process_sensor_data(sensor_data)

    return render_template('monthly_snapshot.html', snapshot=snapshot, month=month)

def process_sensor_data(sensor_data):
    snapshot = {
        'average_temperature': 0,
        'average_vibration': 0,
        'alerts': []
    }
    total_temp = 0
    total_vibration = 0
    count = 0
    threshold_value = 5.0  # Define the threshold value for vibration

    print(f"Processing {len(sensor_data)} records")

    for record in sensor_data:
        #print(f"Processing record: {record}")
        total_temp += record['Temperature']
        total_vibration += record['Vibration SD']
        count += 1

        if record['Vibration SD'] > threshold_value:
            snapshot['alerts'].append(f'High vibration detected on {record["sample_time_utc"]}')

    if count > 0:
        snapshot['average_temperature'] = total_temp / count
        snapshot['average_vibration'] = total_vibration / count

    print(f"Snapshot: {snapshot}")
    return snapshot

