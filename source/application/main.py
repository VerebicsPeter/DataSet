import tkinter as tk

import ast

from graphviz import Digraph


class ApplicationGUI:

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("Equivalent Transformations")

        self.menubar = tk.Menu(self.root)
        self.appmenu = tk.Menu(self.menubar, tearoff=0)
        self.appmenu.add_command(label="Close", command=self.on_closing)
        self.menubar.add_cascade(label="App", menu=self.appmenu)

        self.root.config(menu=self.menubar)

        self.label = tk.Label(self.root, text="Source", font=('Arial', 20))
        self.label.pack(padx=20, pady=20)

        self.textbox = tk.Text(self.root, height=20, font=('Consolas', 16))
        self.textbox.pack(padx=10, pady=10)

        self.button = tk.Button(self.root, text="Get AST", font=(
            'Arial', 16), command=self.show_ast)
        self.button.pack(padx=10, pady=10)

        self.root.mainloop()

    def show_ast(self):
        text = self.textbox.get('1.0', tk.END)

        parsed = ast.parse(text)

        if not parsed:
            print('Error while parsing.')
        
        print('-'*150)
        print(parsed)
        print('-'*150)
        print(ast.dump(parsed, indent=2))
        print('-'*150)
        
        DotGrapMaker.make(parsed)

    def on_closing(self):
        self.root.destroy()


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

    app = ApplicationGUI()
