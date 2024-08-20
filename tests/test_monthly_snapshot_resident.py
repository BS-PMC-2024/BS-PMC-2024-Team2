# import unittest
# import pytest
# from flask import Flask, session, url_for
# import os
# import mongomock

# class MonthlySnapshotTestCase(unittest.TestCase):

#     def setUp(self):
#         self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
#         self.app.secret_key = 'test_secret_key'
#         self.app.config['TESTING'] = True
#         self.client = self.app.test_client()

#         self.mongo_client = mongomock.MongoClient()
#         self.db = self.mongo_client['Data']


#         from app.modules.users.routes import users_bp
#         from app.modules.users.resident.routes import resident_bp
#         self.app.register_blueprint(users_bp, url_prefix='/users')
#         self.app.register_blueprint(resident_bp, url_prefix='/resident')

#         # Add mock data
#         self.db['Sensor_Data'].insert_many([
#             {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
#             {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
#         ])

#         # Assign mock DB to blueprint
#         resident_bp.sensors_collection = self.db['Sensor_Data']

#     def login(self, username, password):
#         return self.client.post('/users/login', data=dict(
#             username=username,
#             password=password
#         ), follow_redirects=True)

#     def test_login(self):
#         response = self.login('test_resident', 'test_password')
#         assert response.status_code == 200

#     def test_monthly_snapshot(self):
#         response = self.login('test_resident', 'test_password')
#         assert response.status_code == 200
#         with self.client.session_transaction() as sess:
#             sess['username'] = 'test_resident'
#         response = self.client.get('/resident/monthly_snapshot?month=7')
#         assert response.status_code == 200
#         assert b"Building Sensor Data Summary" in response.data
#         assert b"Average Temperature" in response.data
#         assert b"27.0" in response.data  # Check if the average temperature is correct
#         assert b"0.006" in response.data  # Check if the average vibration is correct

#     def test_process_sensor_data(self):
#         from app.modules.users.resident.routes import process_sensor_data

#         sensor_data = [
#             {'Temperature': 26.0, 'Vibration SD': 0.005, 'sample_time_utc': '2024-07-05T12:00:00.000Z'},
#             {'Temperature': 28.0, 'Vibration SD': 0.007, 'sample_time_utc': '2024-07-15T12:00:00.000Z'}
#         ]
#         snapshot = process_sensor_data(sensor_data)
#         self.assertEqual(snapshot['average_temperature'], 27.0)
#         self.assertEqual(snapshot['average_vibration'], 0.006)
#         self.assertEqual(len(snapshot['alerts']), 0)

# if __name__ == "__main__":
#     pytest.main()
