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
        if user:
            flash(f"{user.get('username')} logged out")
            parameters = {
                "username": user.get("username"),
                "password": user.get("password"),
            }
            return redirect(url_for("auth.login", **parameters))
        else:
            return redirect(url_for("auth.login"))

    def handle_login(self):
        parameters = {
            "room_name": request.form.get("room", "").strip(),
            "username": request.form.get("username", "").strip(),
            "password": request.form.get("password", "").strip(),
        }

        try:
            user, room = self.auth_model.validate_login(**parameters)
            session["user"] = dict(user)
            result = redirect(url_for("room.room", room_uuid=room["uuid"]))
        except AuthValidationException as e:
            logging.warning(e)
            flash(e.get_message())
            result = self.login(**parameters)
        except Exception as e:
            logging.warning(e)
            flash(str(e))
            result = self.login(**parameters)
        return result
