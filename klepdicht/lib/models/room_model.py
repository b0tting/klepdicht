from klepdicht.lib.models.base_model import BaseModel


class RoomModel(BaseModel):
    def __init__(self, db_file):
        super().__init__(db_file)

    def get_room(self, room_id):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        return cursor.fetchone()

    def get_all_rooms(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms")
        return cursor.fetchall()

    def get_users_for_room(self, room):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT * FROM users u WHERE u.id in (SELECT user_id FROM user_room_link WHERE room_id = ?)",
            (room["id"],),
        )
        return [dict(users) for users in cursor.fetchall()]

    def get_visible_user_count(self, room_id):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT count(*) FROM users u WHERE u.id in (SELECT user_id FROM user_room_link WHERE room_id = ?) and u.is_invisible is not 1",
            (room_id,),
        )
        result = cursor.fetchone()[0]
        return result

    def get_messages_for_room(self, room, time_asc=True):
        cursor = self.get_cursor()
        order = "ASC" if time_asc else "DESC"
        cursor.execute(
            f"SELECT *, u.username, u.color FROM messages m left join users u on m.user_id == u.id WHERE m.room_id = ? ORDER BY m.date_created {order}",
            (room["id"],),
        )
        return [dict(messages) for messages in cursor.fetchall()]

    def get_room_for_uuid(self, uuid):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms WHERE uuid = ?", (uuid,))
        return cursor.fetchone()
