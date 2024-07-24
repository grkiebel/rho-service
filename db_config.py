import yaml
import os

POSTGRES_USER = os.environ.get("POSTGRES_USER", "nothing")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "nothing")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "nothing")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")


def get_db_url(db_key: str = "db_production") -> str:
    """
    Get url to connect to the database from the configuration file.
    """
    dialect = "postgresql+psycopg2"
    host = POSTGRES_HOST
    port = POSTGRES_PORT
    database = POSTGRES_DB
    username = POSTGRES_USER
    password = POSTGRES_PASSWORD

    database_url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"
    print(f"Database URL: {database_url}")
    return database_url
