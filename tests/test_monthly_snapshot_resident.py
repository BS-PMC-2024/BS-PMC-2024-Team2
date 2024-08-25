import unittest
from unittest.mock import patch
from datetime import datetime
import mongomock
from flask import Flask
from app.modules.users.resident.routes import detect_anomalies_and_send_alerts, process_sensor_data, resident_bp

class TestResidentRoutes(unittest.TestCase):

    def setUp(self):
        # Set up a Flask app and a test client
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key'  # Add a secret key for session management
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Use mongomock to create a mock MongoDB database
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['Data']

        # Assign the mock DB to the blueprint
        resident_bp.sensors_collection = self.db['Sensor_Data']

        # Insert mock sensor data into the mock database
        self.db['Sensor_Data'].insert_many([
            {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
            {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
        ])

        # Register the blueprint with the test Flask app
        self.app.register_blueprint(resident_bp, url_prefix='/resident')

    def test_process_sensor_data(self):
        # Test the processing of sensor data
        sensor_data = [
            {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
            {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
        ]
        snapshot = process_sensor_data(sensor_data)
        self.assertEqual(snapshot['average_temperature'], 27.0)
        self.assertEqual(snapshot['average_vibration'], 0.006)
        self.assertEqual(len(snapshot['alerts']), 0)

    def test_no_anomalies_no_email_sent(self):
        # Clear out the test data
        resident_bp.sensors_collection.delete_many({})  # Clearing out the test data

        # Insert mock data without anomalies
        today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        resident_bp.sensors_collection.insert_many([
            {'Temperature': 20.0, 'Vibration SD': 0.001, 'sample_time_utc': today},
            {'Temperature': 21.0, 'Vibration SD': 0.002, 'sample_time_utc': today}
        ])

        # Call the function to test
        result = detect_anomalies_and_send_alerts()
        self.assertFalse(result)

    def test_no_data_for_today(self):
        # Clear out the test data
        resident_bp.sensors_collection.delete_many({})  # Clearing out the test data

        # Test when there is no data for today
        with patch('app.modules.users.resident.routes.send_alert_emails_to_residents') as mock_send_alert_emails:
            result = detect_anomalies_and_send_alerts()
            self.assertFalse(result)
            mock_send_alert_emails.assert_not_called()

if __name__ == "__main__":
    unittest.main()
