from flask import Blueprint, jsonify, session
from pymongo import MongoClient
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize the security blueprint
security_bp = Blueprint('security', __name__)

# Database connection
db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Data")
sensors_collection = db['Sensor_Data']
db_cover=client.get_database("Cover")
users_db=db_cover['users']

@security_bp.route('/send_daily_report', methods=['POST'])
def send_daily_report():
    # Check if the logged-in user is 'kabat'
    if session.get('user_role') != 'securityMan':
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403

    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Fetch sensor data for today's date
    sensor_data = list(sensors_collection.find({
        'sample_time_utc': {'$regex': f'^{today}'}
    }))
    
    if not sensor_data:
        return jsonify({'success': False, 'message': 'No data available for today.'})

    # Generate the summary report
    summary = generate_summary(sensor_data)
    # Retrieve Kabat's information from the database
    kabat_info = users_db.find_one({'username': 'kabat'})
    if not kabat_info:
        return jsonify({'success': False, 'message': 'Kabat information not found.'})
    
    # Send the daily summary report via email
    email_sent = send_email(kabat_info['email'], 'Daily Summary Report', summary)
    
    if email_sent:
        return jsonify({'success': True, 'message': 'Email sent successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send email.'})

def generate_summary(sensor_data):
    # Generate a textual summary report of the day's sensor data
    summary = "Daily Summary Report\n\n"
    for record in sensor_data:
        summary += f"Time: {record['sample_time_utc']}\nTemperature: {record['Temperature']}\nVibration SD: {record['Vibration SD']}\n\n"
    return summary

def send_email(to_email, subject, body):
    sender_email = "coversensor@outlook.com"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.starttls()
        SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', None)
        server.login('apikey', SENDGRID_API_KEY)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
