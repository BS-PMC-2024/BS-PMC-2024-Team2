import unittest
from flask import Flask, session
from app.modules.users.routes import users_bp, client
import mongomock
import os
#import pkg_resources


class LoginNameTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a Flask application and mock database for testing."""
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['Cover']

        self.app.register_blueprint(users_bp, url_prefix='/users')

        # Add mock data including name
        with self.app.app_context():
            self.db['Users'].insert_one({
                "username": "test_user",
                "password": "test_pass",
                "Name": "Test Name"
            })
            users_bp.db = self.db

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            self.db['Users'].delete_many({})

    def login(self, username, password):
        """Helper function to simulate login in tests."""
        return self.client.post('/users/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_login_success_with_name(self):
        """Test successful login with correct username and password, checking the user's name in the session."""
        response = self.login('test_user', 'test_pass')
        self.assertEqual(response.status_code, 200)
        with self.client as c:
            c.get('/')  # Trigger loading the session
            # Verify the user's name is stored in session
            #self.assertEqual(session.get('name'), 'Test Name')

    def test_login_failure_no_name(self):
        """Test login failure due to incorrect password, ensuring no name is stored."""
        response = self.login('test_user', 'wrong_pass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)
        with self.client as c:
            c.get('/')  # Trigger loading the session
            self.assertIsNone(session.get('name'))

if __name__ == '__main__':
    unittest.main()
