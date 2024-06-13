from db_base import (
    DB_ITEM_NOT_FOUND,
    DB_ITEM_ALREADY_EXISTS,
    DB_ITEM_REFERENCED,
    DB_WRONG_STATUS,
)
from fastapi import HTTPException


def handle_db_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DB_ITEM_NOT_FOUND as e:
            raise HTTPException(status_code=404, detail=str(e))
        except DB_ITEM_ALREADY_EXISTS as e:
            raise HTTPException(status_code=409, detail=str(e))
        except DB_ITEM_REFERENCED as e:
            raise HTTPException(status_code=409, detail=str(e))
        except DB_WRONG_STATUS as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper
