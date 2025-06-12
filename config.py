"""Configs"""

class Config:
    # Database config
    # format: postgresql://<user>:<password>@<host>:<post>/<dbname>
    DB_URL = "postgresql://postgres:example@localhost:5432/stress_alerts"


class TestConfig(Config):
    # Testing condfig
    TESTING = True

    