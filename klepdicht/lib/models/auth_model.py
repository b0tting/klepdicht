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
    def validate_login(self, room_name, username, password):
        if not room_name:
            raise AuthValidationException("Room is required", False)
        if not username:
            raise AuthValidationException("Username is required", False)
        if not password:
            raise AuthValidationException("Password is required", False)

        room = dict(self.get_room_for_room_name(room_name))
        user = dict(self.get_user_for_username(username))
        self.validate_user_allowed_in_room(user, room)
        self.validate_password(user, password)
        return user, room

    def validate_message_allowed(self, room, user):
        self.validate_user_allowed_in_room(user, room)

    def get_room_for_room_name(self, room_name):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms WHERE name = ?", (room_name,))
        result = cursor.fetchone()
        if result:
            return dict(result)
        else:
            raise AuthValidationException(f"Room {room_name} does not exist")

    def get_room_for_uuid(self, uuid):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM rooms WHERE uuid = ?", (uuid,))
        result = cursor.fetchone()
        if result:
            return result
        else:
            raise AuthValidationException(f"Room {uuid} does not exist")

    def get_user_for_username(self, username):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return result
        else:
            raise AuthValidationException(f"User {username} does not exist")

    def validate_user_allowed_in_room(self, user, room):
        if user["is_admin"]:
            return True

        cursor = self.get_cursor()
        cursor.execute(
            "SELECT * FROM user_room_link WHERE user_id = ? AND room_id = ?",
            (user["id"], room["id"]),
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            raise AuthValidationException(f"User is not in this room")

    def validate_password(self, user, password):
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = ? AND password = ?", (user["id"], password)
        )
        result = cursor.fetchone()
        if result:
            return True
        else:
            raise AuthValidationException(f"Password for user is incorrect", False)
