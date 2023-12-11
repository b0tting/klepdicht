from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from klepdicht.lib.controllers.base_controller import BaseController
from klepdicht.lib.models.message_model import MessageModel
from klepdicht.lib.models.room_model import RoomModel


class RoomController(BaseController):
    def __init__(self, settings, app):
        super().__init__(settings, app, "room", "/room")
        self.conversation_model = MessageModel(settings.get_database_file())
        self.room_model = RoomModel(settings.get_database_file())
        self.message_model = MessageModel(settings.get_database_file())

    def register_routes(self):
        self.blueprint.add_url_rule("/room", "room", self.room, methods=["GET"])

    def room(self):
        return render_template(
            "room.html.jinja",
            message_character_limit=self.settings.get("message_character_limit"),
            endpoint_url=self.settings.get("endpoint_url"),
        )

    def get_messages_since_id(self, message_id):
        last_message_id = self.message_model.get_last_message_id()
        if message_id == last_message_id:
            return []
        else:
            return self.message_model.get_messages_since_id(message_id)
