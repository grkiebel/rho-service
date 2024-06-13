import os
from sqlmodel import SQLModel, Session, create_engine
from db_config import get_db_url
import db_models  # do not remove this import


class DB_ITEM_NOT_FOUND(Exception):
    pass


class DB_ITEM_ALREADY_EXISTS(Exception):
    pass


class DB_ITEM_REFERENCED(Exception):
    pass


class DB_WRONG_STATUS(Exception):
    pass


engine = None


def create_engine_and_tables():
    if not engine:
        url = get_db_url()
        globals()["engine"] = create_engine(url)
        SQLModel.metadata.create_all(engine)


# Dependency to get the database session
def get_db():
    create_engine_and_tables()
    database = Session(engine)
    try:
        yield database
    finally:
        database.close()
