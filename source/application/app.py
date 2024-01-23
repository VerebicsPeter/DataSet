    # TODO: have the rule selector thing be below the refactoring tab, align the buttons horizontally!

from typing import Protocol

import logging

import keyword, re  # for syntaxt highlighting

import tkinter as tk

from tkinter import ttk, messagebox

import sv_ttk  # tkinter theme

import uuid  # for generating generating treeview ids

from graphviz import Digraph  # for rendering graphs

from transformations import transformation_api as api


class Observable(Protocol):
    @classmethod
    def attach(observer):
        ...
    @classmethod
    def notify():
        ...


class Observer(Protocol):
    def on_update(self):
        ...

class Menu(ttk.Frame):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
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


class TreeView(ttk.Frame):
    def __init__(self, parent, target: str):
        super().__init__(parent)
        
        self.data = []
        self.target = target
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        
        # Treeview
        self.treeview = ttk.Treeview(
            self, columns=(1),
            selectmode="browse", height=self.winfo_height(),
            yscrollcommand=self.scrollbar.set
        )
        self.treeview.pack(expand=True, fill="both")
        
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview.column("#0", anchor="w", width=50)
        self.treeview.column("#1", anchor="w", width=50)

        # Treeview headings
        self.treeview.heading("#0", text="Node type", anchor="center")
        self.treeview.heading("#1", text="Node value", anchor="center")
    
    def on_update(self):
        self.treeview.delete(*self.treeview.get_children())
        
        self.data = AppState.treeview_data(self.target)
        
        if len(self.data) == 0: return
        
        # Insert treeview data
        for item in self.data:
            self.treeview.insert(
                parent=item[0], index='end', iid=item[1], text=item[2], values=item[3]
            )
            if item[0] == "":
                self.treeview.item(item[1], open=True)  # Open parent
        
        # Select root
        self.treeview.selection_set(self.data[0][1])
        self.treeview.see(self.data[0][1])


class SourceText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")

        self.textbox = tk.Text(self, height=self.winfo_height(),
            font=('FreeMono', 14)
        )
        self.textbox.tag_config("keyword", foreground="purple")
        self.textbox.tag_config("strings", foreground="goldenrod")
        self.textbox.tag_config("comment", foreground="green")
        self.textbox.bind("<KeyRelease>", self.on_update)
        self.textbox.pack(fill="both", expand=True)
        
        self.scrollbar.config(command=self.textbox.yview)
        self.textbox['yscrollcommand'] = self.scrollbar.set
        
    def on_update(self, event = None):
        SyntaxHighlighter.highlight(self.textbox)


class ResultText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.scrollBar = ttk.Scrollbar(self)
        self.scrollBar.pack(side="right", fill="y")

        self.textbox = tk.Text(self, height=self.winfo_height(),
            font=('FreeMono', 14)
        )
        self.textbox.config(
            state="disabled"
        )
        self.textbox.tag_config("keyword", foreground="purple")
        self.textbox.tag_config("strings", foreground="goldenrod")
        self.textbox.tag_config("comment", foreground="green")
        self.textbox.pack(fill="both", expand=True)
        
        self.scrollBar.config(command=self.textbox.yview)
        self.textbox['yscrollcommand'] = self.scrollBar.set

    def on_update(self):
        SyntaxHighlighter.highlight(self.textbox)


class RefactorTab(ttk.Frame):
    def __init__(self, parent: tk.Tk):
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
        self.source_text_widget = SourceText(self)
        self.source_text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.source_tree_widget = TreeView(self, "source")
        self.source_tree_widget.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # result widgets
        self.result_text_widget = ResultText(self)
        self.result_text_widget.grid(row=0, column=2, columnspan=2, sticky="nsew")
        
        self.result_tree_widget = TreeView(self, "result")
        self.result_tree_widget.grid(row=1, column=2, columnspan=2, sticky="nsew")
        # show source ast button
        self.show_ast_button = ttk.Button(self, text="Show AST", width=20,
            command=self.ast_show_source
        ).grid(row=2, column=0, pady=10)
        
        # parse source ast button
        self.parse_ast_button = ttk.Button(self, text="Parse AST", width=20,
            command=lambda:self.ast_parse('source')
        ).grid(row=2, column=1, pady=10)
        
        # transform button
        self.transform_button = ttk.Button(self, text="Transform", width=20,
            command=self.ast_transform
        ).grid(row=2, column=2, pady=10)
        
        # show result ast button
        self.show_ast_button = ttk.Button(self, text="Show AST", width=20, 
            command=self.ast_show_result
        ).grid(row=2, column=3, pady=10)
        
    def ast_parse(self, target: str) -> None:
        text: str = self.source_text_widget.textbox.get('1.0', tk.END)
        # parse new ast into the state object
        AppState.parse_ast(text, target)
        # update the tree view
        self.source_tree_widget.on_update()

    def ast_transform(self) -> None:
        if AppState.ast_source:
            visitors = AppState.visitors
            if len(visitors):
                AppState.ast_result = api.CopyTransformer(AppState.ast_source)\
                    .apply_visitors(visitors)\
                    .ast
            else:
                AppState.ast_result = api.CopyTransformer(AppState.ast_source)\
                    .apply_all()\
                    .ast
            # maybe use a try block
            unparsed = api.unparse(AppState.ast_result)
            # update text widget
            self.result_text_widget.textbox['state'] = 'normal'
            self.result_text_widget.textbox.delete(1.0   ,   tk.END)
            self.result_text_widget.textbox.insert(tk.END, unparsed)
            self.result_text_widget.textbox['state'] = 'disabled'
            self.result_text_widget.on_update()
            # update the tree view
            self.result_tree_widget.on_update()
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")

    def ast_show_source(self) -> None:
        if AppState.ast_source:
            DigraphMaker.make(AppState.ast_source)
        else:
            messagebox.showinfo(title="Show AST", message="No AST provided.")

    def ast_show_result(self) -> None:
        if AppState.ast_result: 
            DigraphMaker.make(AppState.ast_result)
        else:
            messagebox.showinfo(title="Show AST", message="No AST generated.")


class DatabaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.placeholder1 = ttk.Label(self,text='Welcome to DB access page!')\
            .pack(ipadx=10, ipady=10)
        self.placeholder2 = ttk.Label(self,
            text=f'Connection: {AppState.connection}' + ', ' + f'Documents: {AppState.get_count()}')\
            .pack(ipadx=10, ipady=10)


class SettingsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        rules = [ name for name in api.all_visitor_names() ]
        
        self.rules = ttk.Labelframe(self, text="Custom Rules")
        self.rules.grid(row=0, column=0, padx=10, pady=10)
        
        self.labelRule = ttk.Label(self.rules, text="New rule")
        self.labelRule.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.comboRules = ttk.Combobox(self.rules, values=rules)
        self.comboRules.grid(row=1, column=0, padx=10, pady=5)
        self.comboRules["state"] = "readonly"
        self.comboRules.set(self.comboRules["values"][0])

        self.addButton = ttk.Button(self.rules, text="Add rule", command=self.add_rule)
        self.addButton.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.labelRules = ttk.Label(self.rules, text="Rules")
        self.labelRules.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.listRules = tk.Listbox(self.rules)
        self.listRules.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.clearButton = ttk.Button(self.rules, text="Clear rules", command=self.clear_rules)
        self.clearButton.grid(row=5, column=0, padx=10, pady=(5, 10), sticky="w")
        self.clearButton["state"] = "disabled"
    
    def add_rule(self):
        self.listRules.insert(tk.END, name := self.comboRules.get())
        AppState.add_visitor(api.create_visitor(name))
        self.clearButton["state"] = "normal"
        
    def clear_rules(self):
        if not len(AppState.visitors): return
        AppState.clear_visitors()
        self.listRules.delete(0, tk.END)
        self.clearButton["state"] = "disabled"


class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # left
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        self.labelSettings = ttk.Label(self, text=f"Settings: {AppState.get_settings()}")
        self.labelSettings.pack(side="left", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="left", padx=10)
        
        # right
        ttk.Sizegrip(self).pack(side="right", anchor="se")
        
        ttk.Separator(self, orient='vertical').pack(side="right", padx=10)
        self.labelConnection = ttk.Label(self, text=f"Database: {AppState.get_connection()}")
        self.labelConnection.pack(side="right", padx=0, pady=3)
        ttk.Separator(self, orient='vertical').pack(side="right", padx=10)
        
        # add observable
        AppState.attach(self)
    
    def on_update(self):
        self.labelConnection["text"] = f"Database: {AppState.get_connection()}"
        self.labelSettings  ["text"] = f"Settings: {AppState.get_settings()}"


class App(tk.Tk):
    def __init__(self) -> None:
        # setup
        super().__init__()
        self.geometry("1280x640")
        self.minsize(1280,640)
        self.title("Equivalent Transformations")
        # menu
        self.menu = Menu(self)
        self.config(menu=self.menu._menubar)
        # tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side="top", fill="both", expand=True)
        
        self.refactorTab = RefactorTab(self.tabs)
        self.refactorTab.pack(fill="both", expand=True)
        self.settingsTab = SettingsTab(self.tabs)
        self.databaseTab = DatabaseTab(self.tabs)
        
        self.tabs.add(self.refactorTab, text="Refactor")
        self.tabs.add(self.settingsTab, text="Settings")
        self.tabs.add(self.databaseTab, text="Database")
        # status bar
        self.statusBar = StatusBar(self)
        self.statusBar.pack(side="bottom", fill="x")
        # set theme
        sv_ttk.set_theme("dark")
        # set logging level
        logging.root.setLevel(logging.DEBUG)
        
    def run(self): self.mainloop()


class AppState(Observable):
    connection = None
    ast_source = None
    ast_result = None
    observers: list[Observer] = []
    visitors: list[api.NodeVisitor] = []
    
    @classmethod
    def set_connection(cls, connection):
        cls.connection = connection
    
    @classmethod
    def get_connection(cls) -> str:
        if cls.connection: return f"{cls.connection.HOST}:{cls.connection.PORT}"
    
    @classmethod
    def get_count(cls):
        if cls.connection:
            db = cls.connection.refactoring
            return db.equivalent.count_documents({})
    
    @classmethod
    def get_settings(cls) -> str:
        return "custom" if len(cls.visitors) else "default (all)"
    
    @classmethod
    def parse_ast(cls, source: str, target: str) -> None:
        if target not in {'source', 'result'}: return
        
        try:
            parsed = api.parse(source)
        except Exception as exception:
            print('Error while parsing:')
            print(exception)
            match exception:
                case SyntaxError():
                    messagebox.showinfo(title="Syntax Error", message=f"Syntax error: {exception.msg} in line {exception.lineno}.")
                case _:
                    messagebox.showinfo(title="Parsing Error", message="Parsing failed.")
            return
        
        if target=='source':
            cls.ast_source = parsed
        if target=='result':
            cls.ast_result = parsed
        
        logging.debug('-'*100)
        logging.debug(parsed)
        logging.debug('-'*100)
        logging.debug(f"\n{api.dump(parsed, indent=2)}")
        logging.debug('-'*100)
    
    @classmethod
    def attach(cls, observer):
        cls.observers.append(observer)

    @classmethod
    def notify(cls):
        for observer in cls.observers:
            observer.on_update()
    
    @classmethod
    def add_visitor(cls, visitor) -> None:
        cls.visitors.append(visitor)
        cls.notify()
    
    @classmethod
    def pop_visitor(cls) -> object:
        # TODO
        pass
    
    @classmethod
    def clear_visitors(cls):
        cls.visitors.clear()
        cls.notify()

    @classmethod
    def treeview_data(cls, target: str) -> list:
        data = []
        
        root = None
        if target not in {'source', 'result'}: return data
        if target == 'source': root = cls.ast_source
        if target == 'result': root = cls.ast_result
        
        if not root: print("No AST provided."); return data
        
        def node_text(node):
            unparsed = api.unparse(node)
            if len(unparsed) < 30:
                return unparsed.split('\n', 1)[0]
            else:
                return unparsed[:30].split('\n', 1)[0]+'...'

        def add_node(node, parent=None):
            node_name = str(node.__class__.__name__)
            node.uuid = uuid.uuid4()
            if parent:
                data.append((parent.uuid,
                    node.uuid, node_name, (node_text(node),))
                )
            else:
                data.append(("",
                    node.uuid, node_name, (node_text(node),))
                )
            for child in api.iter_child_nodes(node):
                add_node(child, node)
        
        add_node(root)
        return data


class DigraphMaker:

    @staticmethod
    def make(root: api.AST) -> None:
        def add_node(node, parent=None):
            node_name = str(node.__class__.__name__)
            dot.node(str(id(node)),node_name)
            if parent:
                dot.edge(str(id(parent)),str(id(node)))
            for child in api.iter_child_nodes(node):
                add_node(child, node)
        # create a Digraph object
        dot = Digraph()
        # add nodes to the Digraph
        add_node(root)
        # render the Digraph as a PNG file
        dot.format = 'png'
        dot.render('ast_graph', view=True)


class SyntaxHighlighter:
    # patterns
    _keyword_pattern = r"\b(" + "|".join(keyword.kwlist) + r")\b"
    _strings_pattern = r"\"(\\.|[^\"\\])*\"|\'(\\.|[^\'\\])*\'"
    # compiled regex
    regex_keyword = re.compile(_keyword_pattern)
    regex_strings = re.compile(_strings_pattern)

    # NOTE: this is slow
    @classmethod
    def highlight(cls, textbox: tk.Text):
        text_content = textbox.get("1.0", "end-1c")
        
        textbox.tag_remove("keyword", "1.0", tk.END)
        textbox.tag_remove("comment", "1.0", tk.END)
        textbox.tag_remove("strings", "1.0", tk.END)
        
        for matched in cls.regex_keyword.finditer(text_content):
            start, end = f"1.0+{matched.start()}c", f"1.0+{matched.end()}c"
            textbox.tag_add("keyword", start, end)
        for matched in cls.regex_strings.finditer(text_content):
            start, end = f"1.0+{matched.start()}c", f"1.0+{matched.end()}c"
            textbox.tag_add("strings", start, end)
