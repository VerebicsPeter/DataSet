#----------------
from math import ceil
import difflib
import logging
#----------------
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
    # TODO turn treeview into table view into
#----------------
from .appstate import AppState
from .appviews import AppGUI
from .controllers import *
#----------------
from persistance.refactoring import Client
#----------------
from transformations import transformation_api as api
#----------------

class App:
    def __init__(self) -> None:
        # app state (basicly the model)
        self._app_state = AppState()  # initialize the (monostate) app state
        # controllers
        self._menu_ctl = CMenu(self._app_state)
        self._refactor_ctl = CRefactor(self._app_state)
        self._database_ctl = CDatabase(self._app_state)
        self._settings_ctl = CSettings(self._app_state)
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

# TODO controller instead of writing callback functions in widgets
