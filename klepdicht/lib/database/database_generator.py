import sqlite3
import uuid
from pathlib import Path

import yaml


class KlepDichtDatabaseGenerator:
    def __init__(self, database_file, overwrite=False, initial_data=False):
        self.database_file = Path(database_file)
        self.create_initial_data = initial_data
        self.database_overwrite = overwrite
        self.prepare_file_location()
        self.conn = sqlite3.connect(self.database_file)
        self.room_cache = {}

    def generate_database(self):
        self.create_table_rooms()
        self.create_table_users()
        self.create_user_room_link()
        self.create_table_messages()
        self.create_table_settings()

    def create_table_rooms(self):
        create_statement = """
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            uuid TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP);
        """
        self.__execute_transaction_statement(create_statement)
        print("✅ Rooms table created")

    def create_table_users(self):
        create_statement = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL,
            username TEXT NOT NULL,
            cryptoname TEXT NOT NULL,
            password TEXT NOT NULL,
            color TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP);
        """
        self.__execute_transaction_statement(create_statement)
        print("✅ Users table created")

    def create_table_messages(self):
        create_statement = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id));
        """
        self.__execute_transaction_statement(create_statement)
        print("✅ Messages table created")

    def create_user_room_link(self):
        create_statement = """
        CREATE TABLE IF NOT EXISTS user_room_link (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id));
        """
        self.__execute_transaction_statement(create_statement)
        print("✅ User room link table created")

    def create_table_settings(self):
        create_statement = """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP);
        """
        self.__execute_transaction_statement(create_statement)
        print("✅ Settings table created")

    def __execute_transaction_statement(self, create_statement, parameters=()):
        c = self.conn.cursor()
        try:
            c.execute(create_statement, parameters)
        except Exception as e:
            print(f"Failed at query: {create_statement}")
            print(e)
        self.conn.commit()
        return c.lastrowid

    def __execute_query(self, query, parameters=()):
        c = self.conn.cursor()
        c.row_factory = sqlite3.Row
        c.execute(query, parameters)
        return c.fetchall()

    def load(self, setup_file):
        with open(setup_file, "r") as f:
            setup = yaml.safe_load(f)
            self.load_settings(setup["settings"])
            self.load_users(setup["users"])

    def load_settings(self, settings):
        for setting in settings:
            self.__execute_transaction_statement(
                "INSERT INTO settings (name, value) VALUES (?, ?)",
                (setting, settings[setting]),
            )
        print("✅ Settings loaded")

    def load_users(self, users):
        for user in users:
            user_id = self.__execute_transaction_statement(
                "INSERT INTO users (uuid, username, cryptoname, password, color) VALUES (?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    user["name"],
                    user["name"],  # Heb geen zin meer in een cryptoname
                    user["password"],
                    user["color"],
                ),
            )
            for room in user["rooms"]:
                if room in self.room_cache:
                    room_id = self.room_cache[room]
                else:
                    room_id = self.__execute_transaction_statement(
                        "INSERT INTO rooms (uuid, name, description) VALUES (?, ?, ?)",
                        (str(uuid.uuid4()), room, room),
                    )
                    self.room_cache[room] = room_id

                self.__execute_transaction_statement(
                    "INSERT INTO user_room_link (room_id, user_id) VALUES (?, ?)",
                    (room_id, user_id),
                )
        print("✅ Users loaded")

    def prepare_file_location(self):
        if not self.database_file.parent.exists():
            self.database_file.parent.mkdir(parents=True)
        if self.database_file.exists():
            if not self.database_overwrite:
                raise ValueError(
                    f"Database file {self.database_file} already exists, set overwrite=True to overwrite"
                )
            else:
                # Unlink verwijdert een bestand
                self.database_file.unlink()
                print("✅ Database already exists, deleted")
        if not self.database_file.exists():
            try:
                self.database_file.touch()
                print("✅ New database setup")
            except Exception as e:
                raise ValueError(
                    f"Could not create database file {self.database_file} due to error {e}"
                )


if __name__ == "__main__":
    my_path = Path(__file__).parent.resolve()
    project_root = my_path.parent.parent
    # Deze slashes komen uit de "Path" module. Dit is een module die je kan gebruiken
    # om paden te maken. Dit is handig omdat je dan niet zelf hoeft te kijken of je
    # een / (mac) of een \ (windows) moet gebruiken.
    database_path = project_root / "databases" / "klepdicht.db"
    database_generator = KlepDichtDatabaseGenerator(
        database_path, overwrite=True, initial_data=True
    )
    database_generator.generate_database()
    database_generator.load(setup_file="../../../default_setup.yaml")
