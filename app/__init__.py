from datetime import timedelta
from flask import Flask, render_template, make_response
from dotenv import load_dotenv
import pymongo
import secrets
import os

def create_app(config_name):
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    # Secure session and cookie handling
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS.
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JS access to cookies.
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout.


    # csrf = CSRFProtect()
    # csrf.init_app(app)
    
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
    app.secret_key = secrets.token_hex(16)

    try:
        client.admin.command('ping')
        print("Successful connection to MongoDB")
    except Exception as e:
        print(e)

    from modules.users.routes import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.after_request
    def apply_caching(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


    return app

db = None  # Placeholder for the db object
