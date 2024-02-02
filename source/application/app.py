#----------------
import logging
#----------------
from .appstate import AppState
from .appviews import AppGUI
from .client import Client
from .controllers import *
#----------------
from transformations import transformation_api as api
#----------------

class App:
    def __init__(self) -> None:
        # app state (basicly the model)
        self._app_state = AppState()  # initialize the (monostate) app state
        # controllers
        self._menu_ctl = MenuController(self._app_state)
        self._refactor_ctl = RefactorController(self._app_state)
        self._database_ctl = DatabaseController(Client())
        self._settings_ctl = SettingsController(self._app_state)
        # view
        self._app_GUI  = AppGUI(
            self._menu_ctl,
            self._refactor_ctl,
            self._database_ctl,
            self._settings_ctl,
        )
        # set logging level
        logging.root.setLevel(logging.DEBUG)
        
    def run(self):
        self._app_GUI.run()
