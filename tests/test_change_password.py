import unittest
from flask import Flask
from flask_testing import TestCase
import pymongo
from app.modules.users.models import User
from app.main_cover import create_app

class TestChangePassword(TestCase):
    
    def create_app(self):
        # Create the Flask app instance
        return create_app('testing')

    def setUp(self):
        # Setup before each test
        self.client = self.app.test_client()
        self.db = self.app.db  # Assuming db is attached to the app instance
        self.user_collection = self.db['users']
        
        # Insert a test user
        self.user_collection.insert_one({
            "username": "testuser",
            "password": "oldpassword",
            "email": "testuser@example.com"
        })

    def tearDown(self):
        # Cleanup after each test
        self.user_collection.delete_many({})

    def test_successful_password_change(self):
        response = self.client.post('/users/change_password', data={
            'email': 'testuser@example.com',
            'username': 'testuser',
            'old_password': 'oldpassword',
            'new_password': 'newpassword'
        })
        self.assert200(response)
        self.assertIn(b'Password successfully updated', response.data)

    def test_invalid_username_password(self):
        response = self.client.post('/users/change_password', data={
            'email': 'testuser@example.com',
            'username': 'testuser',
            'old_password': 'wrongpassword',
            'new_password': 'newpassword'
        })
        self.assert200(response)
        self.assertIn(b'Invalid username, email or password', response.data)

    def test_empty_fields(self):
        response = self.client.post('/users/change_password', data={
            'email': '',
            'username': 'testuser',
            'old_password': 'oldpassword',
            'new_password': 'newpassword'
        })
        self.assert200(response)
        self.assertIn(b'All fields are required', response.data)

    def test_password_validation(self):
        response = self.client.post('/users/change_password', data={
            'email': 'testuser@example.com',
            'username': 'testuser',
            'old_password': 'oldpassword',
            'new_password': 'short'
        })
        self.assert200(response)
        self.assertIn(b'New password does not meet criteria', response.data)

if __name__ == '__main__':
    unittest.main()
