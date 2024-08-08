import unittest
from flask import Flask, session, make_response
import os

class CacheControlTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
        self.app.secret_key = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        @self.app.route('/logout')
        def logout():
            session.clear()
            response = make_response("Logged out", 200)
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response

        @self.app.route('/')
        def home():
            return "Home Page"

    def test_no_cache_after_logout(self):
        with self.app.test_client() as client:
            # Call logout and check response headers
            logout_response = client.get('/logout')
            self.assertIn('Cache-Control', logout_response.headers)
            self.assertIn('no-store', logout_response.headers['Cache-Control'])
            self.assertEqual(logout_response.headers['Pragma'], 'no-cache')
            self.assertEqual(logout_response.headers['Expires'], '0')

            # Verify headers after visiting the home page
            home_response = client.get('/')
            self.assertNotIn('Cache-Control', home_response.headers)

    def test_cache_control_headers(self):
        with self.app.test_client() as client:
            response = client.get('/logout')
            self.assertEqual(response.headers['Cache-Control'], 'no-store, no-cache, must-revalidate, max-age=0')
            self.assertEqual(response.headers['Pragma'], 'no-cache')
            self.assertEqual(response.headers['Expires'], '0')

if __name__ == '__main__':
    unittest.main()
