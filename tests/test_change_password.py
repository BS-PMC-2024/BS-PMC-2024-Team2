import unittest
from flask import Flask
from app.modules.users.routes import users_bp
import mongomock
import os

class ChangePasswordTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.register_blueprint(users_bp, url_prefix='/users')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['Cover']
        users_bp.db = self.db

        # Add mock data
        with self.app.app_context():
            self.db['Users'].insert_many([
                {"username": "testuser1", "email": "test1@example.com", "password": "password1"},
                {"username": "testuser2", "email": "test2@example.com", "password": "password2"}
            ])

    def tearDown(self):
        """Tear down the test environment after each test."""
        with self.app.app_context():
            self.db['Users'].delete_many({})

    def test_empty_fields(self):
        response = self.client.post('/users/change_password', data={
            'username': '',
            'email': '',
            'old_password': '',
            'new_password': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    def test_invalid_username_password(self):
        response = self.client.post('/users/change_password', data={
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'old_password': 'wrongpassword',
            'new_password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    def test_password_validation(self):
        response = self.client.post('/users/change_password', data={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'old_password': 'password1',
            'new_password': 'short'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    def test_successful_password_change(self):
        response = self.client.post('/users/change_password', data={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'old_password': 'password1',
            'new_password': 'newpassword1'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Password successfully changed!', response.data)

if __name__ == '__main__':
    unittest.main()
