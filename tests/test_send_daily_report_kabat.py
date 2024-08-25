import unittest
from unittest.mock import patch
from datetime import datetime
from flask import Flask, session
import mongomock
from app.modules.users.security_man.routes import send_daily_report, generate_summary

class TestSecurityRoutes(unittest.TestCase):

    def setUp(self):
        # Setup Flask app and test client
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key'  # Set a secret key for sessions
        self.client = self.app.test_client()

        # Setup in-memory mock MongoDB
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['Cover']

        # Mock the collections used in the routes
        self.sensors_collection = self.db['Sensor_Data']
        self.users_db = self.db['Users']

        # Insert test data into the mock collections
        self.today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.sensors_collection.insert_many([
            {'Temperature': 29.0, 'Vibration SD': 0.01, 'sample_time_utc': self.today},
            {'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': self.today}
        ])
        self.users_db.insert_one({
            'username': 'kabat',
            'email': 'kabat@example.com',
            'Name': 'Kabat',
            'user_role': 'securityMan'  # Adding user_role here
        })

        # Replace the collections in the routes with the mock collections
        send_daily_report.sensors_collection = self.sensors_collection
        send_daily_report.users_db = self.users_db

    def tearDown(self):
        # Clean up the mock database after each test
        self.sensors_collection.delete_many({})
        self.users_db.delete_many({})

    @patch('app.modules.users.security_man.routes.send_email')
    def test_send_daily_report_no_data(self, mock_send_email):
        # Mock the session as if a user with the 'securityMan' role is logged in
        with self.client.session_transaction() as sess:
            sess['user_role'] = 'securityMan'
    
        # Remove all sensor data for the test
        self.sensors_collection.delete_many({})
    
        # Call the function to test with no data
        with self.app.test_request_context():
            response, status_code = send_daily_report()
    
        # Convert the response to JSON
        response_json = response.get_json()
    
        # Check that the response indicates no data available
        self.assertFalse(response_json['success'])
        # self.assertEqual(response_json['message'], 'No data available for today.')

    # @patch('app.modules.users.security_man.routes.send_email')
    # def test_send_daily_report_success(self, mock_send_email):
    #     # Mock the session as if a user with the 'securityMan' role is logged in
    #     with self.client.session_transaction() as sess:
    #         sess['user_role'] = 'securityMan'
    
    #     # Simulate a successful email send
    #     mock_send_email.return_value = True
    
    #     # Call the function to test
    #     with self.app.test_request_context():
    #         response, status_code = send_daily_report()
    
    #     # Convert the response to JSON
    #     response_json = response.get_json()
    
    #     # Check that the response is successful
    #     self.assertFalse(response_json['success'])

    def test_send_daily_report_unauthorized(self):
        # Mock the session as if a user with an incorrect role is logged in
        with self.client.session_transaction() as sess:
            sess['user_role'] = 'other_role'
    
        # Call the function to test unauthorized access
        with self.app.test_request_context():
            response, status_code = send_daily_report()
    
        # Convert the response to JSON
        response_json = response.get_json()

        # Check that the response indicates unauthorized access
        self.assertFalse(response_json['success'])
        self.assertEqual(response_json['message'], 'Unauthorized access.')

    def test_generate_summary(self):
        # Test the summary generation
        sensor_data = list(self.sensors_collection.find({'sample_time_utc': {'$regex': f'^{self.today}'}}))
        summary = generate_summary(sensor_data)
        
        # Check that the summary contains the expected content
        self.assertIn("Daily Summary Report", summary)
        self.assertIn("Temperature: 29.0", summary)
        self.assertIn("Vibration SD: 0.01", summary)

if __name__ == "__main__":
    unittest.main()
