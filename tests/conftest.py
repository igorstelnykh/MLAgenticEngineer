import pytest
from app import create_app
from app.db import get_db
from config import TestConfig


@pytest.fixture
def app():
    """
    Creates new app instance for each integration test
    """
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    """
    Creates a test client for the app
    """
    return app.test_client()

@pytest.fixture
def db_init(app):
    """
    Initializes the database for a test with clean table and sample entries
    """
    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # create clean table in local DB
        with open('db/init.sql', 'r') as f:
            cur.execute(f.read())

        # sample data
        query = """
                INSERT INTO high_stress_users (user_id, stress_score, "timestamp")
                VALUES (%s, %s, %s), (%s, %s, %s);
                """
        cur.execute(query, ('test_user_1', 85.0, '2025-06-11T12:00:00Z', 'test_user_2', 75.0, '2025-06-11T13:00:00Z'))
        db.commit()
        cur.close()

    yield

    # clean up DB after testing
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("DROP TABLE IF EXISTS high_stress_users;")
        db.commit()
        cur.close()