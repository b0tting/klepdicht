from klepdicht.lib.models.base_model import BaseModel


class AuthValidationException(Exception):
    def __init__(self, private_message, private=True):
        super().__init__(private_message)
        self.private = private

    def get_message(self):
        if self.private:
            return "An error occurred"
        else:
            return self.args[0]


class AuthModel(BaseModel):
    def validate_login(self, room, username, password):
        if not room:
            raise AuthValidationException("Room is required", False)
        if not username:
            raise AuthValidationException("Username is required", False)
        if not password:
            raise AuthValidationException("Password is required", False)

        room_id = self.get_id_for_room_name(room)
        user_id = self.get_user_for_username(username)["id"]
        self.validate_user_in_room(user_id, room_id)
        self.validate_password(user_id, password)

    def get_id_for_room_name(self, room):
        cursor = self.get_cursor()
        cursor.execute("SELECT id FROM rooms WHERE name = ?", (room,))
        result = cursor.fetchone()
        if result:
            return result["id"]
        else:
            raise AuthValidationException(f"Room {room} does not exist")

    def get_user_for_username(self, username):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return result
        else:
            raise AuthValidationException(f"User {username} does not exist")

    def validate_user_in_room(self, user_id, room_id):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT * FROM user_room_link WHERE user_id = ? AND room_id = ?",
            (user_id, room_id),
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            raise AuthValidationException(f"User is not in this room")

    def validate_password(self, user_id, password):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = ? AND password = ?", (user_id, password)
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            raise AuthValidationException(f"Password for user is incorrect", False)
