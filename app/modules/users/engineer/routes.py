from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file
import pymongo
import os
import pandas as pd
from io import BytesIO

engineer_bp = Blueprint('engineer', __name__)

db_username = os.environ.get('DB_USERNAME', None)
db_password = os.environ.get('DB_PASSWORD', None)
client = pymongo.MongoClient(f"mongodb+srv://{db_username}:{db_password}@team2interactivetables.g85jafu.mongodb.net/?retryWrites=true&w=majority&appName=Team2InteractiveTables")
db_Cover = client.get_database("Cover")
residents_db = db_Cover['Residents']

db_Sensor = client.get_database("Data")
sensors_collection = db_Sensor['Sensor_Data']

@engineer_bp.route('/ResidentsInfo')
def ResidentsInfo():
    if 'username' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('users.login'))

    # Fetch all residents
    residents = list(residents_db.find())

    # Aggregate data to count residents per building
    building_counts = residents_db.aggregate([
        {"$group": {"_id": "$Building", "count": {"$sum": 1}}}
    ])
    building_counts_dict = {doc['_id']: doc['count'] for doc in building_counts if doc['_id']}  # Skip empty building names

    return render_template('ResidentsInfo.html', username=session['username'], residents=residents, building_counts=building_counts_dict)

@engineer_bp.route('/export_residents')
def export_residents():
    if 'username' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('users.login'))

    # Fetch residents data from the database
    residents = list(residents_db.find({}, {'_id': 0, 'Name': 1, 'Surname': 1, 'Phone': 1, 'Building': 1, 'Email': 1}))
    df = pd.DataFrame(residents)

    # Create a BytesIO buffer for the Excel file
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Residents')

        # Add additional sheets or enhancements here if needed

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='residents.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@engineer_bp.route('/preview_export', methods=['GET'])
def preview_export():
    if session.get('username') != 'engineer':
        return redirect(url_for('users.dashboard'))

    # Fetch sensor data from the database
    sensor_data = list(sensors_collection.find({}))
    df = pd.DataFrame(sensor_data)

    # Render the data in a preview template
    return render_template('preview_export.html', tables=df.to_html(classes='table table-striped', index=False))
    # return render_template('preview_export.html', tables=[df.to_html(classes='table table-striped')], titles=df.columns.values)

@engineer_bp.route('/export')
def export():
    if session.get('username') != 'engineer':
        return redirect(url_for('users.dashboard'))

    # Fetch sensor data from the database
    sensor_data = list(sensors_collection.find({}))
    df = pd.DataFrame(sensor_data)

    # Create a BytesIO buffer for the Excel file
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sensor Data')

        # Add additional sheets or enhancements here
        workbook = writer.book
        worksheet = writer.sheets['Sensor Data']

        # Example: Add a summary
        worksheet.write('K1', 'Summary')
        worksheet.write('K2', 'Average Temperature')
        worksheet.write('L2', df['Temperature'].mean())
        worksheet.write('K3', 'Average Vibration')
        worksheet.write('L3', df['Vibration SD'].mean())

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='sensor_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@engineer_bp.route('/abnormal_data', methods=['GET'])
def abnormal_data():
    if session.get('username') != 'engineer':
        return redirect(url_for('users.dashboard'))

    # Fetch sensor data from the database
    sensor_data = list(sensors_collection.find({}))
    df = pd.DataFrame(sensor_data)

    # Debugging: Print the first few rows of the DataFrame

    # Convert columns to numeric if needed
    df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    df['Vibration SD'] = pd.to_numeric(df['Vibration SD'], errors='coerce')

    # Filter the data
    filtered_df = df[(df['Temperature'] > 28.5) | (df['Vibration SD'] > 0.01)]

    print("DataFrame Head:\n", filtered_df.head())
    # Render the filtered data in a preview template
    return render_template('abnormal_data.html', tables=filtered_df.to_html(classes='table table-striped', index=False))
