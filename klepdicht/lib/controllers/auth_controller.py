import logging

from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from klepdicht.lib.controllers.base_controller import BaseController
from klepdicht.lib.models.auth_model import AuthModel, AuthValidationException


class AuthController(BaseController):
    default_login_route = "/login"

    def __init__(self, settings, app):
        super().__init__(settings, app, "auth", "/auth")
        self.auth_model = AuthModel(settings.get_database_file())

    def register_routes(self):
        self.blueprint.add_url_rule(
            "/login", "login", self.login, methods=["GET", "POST"]
        )
        self.blueprint.add_url_rule(
            "/login/<room>/<username>/<password>", "login", self.login
        )
        self.blueprint.add_url_rule(
            "/handle_login", "handle_login", self.handle_login, methods=["POST"]
        )

        self.blueprint.add_url_rule("/logout", "logout", self.logout, methods=["GET"])

    def login(self, room="", username="", password=""):
        parameters = {
            "room": request.args.get("room", room),
            "username": request.args.get("username", username),
            "password": request.args.get("password", password),
        }
        return render_template("login.html.jinja", **parameters)

    def logout(self):
        user = session.pop("user", None)
        room = session.pop("room", None)
        parameters = {
            "room": room.get("name"),
            "username": user.get("username"),
            "password": user.get("password"),
        }
        return render_template("login.html.jinja", **parameters)

    def handle_login(self):
        parameters = {
            "room": request.form["room"],
            "username": request.form["username"],
            "password": request.form["password"],
        }

        try:
            self.auth_model.validate_login(**parameters)
            session["room"] = self.auth_model.get_room_for_room_name(parameters["room"])
            session["user"] = dict(
                self.auth_model.get_user_for_username(parameters["username"])
            )
            result = redirect(url_for("room.room"))
        except AuthValidationException as e:
            logging.warning(e)
            flash(e.get_message())
            result = self.login(**parameters)
        except Exception as e:
            logging.warning(e)
            flash(str(e))
            result = self.login(**parameters)
        return result
