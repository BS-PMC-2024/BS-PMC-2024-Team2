import os
import unittest
from flask import Flask
from flask_testing import TestCase
from app.main_cover import create_app, client, db

class TestChangePassword(TestCase):
    def create_app(self):
        # Create the Flask app instance
        return create_app('testing')

    def setUp(self):
        # Set up any initial state for the tests
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.db = db

        # Insert test data into the database
        self.db.users.insert_many([
            {"username": "testuser1", "email": "test1@example.com", "password": "password1"},
            {"username": "testuser2", "email": "test2@example.com", "password": "password2"}
        ])

    def tearDown(self):
        # Clean up any test data in the database
        self.db.users.delete_many({})

    def test_empty_fields(self):
        response = self.client.post('/change-password', data={
            'username': '',
            'email': '',
            'old_password': '',
            'new_password': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'All fields are required', response.data)

    def test_invalid_username_password(self):
        response = self.client.post('/change-password', data={
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'old_password': 'wrongpassword',
            'new_password': 'newpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid username or password', response.data)

    def test_password_validation(self):
        response = self.client.post('/change-password', data={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'old_password': 'password1',
            'new_password': 'short'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Password must be at least 8 characters long', response.data)

    def test_successful_password_change(self):
        response = self.client.post('/change-password', data={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'old_password': 'password1',
            'new_password': 'newpassword1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password successfully changed', response.data)

if __name__ == '__main__':
    unittest.main()
