import unittest
import pytest
import mongomock
from flask import Flask
from flask.testing import FlaskClient
from flask.json import jsonify

class TestDataRoutes(unittest.TestCase):

    def setUp(self):
        # Set up Flask app and testing client
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Set up MongoDB mock client
        self.mongo_client = mongomock.MongoClient()
        self.db_Data = self.mongo_client['Data']

        # Create mock collection and insert test data
        self.db_Data['Sensor_Data'].insert_many([
            {'Temperature': 25.0, 'Vibration SD': 0.01, 'sample_time_utc': '2024-07-07T10:46:29.000Z'},
            {'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': '2024-07-07T11:46:29.000Z'}
        ])

        # Assign mock DB collection to a function
        self.app.config['DB'] = self.db_Data
        self.app.route('/users/data')(self.mock_get_data)

    def mock_get_data(self):
        # Mock function for fetching data
        db = self.app.config['DB']
        collection = db['Sensor_Data']
        data = list(collection.find({}, {'_id': 0, 'Temperature': 1, 'Vibration SD': 1, 'sample_time_utc': 1}))
        return jsonify(data)

    def test_get_data(self):
        # Test the /users/data route
        response = self.client.get('/users/data')
        assert response.status_code == 200
        expected_data = [
            {'Temperature': 25.0, 'Vibration SD': 0.01, 'sample_time_utc': '2024-07-07T10:46:29.000Z'},
            {'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': '2024-07-07T11:46:29.000Z'}
        ]
        assert response.json == expected_data

if __name__ == "__main__":
    pytest.main()
