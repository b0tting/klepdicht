from flask import render_template, session, redirect, url_for

from klepdicht.lib.controllers.base_controller import BaseController
from klepdicht.lib.models.room_model import RoomModel


class AdminController(BaseController):
    def __init__(self, settings, app):
        super().__init__(settings, app, "admin", "/admin")
        self.room = RoomModel(settings.get_database_file())

    def register_routes(self):
        self.blueprint.add_url_rule(
            "/ylva_admin", "ylva_admin", self.admin, methods=["GET"]
        )

    def admin(self):
        if (
            not session.get("user")
            or not session.get("user").get("username") == "admin"
        ):
            return redirect(url_for("auth.login"))
        rooms = self.room.get_all_rooms()
        users_room = {room: self.room.get_users_for_room(room) for room in rooms}
        messages_room = {
            room: self.room.get_messages_for_room(room, time_asc=False)
            for room in rooms
        }
        return render_template(
            "admin.html.jinja", users_room=users_room, messages_room=messages_room
        )
