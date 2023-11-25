import ast

import tkinter as tk

from tkinter import ttk

from graphviz import Digraph


class Menu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._menubar = tk.Menu(parent)
        self.filemenu = tk.Menu(self._menubar, tearoff=0)
        self.filemenu.add_command(label="Close", command=self.on_closing)
        self._menubar.add_cascade(label="File", menu=self.filemenu, font=('lucida',10))
        self.parent = parent
    
    def on_closing(self):
        self.parent.destroy()


class SourceWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.source_label = tk.Label(parent, text="Source", font=('lucida', 16))
        self.source_label.grid(
            row=0, column=0, padx=10, pady=10, columnspan=2
        )
        self.source_textbox = tk.Text(parent, height=21, width=42, font=('courier', 16))
        self.source_textbox.grid(
            row=1, column=0, padx=10, pady=10, columnspan=2
        )
        self.source_ast_button = tk.Button(parent, text="Show AST", font=('lucida', 14), command=self.show_ast)
        self.source_ast_button.grid(
            row=2, column=0, padx=10, pady=10
        )
        
        self.t_button = tk.Button(parent, text="Transform", font=('lucida', 16)) #command=)
        self.t_button.grid(
            row=2, column=1, padx=10, pady=10
        )

        self.parent = parent
        
    def show_ast(self):
        text = self.source_textbox.get('1.0', tk.END)
        
        parsed = ast.parse(text)

        if not parsed: print('Error while parsing.')
        
        print('-'*150)
        print(parsed)
        print('-'*150)
        print(ast.dump(parsed, indent=2))
        print('-'*150)
        
        DotGrapMaker.make(parsed)


class ResultWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.result_label = tk.Label(parent, text="Result", font=('lucida', 16))
        self.result_label.grid(
            row=0, column=2, padx=10, pady=10, columnspan=2
        )
        self.result_textbox = tk.Text(parent, height=21, width=42, font=('courier', 16))
        self.result_textbox.grid(
            row=1, column=2, padx=10, pady=10, columnspan=2
        )
        self.result_ast_button = tk.Button(parent, text="Show AST", font=('lucida', 14), command=self.show_ast)
        self.result_ast_button.grid(
            row=2, column=2, padx=10, pady=10, columnspan=2
        )
    
    def show_ast(self):
        text = self.result_textbox.get('1.0', tk.END)
        
        parsed = ast.parse(text)

        if not parsed: print('Error while parsing.')
        
        print('-'*150)
        print(parsed)
        print('-'*150)
        print(ast.dump(parsed, indent=2))
        print('-'*150)
        
        DotGrapMaker.make(parsed)


class App(tk.Tk):

    def __init__(self) -> None:
        # setup
        super().__init__()
        self.geometry("1150x640")
        self.maxsize(1150,640)
        self.minsize( 640,480)
        self.title("Equivalent Transformations")
        
        # menu
        self.menu = Menu(self)
        self.config(menu=self.menu._menubar)
        
        # widgets
        self.source_widget = SourceWidget(self)
        self.result_widget = ResultWidget(self)
        
        # run
        self.mainloop()


class DotGrapMaker:

    @staticmethod
    def make(parsed: ast.AST):
        # Create a Graphviz Digraph object
        dot = Digraph()

        # Define a function to recursively add nodes to the Digraph
        def add_node(node, parent=None):
            node_name = str(node.__class__.__name__)
            dot.node(str(id(node)), node_name)
            if parent:
                dot.edge(str(id(parent)), str(id(node)))
            for child in ast.iter_child_nodes(node):
                add_node(child, node)

        # Add nodes to the Digraph
        add_node(parsed)

        # Render the Digraph as a PNG file
        dot.format = 'png'
        dot.render('ast_graph', view=True)


if __name__ == "__main__":
    app = App()
