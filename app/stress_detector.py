import pandas as pd
import psycopg2
from app import db
import logging


def run_agent(filepath: str):
    """
    Core agent logic for reading data from csv and classifying it
    Args:
        filepath (str): path to csv file for data
    
    Returns:
        ...
    """
    logging.info("Agent running")

    # get data from file into dataframe
    try:
        logging.info(f"Reading from {filepath}")
        df = pd.read_csv(filepath, parse_dates=['timestamp'])
        logging.info(f"Successfully read {len(df)} records from {filepath}")
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return
    except Exception as e:
        logging.error(f"Error while reading {filepath}: {e}")
        return
    
    # get rows from df that are above threshold
    STRESS_THRESHOLD = 70
    high_stress_df = df[df['stress_level'] > STRESS_THRESHOLD].copy()

    # no data was found
    if high_stress_df.empty:
        logging.info(f"No high stress students were found from data in {filepath}")
        logging.info("Agent run finished")
        return
    
    # generate user IDs based on index
    high_stress_df['user_id'] = [f"user_{i}" for i in high_stress_df.index]
    
    # store flagged users in DB
    logging.info(f"Flagged {len(high_stress_df)} students as high stress")
    conn = None
    try:
        conn = db.get_db()
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
    
    except (Exception, psycopg2.DatabaseError) as e:
        logging.error(f"Error while writing to DB: {e}")
        if conn:    # revert transaction
            conn.rollback()
    finally:
        logging.info("Agent run finished")

