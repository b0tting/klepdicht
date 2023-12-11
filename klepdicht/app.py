import logging

import sys

# Returns "lib.controllers.auth_controller" from "AuthController" and "lib.controllers"
from klepdicht import create_app, socketio

from lib.models.settings_model import SettingsModel

settings = SettingsModel("databases/klepdicht.db")
app = create_app(settings)
logging.basicConfig(level=logging.DEBUG)
logging.debug("STARTING APP")
if __name__ == "__main__":
    socketio.run(app, debug=True, port=settings.get("port"), allow_unsafe_werkzeug=True)
