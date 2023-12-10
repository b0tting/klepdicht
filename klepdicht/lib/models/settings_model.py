from lib.models.base_model import BaseModel


class SettingsModel(BaseModel):
    def __init__(self, db_file):
        self.db_file = db_file
        super().__init__(db_file)
        self.settings_cache = {}

    def get_database_file(self):
        return self.db_file

    def get(self, name):
        if name in self.settings_cache:
            return self.settings_cache[name]
        else:
            value = self.__get_setting(name)
            self.settings_cache[name] = value
            return value

    def __get_setting(self, name):
        cursor = self.get_cursor()
        cursor.execute("SELECT value FROM settings WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            return result["value"]
        else:
            raise KeyError(f"Setting {name} not found")

    def set(self, name, value):
        cursor = self.__get_cursor()
        cursor.execute(
            "INSERT INTO settings (name, value) VALUES (?, ?)", (name, value)
        )
        cursor.connection.commit()
        self.settings_cache[name] = value
        return cursor.lastrowid
