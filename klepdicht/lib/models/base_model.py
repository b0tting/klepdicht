import sqlite3
from pathlib import Path


class BaseModel:
    def __init__(self, db):
        db_path = Path(db)
        if not db_path.exists():
            raise FileNotFoundError(f"Database file {db} does not exist")
        self.dbpath = db_path

    def get_cursor(self):
        connection = sqlite3.connect(self.dbpath)
        cursor = connection.cursor()
        cursor.row_factory = sqlite3.Row
        return cursor
