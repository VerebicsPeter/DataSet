#----------------
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sv_ttk  # tkinter theme
#----------------
from .appstate import AppState
from .helpers  import DigraphMaker, SyntaxHighlighter, NAVIGATION_KEYCODES
#----------------
from persistance.refactoring import Client
#----------------
from transformations import transformation_api as api
#----------------


class CustomFrame(ttk.Frame):
    """ A frame that has optional state parameter in constructor
    """
    def __init__(self, parent, state: AppState = None):
        super().__init__(parent)
        self._state = state


class Menu(CustomFrame):
    def __init__(self, parent: tk.Tk, state = None):
        super().__init__(parent, state)
        
        self._menubar = tk.Menu(parent)
        # submenus
        self.filemenu = tk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.filemenu.add_command(label="Close", command=self.on_close)
        self.aboutmenu = tk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.aboutmenu.add_command(label="Usage", command=self.on_about)
        # add cascade
        self._menubar.add_cascade(label="File", menu=self.filemenu)
        self._menubar.add_cascade(label="About", menu=self.aboutmenu)
        self.parent = parent
    
    def on_close(self):
        self.parent.destroy()
    
    def on_about(self):
        logging.info('"on_about" not implemented')


class TreeView(CustomFrame):
    def __init__(self, parent, state = None, target: str = None):
        super().__init__(parent, state)
        
        self.target = target; self.data = []
        # treeview
        self.treeview = ttk.Treeview(self, height=self.winfo_height(),
                                     selectmode="browse", columns=(1))
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
        
        self.data = self._state.treeview_data(self.target)
        
        # insert treeview data
        for item in self.data:
            self.treeview.insert(
                parent=item[0], index='end', iid=item[1], text=item[2], values=item[3])
            if item[0] == "":
                self.treeview.item(item[1], open=True)  # open parent
        # select root
        self.treeview.selection_set(self.data[0][1])
        self.treeview.see(self.data[0][1])


class SourceText(CustomFrame):
    def __init__(self, parent, state = None):
        super().__init__(parent, state)
        
        self.textbox = tk.Text(self, height=self.winfo_height(), font=('FreeMono', 12))
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


class ResultText(CustomFrame):
    def __init__(self, parent, state = None):
        super().__init__(parent, state)
        
        self.textbox = tk.Text(self, height=self.winfo_height(), font=('FreeMono', 12))
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


class RefactorTab(CustomFrame):
    def __init__(self, parent, state = None):
        super().__init__(parent, state)
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
        self.source_text_widget = SourceText(self, state)
        self.source_tree_widget = TreeView(self, state, "source")
        # result widgets
        self.result_text_widget = ResultText(self, state)
        self.result_tree_widget = TreeView(self, state, "result")
        
        # grid
        self.source_text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.source_tree_widget.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.result_text_widget.grid(row=0, column=2, columnspan=2, sticky="nsew")
        self.result_tree_widget.grid(row=1, column=2, columnspan=2, sticky="nsew")
        
        # show source ast button
        ttk.Button(self, text="Show source AST", width=20,
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
        ttk.Button(self, text="Show result AST", width=20, 
            command=self.ast_show_result
        ).grid(row=2, column=3, pady=10)

    
    def ast_parse(self, target: str) -> None:
        text: str = self.source_text_widget.textbox.get('1.0', tk.END)
        # parse new ast into the state object
        try:
            self._state.ast_parse(text, target)
        except Exception as exception:
            match exception:
                case SyntaxError():
                    messagebox.showinfo(title="Syntax Error", message=f"Syntax error: {exception.msg} in line {exception.lineno}.")
                case _:
                    messagebox.showinfo(title="Parsing Error", message="Parsing failed.")
        # update the tree view
        self.source_tree_widget.on_update()

    def ast_transform(self) -> None:
        if self._state.ast_source:
            result = self._state.ast_transform()
            # update text widget
            self.result_text_widget.on_update_text(result)
            # update tree widget
            self.result_tree_widget.on_update()
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")

    def ast_show_source(self) -> None:
        if self._state.ast_source:
            DigraphMaker(api.iter_child_nodes).make(self._state.ast_source)
        else:
            messagebox.showinfo(title="Show AST", message="No AST provided.")

    def ast_show_result(self) -> None:
        if self._state.ast_result:
            DigraphMaker(api.iter_child_nodes).make(self._state.ast_result)
        else:
            messagebox.showinfo(title="Show AST", message="No AST generated.")


class DatabaseTab(CustomFrame):
    def __init__(self, parent, state = None):
        super().__init__(parent, state)
        self.label =ttk.Label(self, text=f'Connection: {Client.get_client_info()}'+ ', '+f'Documents: {Client.count_documents()}')
        self.label.pack(side="top", fill="y", expand=False, padx=5, pady=5)


class SettingsTab(CustomFrame):
    def __init__(self, parent, state = None, rules: list[str] = None):
        super().__init__(parent, state)
        
        self.rules = ttk.Labelframe(self, text="Custom Rules")
        self.rules.grid(row=0, column=0, padx=10, pady=10)
        
        self.label_rule = ttk.Label(self.rules, text="New rule")
        self.label_rule.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.combo_rules = ttk.Combobox(self.rules, values=rules)
        self.combo_rules.grid(row=1, column=0, padx=10, pady=5)
        self.combo_rules["state"] = "readonly"
        self.combo_rules.set(self.combo_rules["values"][0])

        self.add_button = ttk.Button(self.rules, text="Add rule",
                                    command=self.add_rule)
        self.add_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.label_rules = ttk.Label(self.rules, text="Rules")
        self.label_rules.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.list_rules = tk.Listbox(self.rules)
        self.list_rules.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.clear_button = ttk.Button(self.rules, text="Clear rules",
                                       command=self.clear_rules)
        self.clear_button.grid(row=5, column=0, padx=10, pady=(5, 10), sticky="w")
        self.clear_button["state"] = "disabled"
    
    def add_rule(self):
        self.list_rules.insert(tk.END, name := self.combo_rules.get())
        self._state.add_visitor(name)
        self.clear_button["state"] = "normal"
    
    def clear_rules(self):
        if not self._state.visitors: return
        self.list_rules.delete(0, tk.END)
        self._state.clear_visitors()
        self.clear_button["state"] = "disabled"


class StatusBar(CustomFrame):
    def __init__(self, parent, state = None):
        super().__init__(parent, state)
        # right
        ttk.Sizegrip(self).pack(side="right", anchor="se")
        ttk.Separator(self, orient='vertical').pack(side="right", padx=10)
        self.labelDatabase = ttk.Label(self, text=f"Database: {Client.get_client_info()}")
        self.labelDatabase.pack(side="right", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="right", padx=10)
        # left
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        self.labelSettings = ttk.Label(self, text=f"Settings: {self._state.settings_info()}")
        self.labelSettings.pack(side="left", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        # add observable
        self._state.attach(self)
    
    def on_update(self):
        self.labelDatabase["text"] = f"Database: {Client.get_client_info()}"
        self.labelSettings["text"] = f"Settings: {self._state.settings_info()}"


class AppGUI(tk.Tk):
    def __init__(self, state: AppState = None) -> None:
        # setup
        super().__init__()
        self.geometry("1280x640")
        self.minsize(1280,640)
        self.title("Equivalent Transformations")
        # menu
        self.menu = Menu(self, state)
        self.config(menu=self.menu._menubar)
        # tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side="top", fill="both", expand=True)
        
        self.refactorTab = RefactorTab(self.tabs, state)
        self.refactorTab.pack(fill="both", expand=True)
        self.settingsTab = SettingsTab(self.tabs, state, rules=api.all_visitor_names())
        self.databaseTab = DatabaseTab(self.tabs, state)
        
        self.tabs.add(self.refactorTab, text="Refactor")
        self.tabs.add(self.settingsTab, text="Settings")
        self.tabs.add(self.databaseTab, text="Database")
        # status bar
        self.statusBar = StatusBar(self, state)
        self.statusBar.pack(side="bottom", fill="x")
        # set theme
        sv_ttk.set_theme("dark")

    def run(self): self.mainloop()


class App:
    def __init__(self) -> None:
        self._app_state = AppState()
        self._app_GUI   = AppGUI(state=self._app_state)
        # set logging level
        logging.root.setLevel(logging.DEBUG)
        
    def run(self): self._app_GUI.run()
