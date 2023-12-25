# I don't know how to wrap socketio routes in a blueprint
import logging

from flask import session, request

from klepdicht import socketio, controllers
from klepdicht.lib.models.auth_model import AuthModel
from klepdicht.lib.models.message_model import MessageModel
from flask_socketio import emit, join_room, send

from klepdicht.lib.models.room_model import RoomModel

# BAD BAD BAD.
settings = controllers.room_controller.settings
message_model = MessageModel(settings.get_database_file())
room_model = RoomModel(settings.get_database_file())
auth_model = AuthModel(settings.get_database_file())


@socketio.on("message")
def handle_message(body):
    if "user" not in session:
        logging.warning("No user_id in session")
        return {"error": "No user or room in session", "reason": "login"}, 400

    user = session["user"]
    room_uuid = body["room"]
    room = room_model.get_room_for_uuid(room_uuid)
    try:
        auth_model.validate_message_allowed(room, user)
    except Exception as e:
        logging.warning(e)
        return {"error": "No user or room in session", "reason": "login"}, 400
    logging.debug(f"Got message from user {user['id']} with sid {request.sid}")
    if message := body.get("message"):
        message = message.strip()
        print(f"Got message in body and saving {message}")
        message_model.save_message(room["id"], user["id"], message)
        send(
            {
                "message": message,
                "id": message_model.get_last_message_id(),
                "author_uuid": user["uuid"],
                "color": user["color"],
            },
            to=room["uuid"],
        )
    else:
        print("No message in body")


@socketio.on("joined")
def handle_join(join_message):
    if "user" not in session:
        print("No user in session")
        socketio.send(
            {"error": "No user in session", "reason": "login"}, room=request.sid
        )
        return {"error": "No user in session", "reason": "login"}, 400

    client_last_seen_id = join_message.get("last_message_id")
    user = session["user"]
    room = room_model.get_room_for_uuid(join_message["room_uuid"])
    try:
        auth_model.validate_message_allowed(room, user)
    except Exception as e:
        logging.warning(e)
        socketio.send(
            {"error": "No user in session", "reason": "login"}, room=request.sid
        )
        return {"error": "No user or room in session", "reason": "login"}, 400

    join_room(room["uuid"])
    logging.debug(f"Got join request from user {user['id']}")
    logging.debug("User last seen message id: " + str(client_last_seen_id))
    messages = message_model.get_messages_since_id(
        client_last_seen_id, room["id"], settings.get("message_limit")
    )
    logging.debug(
        f"Sending {len(messages)} messages to user {user['id']} with sid {request.sid} in room {room['name']}"
    )
    user_count = room_model.get_visible_user_count(room["id"])
    socketio.send(
        {
            "message": f"There are {user_count} users in room {room['name']}",
            "is_info": True,
        },
        room=request.sid,
    )

    for message in messages:
        socketio.send(
            {
                "message": message["message"],
                "id": message["id"],
                "author_uuid": message["author_uuid"],
                "color": message["color"],
            },
            room=request.sid,
        )
