from klepdicht.lib.models.base_model import BaseModel


class RoomModel(BaseModel):
    def __init__(self, db_file):
        super().__init__(db_file)

    def get_room(self, room_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        return cursor.fetchone()
