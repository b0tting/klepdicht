from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO

from klepdicht.lib.controllers.auth_controller import AuthController
from lib.models.settings_model import SettingsModel


def get_snake_name(camel_name):
    return "".join(["_" + c.lower() if c.isupper() else c for c in camel_name]).lstrip(
        "_"
    )


def generate_module_name(blueprint_dir, blueprint_name):
    return blueprint_dir + "." + get_snake_name(blueprint_name)


def index():
    return redirect(AuthController.default_login_route)


class Controllers:
    def add_controller(self, controller_name, controller):
        setattr(self, controller_name, controller)


socketio = SocketIO()
controllers = Controllers()


def create_app(settings):
    app = Flask(__name__)
    app.secret_key = settings.get("secret_key")

    blueprint_dir = "lib.controllers"
    blueprints = ["AuthController", "RoomController", "AdminController"]
    for blueprint in blueprints:
        module = __import__(
            generate_module_name(blueprint_dir, blueprint), fromlist=["bp"]
        )
        blueprint_class = getattr(module, blueprint)
        controllers.add_controller(
            get_snake_name(blueprint), blueprint_class(settings, app)
        )

    import lib.controllers.socketio_routes

    app.add_url_rule("/", "index", index)

    socketio.init_app(app)
    return app
