import yaml
import os

POSTGRES_USER = os.environ.get("POSTGRES_USER", "nothing")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "nothing")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "nothing")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "nothing")


def get_db_url(db_key: str = "db_production") -> str:
    """
    Get url to connect to the database from the configuration file.
    """
    dialect = "postgresql+psycopg2"
    host = POSTGRES_HOST
    port = "5432"
    database = POSTGRES_DB
    username = POSTGRES_USER
    password = POSTGRES_PASSWORD

    return f"{dialect}://{username}:{password}@{host}:{port}/{database}"
