import sqlite3
import uuid
from pathlib import Path


class KlepDichtDatabaseGenerator:
    def __init__(self, database_file, overwrite=False, initial_data=False):
        self.database_file = Path(database_file)
        self.create_initial_data = initial_data
        self.database_overwrite = overwrite
        self.prepare_file_location()
        self.conn = sqlite3.connect(self.database_file)

    def generate_database(self):
        self.create_table_rooms()
        self.create_table_users()
        self.create_user_room_link()
        self.create_table_messages()
        self.create_table_settings()
        self.add_default_settings()
        self.add_default_data()

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

    def add_default_settings(self):
        settings = [
            ["version", "0.0.1"],
            ["name", "klepdicht"],
            ["secret_key", uuid.uuid4().hex],
            ["message_limit", 10],
            ["message_character_limit", 250],
            ["port", 5000],
        ]
        self.__execute_many_transaction_statement(
            "INSERT INTO settings (name, value) VALUES (?, ?)", settings
        )

    def add_default_data(self):
        if self.create_initial_data:
            query = "INSERT INTO users (username, uuid, cryptoname,  color, password) VALUES (?, ?, ?, ?, ?)"
            user_id = self.__execute_transaction_statement(
                query, ["sexyuser", uuid.uuid4().hex, "banana", "red", "admin"]
            )
            user_id2 = self.__execute_transaction_statement(
                query, ["otheruser", uuid.uuid4().hex, "banana", "blue", "admin"]
            )
            query = "INSERT INTO rooms (name, description, uuid) VALUES (?, ?, ?)"
            room_id = self.__execute_transaction_statement(
                query, ["test", "testroom", uuid.uuid4().hex]
            )
            query = "INSERT INTO user_room_link (room_id, user_id) VALUES (?, ?)"
            self.__execute_transaction_statement(query, [room_id, user_id])
            self.__execute_transaction_statement(query, [room_id, user_id2])
            query = "INSERT INTO messages (message, room_id, user_id) VALUES (?, ?, ?)"
            self.__execute_transaction_statement(
                query, ["testmessage", room_id, user_id]
            )
            self.__execute_transaction_statement(
                query, ["testmessage 2", room_id, user_id2]
            )

            print("✅ Default data added")

    def __execute_many_transaction_statement(
        self, create_statement, list_of_parameters=()
    ):
        c = self.conn.cursor()
        c.executemany(create_statement, list_of_parameters)
        self.conn.commit()

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
