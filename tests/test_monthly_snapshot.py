import unittest
import sys
import os

# Adjust the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.main_cover import create_app, client
from app.modules.users.resident.routes import process_sensor_data
import mongomock

class MonthlySnapshotTestCase(unittest.TestCase):

    def setUp(self):
        print("Setting up Flask app for testing...")
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Connecting to the mock MongoDB
        print("Connecting to mock MongoDB...")
        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client.get_database("Data")
        self.db.Sensor_Data = self.db['Sensor_Data']

        # Mock the MongoDB object in routes
        self.app.blueprints['resident'].mongo = self.mongo_client

        # Adding mock sensor data
        print("Inserting test data...")
        self.db.Sensor_Data.insert_many([
            {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
            {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
        ])

    def tearDown(self):
        # Dropping the test database
        print("Dropping test database...")
        self.mongo_client.drop_database("Data")

    def test_monthly_snapshot(self):
        print("Testing monthly snapshot endpoint for July...")
        response = self.client.get('/resident/monthly_snapshot?month=7')
        print(response.data)  # Print response for debugging
        self.assertEqual(response.status_code, 200, "Failed to get monthly snapshot")
        self.assertIn(b"Building Sensor Data Summary", response.data)
        self.assertIn(b"Average Temperature", response.data)
        self.assertIn(b"27.0", response.data)  # Check if the average temperature is correct
        self.assertIn(b"0.006", response.data)  # Check if the average vibration is correct

    def test_process_sensor_data(self):
        print("Testing process_sensor_data function...")
        sensor_data = [
            {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
            {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
        ]
        snapshot = process_sensor_data(sensor_data)
        self.assertEqual(snapshot['average_temperature'], 27.0)
        self.assertEqual(snapshot['average_vibration'], 0.006)
        self.assertEqual(len(snapshot['alerts']), 0)

if __name__ == '__main__':
    unittest.main()
