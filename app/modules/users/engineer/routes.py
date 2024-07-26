from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import pymongo
import os

engineer_bp = Blueprint('engineer', __name__)

db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db = client.get_database("Cover")
residents_db = db['Residents']

@engineer_bp.route('/ResidentsInfo')
def ResidentsInfo():
    if 'username' in session:
        residents = list(residents_db.find())
        return render_template('ResidentsInfo.html', username=session['username'], residents=residents)
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('users.login'))
