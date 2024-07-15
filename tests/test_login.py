# tests/test_login.py

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from Cover import create_app

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.app, self.db = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Tear down the test environment after each test."""
        self.app_context.pop()

    @patch('app.modules.users.routes.db')
    def test_login_success(self, mock_db):
        """Test successful login."""
        # Mock the database operations
        mock_db.users.find_one.return_value = {'username': 'testuser', 'password': 'testpassword'}

        # Log in the user
        response = self.client.post('/users/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, testuser', response.data)

    @patch('app.modules.users.routes.db')
    def test_login_failure(self, mock_db):
        """Test failed login due to incorrect password."""
        # Mock the database operations
        mock_db.users.find_one.return_value = {'username': 'testuser', 'password': 'testpassword'}

        # Attempt to log in with incorrect password
        response = self.client.post('/users/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

if __name__ == '__main__':
    unittest.main()
