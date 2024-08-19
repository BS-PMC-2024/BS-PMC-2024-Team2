import unittest
from unittest.mock import patch
from datetime import datetime
from app.modules.users.resident.routes import detect_anomalies_and_send_alerts, sensors_collection

class TestResidentRoutes(unittest.TestCase):

    def setUp(self):
        # Set up the in-memory MongoDB using mongomock or real MongoDB if necessary
        today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        sensors_collection.insert_many([
            {'Temperature': 29.0, 'Vibration SD': 0.01, 'sample_time_utc': today},
            {'Temperature': 26.0, 'Vibration SD': 0.02, 'sample_time_utc': today}
        ])

    @patch('app.modules.users.resident.routes.send_alert_emails_to_residents')
    def test_anomalies_detection_and_alert_sending(self, mock_send_alert_emails):
        # Call the function to test
        result = detect_anomalies_and_send_alerts()

        # Print the result and any anomalies for debugging
        print("Test result:", result)
        anomalies = sensors_collection.find({
            'sample_time_utc': {'$regex': f'^{datetime.utcnow().strftime("%Y-%m-%d")}'}
        })
        print("Anomalies found:", list(anomalies))

        # Check that the function returned True
        self.assertTrue(result)

        # Check that the email sending function was called once
        mock_send_alert_emails.assert_called_once()

    def test_no_anomalies_no_email_sent(self):
        # Assuming you have no anomalies inserted, the function should return False
        sensors_collection.delete_many({})  # Clearing out the test data
        result = detect_anomalies_and_send_alerts()
        self.assertFalse(result)

    def test_no_data_for_today(self):
        # If there is no data for today, the function should return False
        sensors_collection.delete_many({})  # Clearing out the test data

        with patch('app.modules.users.resident.routes.send_alert_emails_to_residents') as mock_send_alert_emails:
            result = detect_anomalies_and_send_alerts()
            self.assertFalse(result)
            mock_send_alert_emails.assert_not_called()

if __name__ == "__main__":
    unittest.main()
