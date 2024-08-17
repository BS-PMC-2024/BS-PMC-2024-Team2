from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import pymongo
import secrets
import os
import sys
from threading import Thread
import time
from modules.users.resident.routes import detect_anomalies_and_send_alerts, send_alert_emails_to_residents



sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

# Database client
client = None
db = None

def create_app(config_name):
    global client, db

    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    try:
        load_dotenv()
    except Exception as e:
        err_msg = f"Failed to load env vars - {e}"
        print(err_msg)
        raise Exception(err_msg)

    db_username = os.environ.get('DB_USERNAME', None)
    db_password = os.environ.get('DB_PASSWORD', None)
    client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
    db = client.get_database("Cover")

    try:
        client.admin.command('ping')
        print("Successful connection to MongoDB")
    except Exception as e:
        print(e)

    # Register the blueprints
    from modules.users.routes import users_bp
    from modules.users.engineer.routes import engineer_bp
    from modules.users.resident.routes import resident_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(engineer_bp, url_prefix='/engineer')
    app.register_blueprint(resident_bp, url_prefix='/resident')

    @app.route('/')
    def home():
        return redirect(url_for('users.login'))
    
    @app.after_request
    def apply_caching(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app


def check_for_anomalies():
    # This will keep running in the background
    while True:
        anomalies_detected = detect_anomalies_and_send_alerts()
        if anomalies_detected:
            break  # Stop further checks after detecting an anomaly
        time.sleep(60)  # Check every 60 seconds

def start_background_anomaly_check():
    thread = Thread(target=check_for_anomalies)
    thread.daemon = True  # Ensures the thread will close when the main program exits
    thread.start()

if __name__ == '__main__':
    app = create_app('default')
    start_background_anomaly_check()
    app.run(debug=True)
