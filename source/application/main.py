import ast

from dataclasses import dataclass

import tkinter as tk

from tkinter import ttk, messagebox

import sv_ttk

import uuid

from graphviz import Digraph

import transformations.transform_api as api


class Menu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._menubar = tk.Menu(parent)
        # submenus
        self.filemenu = tk.Menu(self._menubar, tearoff=0, font=('lucida, 10'))
        self.filemenu.add_command(label="Close", command=self.on_close)
        self.aboutmenu = tk.Menu(self._menubar, tearoff=0, font=('lucida, 10'))
        self.aboutmenu.add_command(label="Usage", command=self.on_about)
        # add cascade
        self._menubar.add_cascade(label="File", menu=self.filemenu)
        self._menubar.add_cascade(label="About", menu=self.aboutmenu)
        self.parent = parent
    
    def on_close(self):
        self.parent.destroy()
    
    def on_about(self):
        print('`on_about` not implemented')


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
                self.treeview.item(item[1], open=True) # Open parent
        
        # Select root
        self.treeview.selection_set(self.data[0][1])
        self.treeview.see(self.data[0][1])


class SourceText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.textbox = tk.Text(self, height=self.winfo_height(), width=self.winfo_width(),
            font=('consolas', 14)
        )
        self.textbox.pack(fill="both", expand=True)


class SourceInputs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # parse ast button
        self.parse_ast_button = ttk.Button(self, text="Parse AST", width=20,
            command=lambda:parent.ast_parse('source')
        )
        self.parse_ast_button.pack(pady=3)
        
        # show ast button
        self.show_ast_button = ttk.Button(self, text="Show AST", width=20,
            command=parent.ast_show_source
        )
        self.show_ast_button.pack(pady=3)
        
        # transform button
        self.transform_button = ttk.Button(self, text="Transform", width=20,
            command=parent.ast_transform
        )
        self.transform_button.pack(pady=3)


class ResultText(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.textbox = tk.Text(self, height=self.winfo_height(), width=self.winfo_width(),
            font=('consolas', 14)
        )
        self.textbox.config(
            state="disabled"
        )
        self.textbox.pack(fill="both", expand=True)


class ResultInputs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # parse ast button
        self.show_ast_button = ttk.Button(self, text="Show AST", width=20,
            command=parent.ast_show_result
        )
        self.show_ast_button.pack()


@dataclass
class TransformView():
    text: SourceText | ResultText
    inputs: SourceInputs | ResultInputs
    treeview: TreeView


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
        # rows and columns
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        # widgets
        self.source_text_widget = SourceText(self)
        self.source_text_widget.grid(row=0, column=0, sticky="nsew")
        self.result_text_widget = ResultText(self)
        self.result_text_widget.grid(row=0, column=1, sticky="nsew")
        self.source_tree_widget = TreeView(self, "source")
        self.source_tree_widget.grid(row=1, column=0, sticky="nsew")
        self.result_tree_widget = TreeView(self, "result")
        self.result_tree_widget.grid(row=1, column=1, sticky="nsew")
        self.source_input_widget = SourceInputs(self)
        self.source_input_widget.grid(row=2, column=0)
        self.result_input_widget = ResultInputs(self)
        self.result_input_widget.grid(row=2, column=1)
        # dict of widgets
        self.views: dict[str, TransformView] = {}
        
        self.views['source'] = TransformView(
            self.source_text_widget,
            self.source_input_widget,
            self.source_tree_widget
        )
        self.views['result'] = TransformView(
            self.result_text_widget,
            self.result_input_widget,
            self.result_tree_widget
        )
        # set theme
        sv_ttk.set_theme("dark")
        # run
        self.mainloop()


    def ast_parse(self, target: str) -> None:
        if target not in {'source', 'result'}: return
        text: str = self.views[target].text.textbox.get('1.0', tk.END)
        AppState.parse_ast(text,target)
        # update the tree view
        self.views[target].treeview.on_update()


    def ast_transform(self) -> None:
        if AppState.source_ast:
            AppState.result_ast = api.for_to_comprehension(AppState.source_ast)
            # maybe use a try except
            unparsed = ast.unparse(AppState.result_ast)
            self.result_text_widget.textbox['state'] = 'normal'
            self.result_text_widget.textbox.delete(1.0,    tk.END)
            self.result_text_widget.textbox.insert(tk.END, unparsed)
            self.result_tree_widget.on_update()
            self.result_text_widget.textbox['state'] = 'disabled'
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")


    def ast_show_source(self) -> None:
        if AppState.source_ast: 
            DotGrapMaker.make(AppState.source_ast)
        else:
            messagebox.showinfo(title="Transform", message="No AST provided.")


    def ast_show_result(self) -> None:
        if AppState.result_ast: 
            DotGrapMaker.make(AppState.result_ast)
        else:
            messagebox.showinfo(title="Transform", message="No AST generated.")


class AppState:
    source_ast = None
    result_ast = None
    
    @classmethod
    def parse_ast(cls, source: str, target: str, show_image: bool = False) -> None:
        if target not in {'source', 'result'}: return
        
        try:
            parsed = ast.parse(source)
        except Exception as exeception:
            print('Error while parsing:');print(exeception)
            messagebox.showinfo(title="Transform", message=exeception)
            return
        
        if target=='source':
            cls.source_ast = parsed
        if target=='result':
            cls.result_ast = parsed
        
        print('-'*150)
        print(parsed)
        print('-'*150)
        print(ast.dump(parsed, indent=2))
        print('-'*150)
        
    
    @classmethod
    def treeview_data(cls, target: str) -> list:
        data = []
        
        root = None
        if target not in {'source', 'result'}: return data
        if target == 'source': root = cls.source_ast
        if target == 'result': root = cls.result_ast
        
        if not root: print("No AST provided."); return data
        
        def node_text(node):
            unparsed = ast.unparse(node)
            if len(unparsed) < 30:
                return unparsed.split('\n', 1)[0]
            else:
                return unparsed[:30].split('\n', 1)[0]+' ... '

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
            for child in ast.iter_child_nodes(node):
                add_node(child, node)
        
        add_node(root)
        return data


class DotGrapMaker:

    @staticmethod
    def make(root: ast.AST) -> None:
        # create a Digraph object
        dot = Digraph()
        def add_node(node, parent=None):
            node_name = str(node.__class__.__name__)
            dot.node(str(id(node)),node_name)
            if parent:
                dot.edge(str(id(parent)),str(id(node)))
            for child in ast.iter_child_nodes(node):
                add_node(child, node)
        # add nodes to the Digraph
        add_node(root)
        # render the Digraph as a PNG file
        dot.format = 'png'
        dot.render('ast_graph', view=True)


if __name__ == "__main__":
    # create app
    app = App()
