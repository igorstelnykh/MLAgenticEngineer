import json
import os
import psycopg2
from datetime import datetime
import logging

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
    Lambda handler: connects to DB, fetches alerts, and returns them
    """
    logger.info("GetAlertsFunction invoked")

    try:
        # get DB connection
        conn = get_db_connection()
        cur = conn.cursor()

        # query DB
        query = 'SELECT user_id, stress_score, "timestamp" FROM high_stress_users ORDER BY "timestamp" DESC;'
        cur.execute(query)
        db_alerts = cur.fetchall()
        cur.close()

        # convert to json
        alerts_list = []
        for alert in db_alerts:
            user_id = alert[0]
            stress_score = int(alert[1])/100
            timestamp = alert[2].strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            alerts_list.append({
                "user_id": user_id,
                "stress_score": stress_score,
                "timestamp": timestamp
            })
        logger.info(f"Successfully fetched {(len(alerts_list))} alerts")

        # format return for API gateway
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(alerts_list, sort_keys=False)
        }
    except Exception as e:
        # return internal server error
        logger.error(f"Error occured: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "An internal server error occurred"}),
        }
