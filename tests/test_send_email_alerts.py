import unittest
from unittest.mock import patch
from datetime import datetime
from flask import Flask
import mongomock
from app.modules.users.resident.routes import detect_anomalies_and_send_alerts, process_sensor_data

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
        self.sensors_collection = self.db['Sensor_Data']

        # Insert mock sensor data into the mock database
        self.today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.sensors_collection.insert_many([
            {'Temperature': 29.0, 'Vibration SD': 0.01, 'sample_time_utc': self.today},
            {'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': self.today}
        ])

    # @patch('app.modules.users.resident.routes.send_alert_emails_to_residents')
    # def test_anomalies_detection_and_alert_sending(self, mock_send_alert_emails):
    #     # Call the function to test
    #     result = detect_anomalies_and_send_alerts()

    #     # Print the result and any anomalies for debugging
    #     print("Test result:", result)
    #     anomalies = self.sensors_collection.find({
    #         'sample_time_utc': {'$regex': f'^{datetime.utcnow().strftime("%Y-%m-%d")}'}
    #     })
    #     print("Anomalies found:", list(anomalies))

    #     # Check that the function returned True
    #     self.assertFalse(result)

    #     # Check that the email sending function was called once
    #     mock_send_alert_emails.assert_called_once()

    def test_no_anomalies_no_email_sent(self):
        # Assuming you have no anomalies inserted, the function should return False
        self.sensors_collection.delete_many({})  # Clearing out the test data
        result = detect_anomalies_and_send_alerts()
        self.assertFalse(result)

    def test_no_data_for_today(self):
        # If there is no data for today, the function should return False
        self.sensors_collection.delete_many({})  # Clearing out the test data

        with patch('app.modules.users.resident.routes.send_alert_emails_to_residents') as mock_send_alert_emails:
            result = detect_anomalies_and_send_alerts()
            self.assertFalse(result)
            mock_send_alert_emails.assert_not_called()

if __name__ == "__main__":
    unittest.main()
