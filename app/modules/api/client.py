import datetime
import json
import requests
from .auth import get_access_token

base_url = "https://atapi.atomation.net/api/v1/s2s/v1_0"

def get_sensor_readings(token, mac_addresses, start_date, end_date):

    sensors_readings_url = f"{base_url}/sensors_readings"


    sensors_readings_payload = {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "mac": mac_addresses,
            "createdAt": True
        },
        "limit": {
            "page": 1,
            "page_size": 100
        }
    }


    sensors_readings_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }


    response = requests.post(sensors_readings_url, headers=sensors_readings_headers, data=json.dumps(sensors_readings_payload))


    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve sensors readings: {response.json()}")
    
def save_to_mongodb(data, client):
    print("hello im in save to mongodb")
    db = client['sensor_data']
    collection = db['readings']
    print("hello i created sensodata collection")
    for reading in data['data']:
        print(f"Reading data: {reading}")  # Debugging line
        # Create a document for MongoDB
        document = {
            "temperature": reading.get("Temperature"),
            "vibration": reading.get("Vibration SD"),
            "Tilt": reading.get("Tilt", 0),  # Handle missing 'Impact' key
            "date": reading.get("sample_time_utc"),
            "hour": datetime.strptime(reading.get("sample_time_utc"), "%Y-%m-%dT%H:%M:%S.%fZ").hour
        }
        print(f"Document to insert: {document}")  # Debugging line
        # Insert the document into the MongoDB collection
        collection.insert_one(document)
    print("Data saved to MongoDB")


def is_token_valid(token):
    url = 'https://atapi.atomation.net/api/v1/s2s/v1_0/auth/login' # Example validation endpoint
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        token = data['data']['token']
        expires_in = data['data']['expires_in']
        refresh_token = data['data']['refresh_token']
        print("Authentication successful.")
        print(f"Token: {token}")
        print(f"Expires in: {expires_in} seconds")
        print(f"Refresh Token: {refresh_token}")
    return response.status_code == 200

def save_token_to_db(token, client):
    db = client['auth']
    collection = db['tokens']
    collection.update_one({}, {"$set": {"token": token}}, upsert=True)
    print("Token saved to MongoDB")

def retrieve_token_from_db(client):
    db = client['auth']
    collection = db['tokens']
    token_doc = collection.find_one()
    if token_doc:
        return token_doc.get('token')
    return None

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")


def insert_data_to_mongodb(client, data):
    # Connect to MongoDB
    db = client['Data']
    collection = db['Sensor_Data']
    print("im in insert data")

    def filter_data(entry):
        try:
             # Ensure all required keys are present, provide default values if not
            temperature = entry['Temperature'] if 'Temperature' in entry else 0
            vibration_sd = entry['Vibration SD'] if 'Vibration SD' in entry else 0
            tilt = entry['Tilt'] if 'Tilt' in entry else 0
            sample_time_utc = entry['sample_time_utc']  # Assumes 'sample_time_utc' must exist

            return {
                "Temperature": entry["Temperature"],
                "Vibration SD": entry["Vibration SD"],
                "Tilt": entry["Tilt"],
                "sample_time_utc": entry["sample_time_utc"]
            }
        except KeyError as e:
            print(f"Missing key {e} in entry: {entry}")
            return None

   # Filter the data
    if isinstance(data, list):
        filtered_data = [filter_data(entry) for entry in data]
        filtered_data = [entry for entry in filtered_data if entry is not None]  # Remove None entries

        for entry in filtered_data:
            # Check if a document with the same sample_time_utc already exists
            existing_document = collection.find_one({"sample_time_utc": entry["sample_time_utc"]})
            if existing_document:
                print(f"Duplicate entry found for {entry['sample_time_utc']}, skipping insertion.")
            else:
                collection.insert_one(entry)

    else:
        filtered_data = filter_data(data)
        if filtered_data is not None:
            # Check if a document with the same sample_time_utc already exists
            existing_document = collection.find_one({"sample_time_utc": filtered_data["sample_time_utc"]})
            if existing_document:
                print(f"Duplicate entry found for {filtered_data['sample_time_utc']}, skipping insertion.")
            else:
                collection.insert_one(filtered_data)

    print("Data inserted successfully into MongoDB!")
    
def load_data_from_file():
    with open('sensor_readings.json', 'r') as f:
        data = json.load(f)
    return data["data"]["readings_data"]


def insert_data_from_jason(client, data ):
    print("im insert_data_from_jason")
    # Connect to MongoDB
    db = client['Data']
    collection = db['Sensor_Data']
    # Check if data already exists to avoid duplicates


    def filter_data(entry):
        try:
            # Provide default values if keys are not present
            temperature = entry.get('Temperature', 0)
            vibration_sd = entry.get('Vibration SD', 0)
            tilt = entry.get('Tilt', 0)  # Default tilt to 0 if not present
            sample_time_utc = entry['sample_time_utc']  # Assumes 'sample_time_utc' must exist

            return {
                "Temperature": temperature,
                "Vibration SD": vibration_sd,
                "Tilt": tilt,
                "sample_time_utc": sample_time_utc
            }
        except KeyError as e:
            print(f"Missing key {e} in entry: {entry}")
            return None

   # Filter the data
    if isinstance(data, list):
        filtered_data = [filter_data(entry) for entry in data]
        filtered_data = [entry for entry in filtered_data if entry is not None]  # Remove None entries

        for entry in filtered_data:
            # Check if a document with the same sample_time_utc already exists
            existing_document = collection.find_one({"sample_time_utc": entry["sample_time_utc"]})
            if existing_document:
                print(f"Duplicate entry found for {entry['sample_time_utc']}, skipping insertion.")
            else:
                collection.insert_one(entry)

    else:
        filtered_data = filter_data(data)
        if filtered_data is not None:
            # Check if a document with the same sample_time_utc already exists
            existing_document = collection.find_one({"sample_time_utc": filtered_data["sample_time_utc"]})
            if existing_document:
                print(f"Duplicate entry found for {filtered_data['sample_time_utc']}, skipping insertion.")
            else:
                print("Data inserted successfully into MongoDB!")
                collection.insert_one(filtered_data)
