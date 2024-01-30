from abc import ABC
import logging
from tkinter import messagebox
from .appviews import Menu
from .appstate import AppState
from .helpers  import DigraphMaker
from persistance.refactoring import Client
from transformations import transformation_api as api


class Controller(ABC):
    def __init__(self, model) -> None:
        self._model = model


class CMenu(Controller):
    def __init__(self, model) -> None:
        super().__init__(model)
    
    def on_close(self, view: Menu):
        view.parent.destroy()
    
    def on_usage(self):
        logging.info('"on_usage" not implemented')


class CRefactor(Controller):
    def __init__(self, model) -> None:
        super().__init__(model)
    
    
    def ast_parse(self, text: str) -> None:
        # parse new ast into the state object
        try:
            AppState().ast_parse(text)
        except Exception as exception:
            match exception:
                case SyntaxError():
                    messagebox.showinfo(title="Syntax Error", message=f"Syntax error: {exception.msg} in line {exception.lineno}.")
                case _:
                    messagebox.showinfo(title="Parsing Error", message="Parsing failed.")
        # update the tree view
        #view.source_tree.on_update()


    def ast_transform(self) -> None:
        if AppState().ast_source:
            AppState().ast_transform()
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")


    def ast_show_source(self) -> None:
        if AppState().ast_source:
            DigraphMaker(api.iter_child_nodes).make(AppState().ast_source)
        else:
            messagebox.showinfo(title="Show AST", message="No AST provided.")

   
    def ast_show_result(self) -> None:
        if AppState().ast_result:
            DigraphMaker(api.iter_child_nodes).make(AppState().ast_result)
        else:
            messagebox.showinfo(title="Show AST", message="No AST generated.")


class CDatabase(Controller):
    def __init__(self, model) -> None:
        super().__init__(model)


class CSettings(Controller):
    def __init__(self, model) -> None:
        super().__init__(model)
