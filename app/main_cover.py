# app/Cover.py

from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
import pymongo
import secrets
import os
import sys
# from app.modules.users.routes import users_bp

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

    # Register the blueprint
    from modules.users.routes import users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    @app.route('/')
    def home():
        return redirect(url_for('users.login'))

    return app

    
if __name__ == '__main__':
    app = create_app('default')
    app.run(debug=True)