from flask import Blueprint, jsonify, redirect, request, render_template, session
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


resident_bp = Blueprint('resident', __name__)

# Assuming the database connection is established in Cover.py
db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Data")
sensors_collection = db['Sensor_Data']
db_Cover = client.get_database("Cover")
residents_db = db_Cover['Residents']


@resident_bp.route('/monthly_snapshot', methods=['GET'])
def monthly_snapshot():
    month = request.args.get('month', default=7, type=int)  # Default to July if no month is selected
    year = 2024

    # Calculate the date range for the selected month
    start_date = datetime(year, month, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end_date = (datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    print(f"Querying data from {start_date} to {end_date}")

    sensor_data = list(sensors_collection.find({
        'sample_time_utc': {
            '$gte': start_date,
            '$lt': end_date
        }
    }))

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

alerted_anomalies = set()

def send_alert_emails_to_residents(message):
    sender_email = "coversensor@outlook.com"
    subject = "Urgent: Structural Integrity Alert"

    # Retrieve all resident emails from the Cover.Residents collection
    residents = list(residents_db.find({}, {'Email': 1, '_id': 0}))

    for resident in residents:
        email = resident['Email']
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            # Connect to the SendGrid SMTP server
            server = smtplib.SMTP('smtp.sendgrid.net', 587)
            server.starttls()
            SENDGRID_API_KEY=os.environ.get('SENDGRID_API_KEY', None)
            server.login('apikey', SENDGRID_API_KEY)
            text = msg.as_string()
            server.sendmail(sender_email, email, text)
            server.quit()
            print(f"Alert email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

def detect_anomalies_and_send_alerts():    
    today = datetime.now().strftime('%Y-%m-%d')

    # Thresholds for detecting anomalies
    threshold_temperature = 28.5
    threshold_vibration = 0.01

    # Find anomalies for today's date only
    anomalies = sensors_collection.find({
        '$and': [
            {'sample_time_utc': {'$regex': f'^{today}'}},
            {
                '$or': [
                    {'Temperature': {'$gt': threshold_temperature}},
                    {'Vibration SD': {'$gt': threshold_vibration}}
                ]
            }
        ]
    })

    # Check if anomalies exist and send emails only once per run
    if anomalies.count() > 0:
        message = "Warning: Significant structural integrity issues detected today. Please evacuate the building immediately and contact the authorities."
        send_alert_emails_to_residents(message)
        email_sent = True
        print("Anomaly detected, emails sent. Stopping further checks.")
        return True
    
    return False

# Code to display the project for the task of sending the email on abnormal data
# def detect_anomalies_and_send_alerts():
#     threshold_temperature = 28.5
#     threshold_vibration = 0.01
#     anomalies = sensors_collection.find_one({
#         '$or': [
#             {'Temperature': {'$gt': threshold_temperature}},
#             {'Vibration SD': {'$gt': threshold_vibration}}
#         ]
#     })

#     if anomalies:  # Check if anomalies are found and email has not been sent
#         message = "Warning: Significant structural integrity issues detected. Please evacuate the building immediately and contact the authorities."
#         send_alert_emails_to_residents(message)
#         return True

#     return False


# Function to check if the user is logged in as a resident
def is_logged_in_as_resident():
    return session.get('username') == 'resident' and session.get('password') == '12345'

@resident_bp.route('/dashboard', methods=['GET'])
def resident_dashboard():
    if not is_logged_in_as_resident():
        return redirect('/login')

    # Detect anomalies and send alerts if any
    anomalies_detected = detect_anomalies_and_send_alerts()

    if anomalies_detected:
        return render_template('resident_dashboard.html', alert="Anomalies detected. Please check your email for details.")
    else:
        return render_template('resident_dashboard.html', alert="No anomalies detected. All systems normal.")