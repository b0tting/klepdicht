from abc import abstractmethod, ABC

from flask import Blueprint


class BaseController(ABC):
    def __init__(self, settings, app, controller_name, url_prefix):
        self.blueprint = Blueprint(controller_name, __name__, url_prefix)
        self.settings = settings
        self.app = app
        self.register_routes()
        self.app.register_blueprint(self.blueprint)

    @abstractmethod
    def register_routes(self):
        pass
