import logging
import difflib
import webbrowser  # for opening html diff
from tkinter import messagebox
from .appstate import AppState
from .client import Client
from .helpers  import DigraphMaker
from transformations import transformation_api as api


class MenuController:
    
    def __init__(self, model: AppState) -> None:
        self.model = model
    
    
    def close(self):  # this can be used as a hook when closing the app 
        pass


class RefactorController:
    
    def __init__(self, model: AppState) -> None:
        self.model = model
    
    
    def ast_parse(self, text: str) -> None:
        # parse new ast into the state object
        try:
            self.model.ast_parse(text)
        except Exception as exception:
            match exception:
                case SyntaxError():
                    messagebox.showinfo(title="Syntax Error", message=f"Syntax error: {exception.msg} in line {exception.lineno}.")
                case _:
                    messagebox.showinfo(title="Parsing Error", message="Parsing failed.")


    def ast_transform(self) -> None:
        if self.model.ast_source:
            self.model.ast_transform()
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")


    def ast_show_source(self) -> None:
        if self.model.ast_source:
            DigraphMaker(api.iter_child_nodes).make(self.model.ast_source)
        else:
            messagebox.showinfo(title="Show AST", message="No AST provided.")

   
    def ast_show_result(self) -> None:
        if self.model.ast_result:
            DigraphMaker(api.iter_child_nodes).make(self.model.ast_result)
        else:
            messagebox.showinfo(title="Show AST", message="No AST generated.")


class DatabaseController:
    
    def __init__(self, model: Client) -> None:
        self.model = model
    
    
    def document_count(self) -> int | None:
        return self.model.get_document_count()
    
    
    def find_by_id(self, id: str):
        record = self.model.find_one(id)
        if not record:
            messagebox.showinfo(title="Show Diff", message=f"No record with id: {id}.")
            return
        return record


    def find_all(self, skip, limit):
        keys, data = self.model.table_data(skip, limit)

        cols = [ {"text": f"{key}"} for key in keys ]
        # get data row by row
        rows = []
        while data and (row := data.pop()):
            values = [
                    row[key] if key == "_id" else
                    '-'      if not row[key] else
                    self._lines_str(row[key])
                    for key in keys ]
            rows.append(tuple(values))
        
        return cols, rows
    
    
    def get_result(self, doc: dict[str, str], key: str):
        # validate doc
        if not doc.get("_id"):
            return
        if not doc.get("_source"):
            return
        # validate key
        if key in {"_id", "_source"}:
            return
        if key not in doc:
            return
        return doc["_source"], doc[key]


    def create_diff(self, lines_a: list[str], lines_b: list[str]) -> list[str]:
        diff = difflib.Differ().compare(lines_a, lines_b)
        return list(diff)


    def create_diff_html(self, lines_a: list[str], lines_b: list[str]) -> None:
        diff_html = difflib.HtmlDiff().make_file(lines_a, lines_b)
        with open('diff.html', 'w') as f: f.write(diff_html)
        webbrowser.open_new_tab("diff.html")
    
    
    def _lines_str(self, lines: str) -> str:
        return f"{len(lines.splitlines())} lines"


class SettingsController:
    
    def __init__(self, model: AppState) -> None:
        self.model = model


    def add_rule(self, name: str) -> None:
        self.model.add_visitor(name)


    def clear_rules(self) -> None:
        self.model.clear_visitors()
