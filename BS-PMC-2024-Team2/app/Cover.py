from flask import Flask,render_template, request, url_for, redirect,session
from dotenv import load_dotenv
import pymongo
import secrets
import os

app = Flask(__name__)

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
    print("Sucsseful connect to MongoDB")
except Exception as e:
    print(e)

@app.route('/')
def home():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)