#----------------
import logging
#----------------
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
#----------------
from .appstate import AppState
from .client import Client
from .controllers import MenuController, RefactorController, DatabaseController, SettingsController
from .helpers  import SyntaxHighlighter, NAVIGATION_KEYCODES
#----------------
from transformations import transformation_api as api
#----------------


class View(ttk.Frame):
    def __init__(self, parent, controller = None):
        super().__init__(parent)
        self.controller = controller


class CustomText(ttk.Frame):
    def __init__(self, parent, has_scrollbar = True):
        super().__init__(parent)
        # textbox
        self.textbox = ttk.Text(self, height=self.winfo_height(), width=self.winfo_width(), font=('FreeMono',12))
        SyntaxHighlighter.set_colors(self.textbox)
        # config
        if has_scrollbar:
            self.scrollbar = ttk.Scrollbar(self)
            self.scrollbar.config(command=self.textbox.yview)
            self.textbox['yscrollcommand'] = self.scrollbar.set

    def set_text(self, text: str):
        self.textbox['state'] = 'normal'
        self.textbox.delete(1.0, END )
        self.textbox.insert(END, text)
        self.textbox['state'] = 'disabled'

    def on_update(self):
        SyntaxHighlighter.highlight(self.textbox)


class SourceText(CustomText):
    def __init__(self, parent, has_scrollbar = True):
        super().__init__(parent, has_scrollbar)
        # key bindings
        self.textbox.bind("<KeyRelease>", self.on_update)
        # pack
        if has_scrollbar: self.scrollbar.pack(side="right", fill="y")
        self.textbox.pack(fill="both", expand=True)
    
    def on_update(self, event):
        if event.keycode in NAVIGATION_KEYCODES: return
        super().on_update()  # highlights syntax


class ResultText(CustomText):
    def __init__(self, parent, has_scrollbar = True):
        super().__init__(parent, has_scrollbar)
        self.textbox.config(state="disabled")
        # pack
        if has_scrollbar: self.scrollbar.pack(side="right", fill="y")
        self.textbox.pack(fill="both", expand=True)
    
    def on_update(self):
        super().set_text(AppState().str_result)
        super().on_update()  # highlights syntax


class DiffView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.text_original = ResultText(self, has_scrollbar=False)
        self.text_modified = ResultText(self, has_scrollbar=False)
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.config(command=self.scroll_command)
        self.text_original.textbox['yscrollcommand'] = self.scrollbar.set
        self.text_modified.textbox['yscrollcommand'] = self.scrollbar.set
        self.text_original.pack(fill="both", side="left", expand=True)
        self.text_modified.pack(fill="both", side="left", expand=True)
        self.scrollbar.pack(fill="y", side="right")
        
    def scroll_command(self, *args):
        self.text_original.textbox.yview(*args)
        self.text_modified.textbox.yview(*args)

    def set_diff(self, diff: list):
        original, modified = "", ""
        for line in diff:
            if line[0] == "-":
                original += f"{line}\n"; modified += f"\n"; 
                continue
            if line[0] == "+":
                modified += f"{line}\n"; original += f"\n"
                continue
            original += f"{line}\n"; modified += f"{line}\n"
        self.text_original.set_text(original)
        self.text_modified.set_text(modified)


class ASTView(ttk.Frame):
    def __init__(self, parent, target: str = None):
        super().__init__(parent)
        
        self.target = target
        # treeview widget
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
    
    def _generate_treeview(self, data: list):
        # insert treeview data
        for item in data:
            self.treeview.insert(parent=item[0], index=END, iid=item[1], text=item[2], values=item[3])
            if item[0] == "":  # open parent
                self.treeview.item(item[1], open=True)
        # select root
        self.treeview.selection_set(data[0][1])
        self.treeview.see(data[0][1])
    
    def on_update(self):
        self.treeview.delete(*self.treeview.get_children())
        
        self._generate_treeview(AppState().treeview_data(self.target))


class Menu(View):
    controller: MenuController
    
    def __init__(self, parent: ttk.Window, controller: MenuController):
        super().__init__(parent, controller)
        
        self._menubar = ttk.Menu(parent)
        # submenus
        self.filemenu = ttk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.filemenu.add_command(label="Close",
                command=self.on_close)
        self.aboutmenu = ttk.Menu(self._menubar, tearoff=0, font=('lucida', 10))
        self.aboutmenu.add_command(label="Usage",
                command=self.on_usage)
        # add cascade
        self._menubar.add_cascade(label="File",  menu=self.filemenu )
        self._menubar.add_cascade(label="About", menu=self.aboutmenu)
        self.parent = parent
    
    
    def on_close(self):
        self.controller.close()
        self.parent.destroy()

    
    def on_usage(self):
        logging.info('"on_usage" not implemented')


class RefactorTab(View):
    controller: RefactorController
    
    def __init__(self, parent, controller: RefactorController):
        super().__init__(parent, controller)
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
            command=lambda:self.controller.ast_show_source()
        ).grid(row=2, column=0, pady=10)
        # parse source ast button
        ttk.Button(self, text="Parse AST", width=20,
            command=lambda:self.controller.ast_parse(self.get_source_text())
        ).grid(row=2, column=1, pady=10)
        # transform button
        ttk.Button(self, text="Transform", width=20,
            command=lambda:self.controller.ast_transform()
        ).grid(row=2, column=2, pady=10)
        # show result ast button
        ttk.Button(self, text="Show Result AST", width=20,
            command=lambda:self.controller.ast_show_result()
        ).grid(row=2, column=3, pady=10)
        # add to observers
        AppState().attach(self)

    
    def get_source_text(self):
        return self.source_text.textbox.get('1.0', END)
    
    
    def set_source_text(self, text: str):
        self.source_text.set_text(text)
        
    
    def get_result_text(self):
        return self.result_text.textbox.get('1.0', END)
    
    
    def set_result_text(self, text: str):
        self.result_text.set_text(text)
        
    
    def on_update(self, event_type: str):
        if event_type == "ast_parse":
            self.source_tree.on_update()
        if event_type == "ast_transform":
            self.result_tree.on_update()
            self.result_text.on_update()


class DatabaseTab(View):
    controller: DatabaseController
    
    def __init__(self, parent, controller: DatabaseController):
        super().__init__(parent, controller)
        # page size for pagination
        self.page_size = 25
        
        self.label = ttk.Label(self, text='Documents: None')
        self.label.pack(side="top", fill="y", expand=False, padx=5, pady=5)
        
        if not (count := self.controller.document_count()): return
        self.count = count
        self.update_label()
        
        # fetch data
        cols, rows = self.controller.find_all(skip=0, limit=0)
        self._init_table(data=(cols,rows))
        self.diff_view = DiffView(self)
        self.diff_view.pack(fill="both", expand=True)
        
        # diff form widgets
        self.diff_form = ttk.Frame(self)
        self.diff_form.pack(fill="x")
        self.combo_select = ttk.Combobox(self.diff_form, width=25,)
        self.combo_select["state"] = "readonly"
        self.combo_select.grid(row=0, column=0, pady=10, padx=10)
        self.button_show = ttk.Button(self.diff_form, text="Show Diff", command=self.on_item_select)
        self.button_show.grid(row=0, column=1, pady=10)
        self._init_combo(cols)  # used to init the combo select values 


    def _init_table(self, data: tuple[list, list[tuple]]):
        cols, rows = data
        self.table = Tableview(
            self,
            coldata=cols,
            rowdata=rows,
            autofit=False,
            bootstyle=PRIMARY,
            paginated=True, pagesize=self.page_size
        )
        self.table.view.bind("<<TreeviewSelect>>", self.on_item_select)
        self.table.pack(fill="both", expand=True)


    def _init_combo(self, cols):
        self.combo_select["values"] = [ col['text']
                                    for col in cols
                                    if  col['text'] not in {"_id", "_source"} ]
        self.combo_select.set(self.combo_select["values"][0])


    def on_item_select(self, event = None):
        selected = self.table.view.selection()
        if len(selected) - 1:
            print("Can't select more than one item.")
            return
        row = self.table.view.item(selected)["values"]
        if not row: return
        id = row[0]
        if record := self.controller.find_one(id):
            self.update_diff_view(record, self.combo_select.get())


    def update_label(self) -> str:
        self.label["text"] = f"Documents: {self.count}"


    def update_diff_view(self, record : dict, key: str):
        if ("_source" not in record or 
                  key not in record or
                  key in {"_id", "_source"}):
            return
        source : str = record["_source"]
        result : str = record[key]

        diff = self.controller.get_diff(
            s := source.splitlines(),
            r := result.splitlines()
        )
        self.diff_view.set_diff(diff)
        # maybe do this with a separate button
        self.controller.create_diff_html(s, r)


class SettingsTab(View):
    controller: SettingsController
    
    def __init__(self, parent, controller: SettingsController, rules: list[str] = None):
        super().__init__(parent, controller)
        
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
        
        self.button_clear = ttk.Button(self.rules_custom, text="Clear Rules",
                                                command=self.clear_rules)
        self.button_clear.grid(row=1, column=0, padx=10, pady=10)
        self.button_clear["state"] = "disabled"
        
        self.button_delete = ttk.Button(self.rules_custom, text="Delete Rule",
                                                command=self.clear_rules)  # TODO
        self.button_delete.grid(row=1, column=1, padx=10, pady=10)
        self.button_delete["state"] = "disabled"
    
    
    def add_rule(self):
        self.list_rules.insert(tk.END, name := self.combo_rules.get())
        self.controller.add_rule(name)
        self.button_clear["state"] = "normal"
    
    
    def clear_rules(self):
        self.list_rules.delete(0, tk.END)
        self.controller.clear_rules()
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
        # add to observers
        AppState().attach(self)
    
    
    def on_update(self, event_type: str):
        if event_type == "client_change":
            self.label_database["text"] = f"Database: {Client().get_client_info()}"
        if event_type == "settings_change":
            self.label_settings["text"] = f"Settings: {AppState().settings_info()}"


class AppGUI(ttk.Window):
    def __init__(self,
                 menu_ctl: MenuController,
                 refactor_ctl: RefactorController,
                 database_ctl: DatabaseController,
                 settings_ctl: SettingsController,
                ) -> None:
        # setup
        super().__init__(themename="darkly")
        self.geometry("1280x640")
        self.minsize(1280,640)
        self.title("Equivalent Transformations")
        # menu
        self._create_menu_view(menu_ctl)
        # tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side="top", fill="both", expand=True)
        
        self.tab_refactor = RefactorTab(self.tabs, controller=refactor_ctl)
        self.tab_database = DatabaseTab(self.tabs, controller=database_ctl)
        self.tab_settings = SettingsTab(self.tabs, controller=settings_ctl,
                                        rules=api.all_visitor_names())
        
        self.tabs.add(self.tab_refactor, text="Refactor")
        self.tabs.add(self.tab_database, text="Database")
        self.tabs.add(self.tab_settings, text="Settings")
        # status bar
        self.statusbar = StatusBar(self)
        self.statusbar.pack(side="bottom", fill="x")
    
    
    def _create_menu_view(self, menu_ctl):
        self.menu = Menu(self, menu_ctl)
        self.config(menu=self.menu._menubar)
    
    
    def run(self):
        self.mainloop()
