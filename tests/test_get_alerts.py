import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime


# mock a DB url
with patch.dict('os.environ', {'DATABASE_URL': 'sample_db_url'}):
    from lambda_functions.get_alerts import app as get_alerts_app

class TestGetAlerts(unittest.TestCase):

    @patch('lambda_functions.get_alerts.app.psycopg2')
    def test_get_alerts_handler_success(self, mock_db):
        """
        Tests successful exection for get_alerts lambda_handler
        """
        # mock db data
        mock_db_data = [('user_1', 80.0, datetime(2025, 6, 13, 12, 0, 0))]

        # mock DB connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = mock_db_data

        # call lambda handler
        lambda_response = get_alerts_app.lambda_handler({}, {})

        # check that DB was called
        mock_db.connect.assert_called_once_with('sample_db_url')
        mock_conn.cursor.assert_called_once()
        query = 'SELECT user_id, stress_score, "timestamp" FROM high_stress_users ORDER BY "timestamp" DESC;'
        mock_cur.execute.assert_called_once_with(query)

        # check response status
        self.assertEqual(lambda_response['statusCode'], 200)
        self.assertEqual(lambda_response['headers']['Content-Type'], 'application/json')

        # check response body
        body = json.loads(lambda_response['body'])
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['user_id'], 'user_1')
        self.assertEqual(body[0]['stress_score'], 0.8)
        self.assertEqual(body[0]['timestamp'], '2025-06-13T12:00:00Z')
    
    @patch('lambda_functions.get_alerts.app.psycopg2')
    def test_get_alerts_handler_db_fail(self, mock_db):
        """
        Tests that hander returns internal server error(500) if the db connection fails
        """
        # mock connection failure
        mock_db.connect.side_effect = Exception("DB connection failed")

        # call lambda handler
        lambda_response = get_alerts_app.lambda_handler({}, {})

        # check response status and error message presense
        self.assertEqual(lambda_response['statusCode'], 500)
        body = json.loads(lambda_response['body'])
        self.assertIn('error', body)
