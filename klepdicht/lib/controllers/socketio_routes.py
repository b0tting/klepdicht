# I don't know how to wrap socketio routes in a blueprint
import logging

from flask import session, request

from klepdicht import socketio, controllers
from klepdicht.lib.models.message_model import MessageModel
from flask_socketio import emit

# BAD BAD BAD.
settings = controllers.room_controller.settings
message_model = MessageModel(settings.get_database_file())


@socketio.on("message")
def handle_message(body):
    if "user" not in session or "room" not in session:
        logging.warning("No user_id or room_id in session")
        return {"error": "No user or room in session", "reason": "login"}, 400

    user = session["user"]
    room = session["room"]
    logging.debug(f"Got message from user {user['id']}")
    if message := body.get("message"):
        message = message.strip()
        print(f"Got message in body and saving {message}")
        message_model.save_message(room["id"], user["id"], message)
        emit(
            "message",
            {
                "message": message,
                "id": message_model.get_last_message_id(),
                "author_uuid": user["uuid"],
                "color": user["color"],
            },
            broadcast=True,
        )
    else:
        print("No message in body")


@socketio.on("joined")
def handle_join(join_message):
    if "user" not in session or "room" not in session:
        print("No user or roomd in session")
        socketio.send({"error": "No user_id or room_id in session", "reason": "login"})
        return {"error": "No user_id or room_id in session", "reason": "login"}, 400
    client_last_seen_id = join_message.get("last_message_id")
    user_id = session["user"]["id"]
    logging.debug(f"Got join request from user {user_id}")
    logging.debug("User last seen message id: " + str(client_last_seen_id))
    messages = message_model.get_messages_since_id(
        client_last_seen_id, settings.get("message_limit")
    )

    logging.debug(
        f"Sending {len(messages)} messages to user {user_id} with sid {request.sid}"
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
