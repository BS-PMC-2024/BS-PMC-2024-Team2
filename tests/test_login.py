import unittest
from flask import Flask
from app.modules.users.routes import users_bp, client
import mongomock
import os

class UsersRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.mongo_client = mongomock.MongoClient()
        self.db = self.mongo_client['Cover']

        self.app.register_blueprint(users_bp, url_prefix='/users')

        # Add mock data
        with self.app.app_context():
            self.db['Users'].insert_one({
                "username": "test_engineer",
                "password": "test_password"
            })
            users_bp.db = self.db

    def tearDown(self):
        """Tear down the test environment after each test."""
        with self.app.app_context():
            self.db['Users'].delete_many({})

    def login(self, username, password):
        return self.client.post('/users/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_login_success(self):
        """Test successful login."""
        response = self.login('test_engineer', 'test_password')
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        """Test failed login due to incorrect password."""
        response = self.login('test_engineer', 'wrong_password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

if __name__ == '__main__':
    unittest.main()
