import unittest
from unittest.mock import patch, MagicMock, call
import unittest.mock
import pandas as pd
from app import stress_detector
from app.stress_detector import STRESS_THRESHOLD


class TestStressDetectorAgent(unittest.TestCase):
    """
    Unit tests for functions in stress_detector.py
    """

    @patch('app.stress_detector.db')
    @patch('app.stress_detector.pd.read_csv')
    def test_run_agent_valid_data(self, mock_read_csv, mock_db):
        """
        Tests that run agent function parses students with stress levels > threshold and adds to DB
        """
        # mock csv reads
        mock_csv_path = 'test.csv'
        mock_data = {
            'timestamp': pd.to_datetime(['2024-05-03 23:15:00', '2024-05-04 00:00:00', '2024-05-05 05:15:00']),
            'stress_level': [STRESS_THRESHOLD - 10, STRESS_THRESHOLD + 1, STRESS_THRESHOLD + 10]
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_csv.return_value = mock_df

        # mock db connection and cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # run agent
        stress_detector.run_agent(mock_csv_path)

        # check calls to mocked functions/objects
        mock_read_csv.assert_called_once_with(mock_csv_path, parse_dates=['timestamp'])
        mock_db.get_db.assert_called_once()
        mock_conn.cursor.assert_called_once()

        # check expected calls, args, and returns
        expected_user_id_1 = f"user_{mock_df.index[1]}"
        expected_user_id_2 = f"user_{mock_df.index[2]}"

        # expected SQL queries
        expected_calls = [
            call.execute(unittest.mock.ANY, (expected_user_id_1, STRESS_THRESHOLD + 1, pd.Timestamp('2024-05-04 00:00:00'))),
            call.execute(unittest.mock.ANY, (expected_user_id_2, STRESS_THRESHOLD + 10, pd.Timestamp('2024-05-05 05:15:00'))),
        ]
        mock_cur.assert_has_calls(expected_calls, any_order=True)
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
    
    @patch('app.stress_detector.db')
    @patch('app.stress_detector.pd.read_csv')
    def test_run_agent_malformed_data(self, mock_read_csv, mock_db):
        """
        Tests that run agent function removes malformed data before parsing for high stress students
        """
        # mock csv reads
        mock_csv_path = 'test.csv'
        mock_data = {
            'timestamp': ['2025-06-11 10:00:00', 'malformed timestamp', '2025-06-11 12:00:00', '2025-06-11 13:00:00'],
            'stress_level': [STRESS_THRESHOLD - 10, STRESS_THRESHOLD + 1, 'N/A', STRESS_THRESHOLD + 10]
        }
        mock_df = pd.DataFrame(mock_data)
        mock_df['timestamp'] = pd.to_datetime(mock_df['timestamp'], errors='coerce')
        mock_read_csv.return_value = mock_df

        # mock db connection and cursor
        # mock db connection and cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # run agent
        stress_detector.run_agent(mock_csv_path)

        # check that only 1 record was inserted to DB(2 are invalid)
        self.assertEqual(mock_cur.execute.call_count, 1)

        # check that data was still commited to db and db connection was closed
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
    
    @patch('app.stress_detector.db')
    @patch('app.stress_detector.pd.read_csv')
    def test_run_agent_no_students_flagged(self, mock_read_csv, mock_db):
        """
        Tests that run agent function doesn't flag any students if there are non above threshold
        """
        # mock csv reads
        mock_csv_path = 'test.csv'
        mock_data = {
            'timestamp': pd.to_datetime(['2024-05-03 23:15:00', '2024-05-04 00:00:00', '2024-05-05 05:15:00']),
            'stress_level': [STRESS_THRESHOLD - 10, STRESS_THRESHOLD - 1, STRESS_THRESHOLD]
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_csv.return_value = mock_df

        # run agent
        stress_detector.run_agent(mock_csv_path)

        # check that DB functions were never called since there is no data to be added
        mock_db.get_db.assert_not_called()
    
    @patch('app.stress_detector.logging')
    @patch('app.stress_detector.pd.read_csv')
    def test_run_agent_file_not_found(self, mock_read_csv, mock_logging):
        """
        Tests that run agent function logs the error and returns if csv file wasn't found
        """
        # mock csv reads
        mock_csv_path = 'invalid.csv'
        mock_read_csv.side_effect = FileNotFoundError

        # run agent
        stress_detector.run_agent(mock_csv_path)

        # check that correct error was logged
        mock_logging.error.assert_called_with(f"File not found: {mock_csv_path}")
    
    @patch('app.stress_detector.db')
    @patch('app.stress_detector.pd.read_csv')
    def test_run_agent_db_error(self,  mock_read_csv, mock_db):
        """
        Tests that run agent function catches a generic db connection error
        """
        # mock csv reads
        mock_csv_path = 'test.csv'
        mock_data = {
            'timestamp': pd.to_datetime(['2024-05-03 23:15:00', '2024-05-04 00:00:00', '2024-05-05 05:15:00']),
            'stress_level': [STRESS_THRESHOLD - 10, STRESS_THRESHOLD + 1, STRESS_THRESHOLD + 10]
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_csv.return_value = mock_df
        
        # mock get_db to raise a generic error
        mock_db.get_db.side_effect = Exception("DB connection failed")
        mock_conn = MagicMock()

        # run agent
        stress_detector.run_agent(mock_csv_path)

        # check that db connection was attempted and failed and commit was never attempted
        mock_db.get_db.assert_called_once()
        mock_conn.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()