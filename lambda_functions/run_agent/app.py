import json
import os
import logging
import psycopg2
import pandas as pd


STRESS_THRESHOLD = 70

# logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# DB connection
DB_URL = os.environ.get("DATABASE_URL")
_db_connection = None

def get_db_connection():
    """
    Singleton DB connection, creates a connection if one doesn't exist
    """
    global _db_connection
    if not _db_connection or _db_connection.closed:
        try:
            _db_connection = psycopg2.connect(DB_URL)
            logger.info("Successfully connected to DB")
        except psycopg2.OperationalError as e:
            logger.error(f"Error connecting to DB: {e}")
            raise
    return _db_connection

def lambda_handler(event, context):
    """
    Lambda handler: processes CSV file, flags high-stress users using heuritic rule, writes them to DB
    """
    logging.info("RunAgentFunction invoked")

    # get CSV path from event
    filepath = event.get('filepath')
    if not filepath:
        logger.error("Error: 'filepath' missing from event")
        return  {
            "statusCode": 400,
            "body": json.dumps({"error": "'filepath' missing"})
        }
    
    # process data from csv
    try:
        # read data into dataframe
        logger.info(f"Reading from {filepath}")
        df = pd.read_csv(filepath)
        logging.info(f"Successfully read {len(df)} records from {filepath}")

        # check that required columns(stress_level and timestamp) are present in csv
        required_cols = {'timestamp', 'stress_level'}
        if not required_cols.issubset(df.columns):
            logger.error(f"Error: {filepath} is missing one of the required columns {required_cols}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"{filepath} is missing one of the required columns {required_cols}"})
            }

        # clean and log malformed data
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['stress_level'] = pd.to_numeric(df['stress_level'], errors='coerce')
        malformed_rows = df[df['stress_level'].isnull() | df['timestamp'].isnull()]

        if not malformed_rows.empty:
            logging.warning(f"Found {len(malformed_rows)} malformed rows in {filepath}, skipping")
            for idx, row in malformed_rows.iterrows():
                logging.debug(f"Skipping malformed row at index {idx}: {row.to_dict()}")
        df.dropna(subset=['stress_level', 'timestamp'], inplace=True)
    
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return  {
            "statusCode": 404,
            "body": json.dumps({"error": f"file not found in {filepath}"})
        }
    except Exception as e:
        logging.error(f"Error while reading {filepath}: {e}")
        return  {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to process file in {filepath}"})
        }

    # get rows from df that are above threshold
    high_stress_df = df[df['stress_level'] > STRESS_THRESHOLD].copy()

    # no data was found
    if high_stress_df.empty:
        logging.info(f"No high stress students were found from data in {filepath}")
        return  {
            "statusCode": 200,
            "body": json.dumps({"message": "Agent run finished. No high-stress students were found"})
        }
    
    # generate user IDs based on index
    high_stress_df['user_id'] = [f"user_{i}" for i in high_stress_df.index]

    # store flagged users in DB
    logging.info(f"Flagged {len(high_stress_df)} students as high stress")
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Adding flagged users to DB")

        for idx, student in high_stress_df.iterrows():
            user_id = student['user_id']
            stress_score = student['stress_level']
            timestamp = student['timestamp']
            query = """
                    INSERT INTO high_stress_users (user_id, stress_score, "timestamp") VALUES (%s, %s, %s);
                    """
            cur.execute(query, (user_id, stress_score, timestamp))
        
        conn.commit()
        cur.close()
        logging.info(f"Inserted {len(high_stress_df)} alerts into DB")
        return  {
            "statusCode": 200,
            "body": json.dumps({"message": f"Agent run finished. Added {len(high_stress_df)} users to DB"})
        }
    
    except Exception as e:
        logging.error(f"Error while writing to DB: {e}")
        if conn:    # revert transaction
            conn.rollback()
        return  {
            "statusCode": 500,
            "body": json.dumps({"error": "error writing to DB"})
        }
