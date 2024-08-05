import unittest
import pytest
import pymongo
from flask import Flask, session, url_for
import os
import mongomock
import sys


class TestEngineerRoutes (unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.mongo_client = mongomock.MongoClient()
        self.db_Cover = self.mongo_client['Cover']
        self.db_Data = self.mongo_client['Data']
        
        from app.modules.users.routes import users_bp
        from app.modules.users.engineer.routes import engineer_bp
        self.app.register_blueprint(users_bp, url_prefix='/users')
        self.app.register_blueprint(engineer_bp, url_prefix='/engineer')

        # Add mock data
        self.db_Cover['Residents'].insert_one({
            "username": "test_engineer",
            "password": "test_password"
        })
        self.db_Data['Sensor_Data'].insert_many([
            {'_id': 1, 'Temperature': 25.0, 'Vibration SD': 0.01, 'sample_time_utc': '2024-07-07T10:46:29.000Z'},
            {'_id': 2, 'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': '2024-07-07T11:46:29.000Z'}
        ])

        # Assign mock DBs to blueprints
        users_bp.db = self.db_Cover
        engineer_bp.sensors_collection = self.db_Data['Sensor_Data']

    def login(self, username, password):
        return self.client.post('/users/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_login(self):
        self.setUp()
        response = self.login('test_engineer', 'test_password')
        assert response.status_code == 200

    def test_preview_export(self):
        self.setUp()
        response = self.login('test_engineer', 'test_password')
        assert response.status_code == 200
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_engineer'
        response = self.client.get('/engineer/preview_export')
        assert response.status_code == 302
        # assert b'Building Sensor Data Preview' in response.data

    def test_export(self):
        self.setUp()
        response = self.login('test_engineer', 'test_password')
        assert response.status_code == 200
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_engineer'
        response = self.client.get('/engineer/export')
        assert response.status_code == 302

if __name__ == "__main__":
    pytest.main()
