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
from .helpers  import DigraphMaker, SyntaxHighlighter, NAVIGATION_KEYCODES
#----------------
from persistance.refactoring import Client
#----------------
from transformations import transformation_api as api
#----------------


class Menu(ttk.Frame):
    def __init__(self, parent: ttk.Window):
        super().__init__(parent)
        
        self._menubar = ttk.Menu(parent)
        # submenus
        self.filemenu = ttk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.filemenu.add_command(label="Close", command=self.on_close)
        self.aboutmenu = ttk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.aboutmenu.add_command(label="Usage", command=self.on_about)
        # add cascade
        self._menubar.add_cascade(label="File", menu=self.filemenu)
        self._menubar.add_cascade(label="About", menu=self.aboutmenu)
        self.parent = parent
    
    def on_close(self):
        self.parent.destroy()
    
    def on_about(self):
        logging.info('"on_about" not implemented')


class ASTView(ttk.Frame):
    def __init__(self, parent, target: str = None):
        super().__init__(parent)
        
        self.target = target
        # treeview data
        self.data = []
        # treeview widget
        self.treeview = ttk.Treeview(self, height=self.winfo_height(), selectmode="browse", columns=(1))
        # scrollbar
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.config(command=self.treeview.yview)
        self.treeview['yscrollcommand'] = self.scrollbar.set
        # treeview columns
        self.treeview.column("#0", anchor="w", width=50)
        self.treeview.column("#1", anchor="w", width=50)
        # treeview headings
        self.treeview.heading("#0", text="Node type",  anchor="center")
        self.treeview.heading("#1", text="Node value", anchor="center")
        # pack
        self.scrollbar.pack(side="right", fill="y")
        self.treeview.pack(expand=True, fill="both")
    
    def on_update(self):
        self.treeview.delete(*self.treeview.get_children())
        
        self.data = AppState().treeview_data(self.target)
        # insert treeview data
        for item in self.data:
            self.treeview.insert(
                parent=item[0], index='end', iid=item[1], text=item[2], values=item[3])
            if item[0] == "":
                # open parent
                self.treeview.item(item[1], open=True)
        # select root
        self.treeview.selection_set(self.data[0][1])
        self.treeview.see(self.data[0][1])


class SourceText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # textbox
        self.textbox = ttk.Text(self, height=self.winfo_height(), font=('FreeMono', 12))
        self.textbox.bind("<KeyRelease>", self.on_update)
        SyntaxHighlighter.set_colors(self.textbox)
        # config scrollbar
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.config(command=self.textbox.yview)
        self.textbox['yscrollcommand'] = self.scrollbar.set
        # pack
        self.scrollbar.pack(side="right", fill="y")
        self.textbox.pack(fill="both", expand=True)
    
    def on_update(self, event):
        if event.keycode in NAVIGATION_KEYCODES: return
        SyntaxHighlighter.highlight(self.textbox)


class ResultText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # textbox
        self.textbox = ttk.Text(self, height=self.winfo_height(), font=('FreeMono', 12))
        self.textbox.config(state="disabled")
        SyntaxHighlighter.set_colors(self.textbox)
        # config scrollbar
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.config(command=self.textbox.yview)
        self.textbox['yscrollcommand'] = self.scrollbar.set
        # pack
        self.scrollbar.pack(side="right", fill="y")
        self.textbox.pack(fill="both", expand=True)
    
    def on_update(self):
        SyntaxHighlighter.highlight(self.textbox)
    
    def on_update_text(self, text: str):
        self.textbox['state'] = 'normal'
        self.textbox.delete(1.0,  tk.END)
        self.textbox.insert(tk.END, text)
        self.textbox['state'] = 'disabled'
        self.on_update()


class RefactorTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # rows
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=0)
        # columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        # source widgets
        self.source_text = SourceText(self)
        self.source_tree = ASTView(self, "source")
        # result widgets
        self.result_text = ResultText(self)
        self.result_tree = ASTView(self, "result")
        # grid
        self.source_text.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.source_tree.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.result_text.grid(row=0, column=2, columnspan=2, sticky="nsew")
        self.result_tree.grid(row=1, column=2, columnspan=2, sticky="nsew")
        # show source ast button
        ttk.Button(self, text="Show Source AST", width=20,
            command=self.ast_show_source
        ).grid(row=2, column=0, pady=10)
        # parse source ast button
        ttk.Button(self, text="Parse AST", width=20,
            command=lambda:self.ast_parse('source')
        ).grid(row=2, column=1, pady=10)
        # transform button
        ttk.Button(self, text="Transform", width=20,
            command=self.ast_transform
        ).grid(row=2, column=2, pady=10)
        # show result ast button
        ttk.Button(self, text="Show Result AST", width=20, 
            command=self.ast_show_result
        ).grid(row=2, column=3, pady=10)


    def ast_parse(self, target: str) -> None:
        text: str = self.source_text.textbox.get('1.0', tk.END)
        # parse new ast into the state object
        try:
            AppState().ast_parse(text, target)
        except Exception as exception:
            match exception:
                case SyntaxError():
                    messagebox.showinfo(title="Syntax Error", message=f"Syntax error: {exception.msg} in line {exception.lineno}.")
                case _:
                    messagebox.showinfo(title="Parsing Error", message="Parsing failed.")
        # update the tree view
        self.source_tree.on_update()

    def ast_transform(self) -> None:
        if AppState().ast_source:
            result = AppState().ast_transform()
            # update text widget
            self.result_text.on_update_text(result)
            # update tree widget
            self.result_tree.on_update()
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


class DatabaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
    
        self.label = ttk.Label(self, text='Documents: None')
        self.label.pack(side="top", fill="y", expand=False, padx=5, pady=5)
        
        if Client().client is None: return
        
        self.page = 0
        self.page_size = 20
        self.count = Client().get_document_count() 
        self.update_label_text()
        
        # frame for db browser
        self.db_frame = ttk.Frame(self)
        self.db_frame.pack(fill="both", expand=True)
        
        # frame for db browser navigation buttons
        self.button_frame = ttk.Frame(self.db_frame)
        self.button_frame.pack(pady=5)
        
        self.prev_button = ttk.Button(self.button_frame, width=15, text="Previous Page",
                command=lambda:self.on_page_change(-1))
        self.next_button = ttk.Button(self.button_frame, width=15, text="Next Page",
                command=lambda:self.on_page_change( 1))
        
        self.prev_button.config(state="disabled")
        self.prev_button.grid(row=0, column=0, padx=5, pady=5)
        self.next_button.grid(row=0, column=1, padx=5, pady=5)
        
        # fetch the first page
        cols, rows = self.fetch()
        
        self.tree = ttk.Treeview(self.db_frame, columns=cols, show='headings')
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        # define headings
        for col in cols: self.tree.heading(col, text=col)
        # add data to the treeview
        for row in rows: self.tree.insert('', tk.END, values=row)
        # display
        self.tree.pack(fill="both", expand=True)
        
        # text box for diff
        self.diff_text = ttk.Text(self)
        self.diff_text.config(state="disabled")
        self.diff_text.pack(fill="both", expand=False)
    # TODO make a separate form to print the diffs

    def fetch(self):
        keys, data = Client().parsed_data(skip = self.page_size * self.page, limit = self.page_size)

        cols = tuple(keys)
        # get data row by row
        rows = []
        while data and(row := data.pop()):
            values = [ row[key] if key == "_id" else
                       row[key] if not row[key] else len(row[key]) for key in keys ]
            rows.append(tuple(values))
        
        return cols, rows


    def paginate(self, inc: int):
        self.page += inc
        p_min, p_max = 0, ceil(self.count / self.page_size)
        if self.page <= p_min:
            self.page = p_min
            self.prev_button["state"] = "disabled"
        else:
            self.prev_button["state"] = "normal"
        if self.page >= p_max:
            self.page = p_max
            self.next_button["state"] = "disabled"
        else:
            self.next_button["state"] = "normal"


    def on_page_change(self, inc: int):
        self.paginate(inc)
        cols, rows = self.fetch()
        self.tree.destroy()
        self.tree = ttk.Treeview(self.db_frame, columns=cols, show='headings')
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        # define headings
        for col in cols: self.tree.heading(col, text=col)
        # add data to the treeview
        for row in rows: self.tree.insert('', tk.END, values=row)
        # display
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.update_label_text()


    def on_item_select(self, event):
        for selected in self.tree.selection():
            record = self.tree.item(selected)["values"]
            # show a message
            id = record[0]
            if refactoring := Client().equivalent.find_one({"_id": id}):
                self.update_diff_text(refactoring, "autopep+for_to_comp")


    def update_diff_text(self, record, key: str):
        if "_source" not in record or key not in record: return
        source_content : str = record["_source"]
        result_content : str = record[key]
        # split the strings into lines
        source_lines = source_content.splitlines()
        result_lines = result_content.splitlines()
        # use difflib to get the differences
        differ = difflib.Differ()
        diff = list(differ.compare(source_lines, result_lines))
        # update the diff text widget
        self.diff_text['state'] = 'normal'
        self.diff_text.delete(1.0,tk.END)
        # print the differences
        for line in diff:
            self.diff_text.insert(tk.END, line+"\n")
        self.diff_text['state'] = 'disabled'


    def update_label_text(self) -> str:
        self.label["text"] = ', '.join([
            self.get_docs_info(),
            self.get_page_info()])


    def get_docs_info(self) -> str:
        return f'Documents: {self.count}'


    def get_page_info(self) -> str:
        page_index = self.page + 1
        page_count = ceil(self.count / self.page_size) + 1
        return f'Page: {page_index} of {page_count}'


class SettingsTab(ttk.Frame):
    def __init__(self, parent, rules: list[str] = None):
        super().__init__(parent)
        
        self.rules = ttk.Labelframe(self, text="Rules")
        self.rules.pack(pady=10)
        # new rule frame
        self.rules_new = ttk.Labelframe(self.rules, text="New Rule")
        self.rules_new.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        # custom rules frame
        self.rules_custom = ttk.Labelframe(self.rules, text="Custom Rules")
        self.rules_custom.grid(row=0, column=1, padx=10, pady=10)
        
        self.combo_rules = ttk.Combobox(self.rules_new, values=rules, width=25)
        self.combo_rules.grid(row=0, column=0, padx=10, pady=10)
        self.combo_rules["state"] = "readonly"
        self.combo_rules.set(self.combo_rules["values"][0])

        self.button_add = ttk.Button(self.rules_new, text="Add Rule",
                                                command=self.add_rule)
        self.button_add.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.list_rules = tk.Listbox(self.rules_custom, width=30)
        self.list_rules.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        
        self.button_clear = ttk.Button(self.rules_custom, text="Clear rules",
                                                command=self.clear_rules)
        self.button_clear.grid(row=1, column=0, padx=10, pady=10)
        self.button_clear["state"] = "disabled"
        
        self.button_delete = ttk.Button(self.rules_custom, text="Delete rule",
                                                command=self.clear_rules)  # TODO
        self.button_delete.grid(row=1, column=1, padx=10, pady=10)
        self.button_delete["state"] = "disabled"
    
    def add_rule(self):
        self.list_rules.insert(tk.END, name := self.combo_rules.get())
        AppState().add_visitor(name)
        self.button_clear["state"] = "normal"
    
    def clear_rules(self):
        if not AppState().visitors: return
        self.list_rules.delete(0, tk.END)
        AppState().clear_visitors()
        self.button_clear["state"] = "disabled"


class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # right side
        ttk.Sizegrip(self).pack(side="right", anchor="se")
        # left side
        ttk.Separator(self, orient='vertical').pack(side="left", padx=(0,10))
        self.label_database = ttk.Label(self, text=f"Database: {Client().get_client_info()}")
        self.label_database.pack(side="left", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        self.label_settings = ttk.Label(self, text=f"Settings: {AppState().settings_info()}")
        self.label_settings.pack(side="left", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        # add observable
        AppState().attach(self)
    
    def on_update(self):
        self.label_settings["text"] = f"Settings: {AppState().settings_info()}"
        self.label_database["text"] = f"Database: {Client().get_client_info()}"


class AppGUI(ttk.Window):
    def __init__(self) -> None:
        # setup
        super().__init__(themename="solar")
        self.geometry("1280x640")
        self.minsize(1280,640)
        self.title("Equivalent Transformations")
        # menu
        self.menu = Menu(self)
        self.config(menu=self.menu._menubar)
        # tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side="top", fill="both", expand=True)
        self.refactor_tab = RefactorTab(self.tabs)
        self.database_tab = DatabaseTab(self.tabs)
        self.settings_tab = SettingsTab(self.tabs, rules=api.all_visitor_names())
        self.tabs.add(self.refactor_tab, text="Refactor")
        self.tabs.add(self.database_tab, text="Database")
        self.tabs.add(self.settings_tab, text="Settings")
        # status bar
        self.statusbar = StatusBar(self)
        self.statusbar.pack(side="bottom", fill="x")

    def run(self):
        self.mainloop()


class App:
    def __init__(self) -> None:
        AppState()  # initialize the (monostate) app state
        self._app_GUI = AppGUI()
        # set logging level
        logging.root.setLevel(logging.DEBUG)
        
    def run(self):
        self._app_GUI.run()
