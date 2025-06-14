import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd
from datetime import datetime


# mock a DB url
with patch.dict('os.environ', {'DATABASE_URL': 'sample_db_url'}):
    from lambda_functions.run_agent import app as run_agent_app

class TestRunAgent(unittest.TestCase):

    @patch('lambda_functions.run_agent.app.psycopg2')
    @patch('lambda_functions.run_agent.app.pd.read_csv')
    def test_run_agent_handler_success(self, mock_read_csv, mock_db):
        """
        Tests successful exection for run_agent lambda_handler
        """
        # mock csv data
        mock_data = {
            'timestamp': [datetime(2025, 6, 13, 12, 0, 0)],
            'stress_level': [run_agent_app.STRESS_THRESHOLD + 10]
        }
        mock_read_csv.return_value = pd.DataFrame(mock_data)

        # mock DB connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # call lambda handler
        event = {'filepath': 'sample_data.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check all required csv reader and DB functions were called
        mock_read_csv.assert_called_once_with('sample_data.csv')
        mock_db.connect.assert_called_once_with('sample_db_url')
        mock_conn.cursor.assert_called_once()
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()

        # check response status
        self.assertEqual(lambda_response['statusCode'], 200)
    
    @patch('lambda_functions.run_agent.app.psycopg2')
    @patch('lambda_functions.run_agent.app.pd.read_csv')
    def test_run_agent_handler_no_students_flagged(self, mock_read_csv, mock_db):
        """
        Tests run_agent lambda_handler when no stress levels are above the threshold
        """
        # mock csv data
        mock_data = {
            'timestamp': [datetime(2025, 6, 13, 12, 0, 0)],
            'stress_level': [run_agent_app.STRESS_THRESHOLD - 10]
        }
        mock_read_csv.return_value = pd.DataFrame(mock_data)
        
        # call lambda handler
        event = {'filepath': 'sample_data.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check 200 response and that DB was not called
        self.assertEqual(lambda_response['statusCode'], 200)
        mock_db.connect.assert_not_called()
    
    @patch('lambda_functions.run_agent.app.pd.read_csv')
    def test_run_agent_handler_missing_required_column(self, mock_read_csv):
        """
        Tests run_agent lambda_handler when CSV is missing timestamp or stress_level column
        """
        mock_data = {
            'timestamp': [datetime(2025, 6, 13, 12, 0, 0)], 
            'sample_column': [111]
        }
        mock_read_csv.return_value = pd.DataFrame(mock_data)

        # call lambda handler
        event = {'filepath': 'sample_data.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check 400 response
        self.assertEqual(lambda_response['statusCode'], 400)
    
    @patch('lambda_functions.run_agent.app.psycopg2')
    @patch('lambda_functions.run_agent.app.pd.read_csv')
    def test_run_agent_handler_malformed_data(self, mock_read_csv, mock_db):
        """
        Tests run_agent lambda_handler when malformed data is present
        """
        # mock csv data
        mock_data = {
            'timestamp': [datetime(2025, 6, 13, 12, 0, 0), datetime(2025, 6, 13, 12, 1, 0)],
            'stress_level': [run_agent_app.STRESS_THRESHOLD + 10, 'N/A']
        }
        mock_read_csv.return_value = pd.DataFrame(mock_data)

        # mock DB connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # call lambda handler
        event = {'filepath': 'sample_data.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check that db execute was only called once since there should only be 1 write
        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

        # check response status
        self.assertEqual(lambda_response['statusCode'], 200)


    
    @patch('lambda_functions.run_agent.app.pd.read_csv')
    def test_run_agent_handler_file_not_found(self, mock_read_csv):
        """
        Tests run_agent lambda_handler when input file was not found
        """
        # mock csv
        mock_read_csv.side_effect = FileNotFoundError

        # call lambda handler
        event = {'filepath': 'invalid.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check that 404 response is returned
        self.assertEqual(lambda_response['statusCode'], 404)
    
    def test_run_agent_handler_incomplete_event(self):
        """
        Tests run_agent lambda_handler when event is missing a filepath
        """
        # call lambda handler
        lambda_response = run_agent_app.lambda_handler({}, {})

        # check that 400 response is returned
        self.assertEqual(lambda_response['statusCode'], 400)

    @patch('lambda_functions.run_agent.app.pd.read_csv')
    @patch('lambda_functions.run_agent.app.psycopg2')
    def test_run_agent_handler_db_error(self, mock_db, mock_read_csv):
        """
        Tests run_agent lambda_handler when DB connection fails
        """
        # mock csv data
        mock_data = {
            'timestamp': [datetime(2025, 6, 13, 12, 0, 0)],
            'stress_level': [run_agent_app.STRESS_THRESHOLD + 10]
        }
        mock_read_csv.return_value = pd.DataFrame(mock_data)

        # mock connection failure
        mock_db.connect.side_effect = Exception("DB connection failed")

        # call lambda handler
        event = {'filepath': 'sample_data.csv'}
        lambda_response = run_agent_app.lambda_handler(event, {})

        # check that 500 response is returned
        self.assertEqual(lambda_response['statusCode'], 500)