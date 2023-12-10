import logging

from klepdicht.lib.models.base_model import BaseModel


class MessageModel(BaseModel):
    def __init__(self, db_file):
        self.logger = logging.getLogger("klepdicht.lib.models.message_model")
        super().__init__(db_file)

    def get_last_message_id(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT MAX(id) as max_id FROM messages")
        result = cursor.fetchone()
        return result["max_id"]

    def get_messages_since_id(self, message_id, limit=10):
        logging.debug(f"Getting messages since {message_id}")
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT m.*, u.username as author, u.uuid as author_uuid, u.color as color FROM messages m LEFT JOIN users u on m.user_id == u.id WHERE m.id > ? ORDER BY id DESC LIMIT "
            + str(limit),
            (message_id,),
        )
        result = cursor.fetchall()
        result.reverse()
        return result

    def get_conversation(self, room_id):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT *, users.uuid as userlabel "
            "FROM messages LEFT JOIN users "
            "on messages.user_id == users.id "
            "WHERE room_id = ? ORDER BY date_created DESC",
            (room_id,),
        )
        return cursor.fetchall()

    def save_message(self, room_id, user_id, message):
        cursor = self.get_cursor()
        logging.debug(f"Saving message {message} in room {room_id} from user {user_id}")
        cursor.execute(
            "INSERT INTO messages (room_id, user_id, message) VALUES (?, ?, ?)",
            (room_id, user_id, message),
        )
        cursor.connection.commit()
        return cursor.lastrowid
