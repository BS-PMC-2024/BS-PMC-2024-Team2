from flask import Flask
from dotenv import load_dotenv
import pymongo
import os
import secrets

app = Flask(__name__, template_folder='app/templates')
load_dotenv()

db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Cover")
app.secret_key = secrets.token_hex(16)

