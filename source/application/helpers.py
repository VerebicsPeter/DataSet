import keyword, re             # for syntax highlighting
from tkinter import END,Text   # for syntax highlighting
from graphviz import Digraph   # for making graphs

NAVIGATION_KEYCODES = [36, 37, 111, 113, 114, 116]


class DigraphMaker:
    def __init__(self, iterator):
        self.iterator= iterator
    
    def add_node(self, node, parent=None):
        if not self.graph:
            return
        node_name = str(node.__class__.__name__)
        self.graph.node(
            str(id(node)),
            node_name
        )
        if parent:
            self.graph.edge(
                str(id(parent)),
                str(id(node))
            )
        for child in self.iterator(node):
            self.add_node(child, parent=node)

    def make(self, root) -> None:
        # create a Digraph object
        self.graph = Digraph()
        # add nodes to the Digraph object
        self.add_node(root)
        # render the Digraph as a PNG file
        self.graph.format = 'png'
        self.graph.render('ast_graph', view=True)


class SyntaxHighlighter:
    # patterns
    _keyword_pattern = r"\b(" + "|".join(keyword.kwlist) + r")\b"
    _strings_pattern = r"\"(\\.|[^\"\\])*\"|\'(\\.|[^\'\\])*\'"
    # compiled regex
    regex_keyword = re.compile(_keyword_pattern)
    regex_strings = re.compile(_strings_pattern)

    # NOTE: this is slow
    @classmethod
    def highlight(cls, textbox: Text):
        text_content = textbox.get("1.0", "end-1c")
        
        textbox.tag_remove("keyword", "1.0", END)
        textbox.tag_remove("strings", "1.0", END)
        
        for matched in cls.regex_keyword.finditer(text_content):
            start, end = f"1.0+{matched.start()}c", f"1.0+{matched.end()}c"
            textbox.tag_add("keyword", start, end)
        for matched in cls.regex_strings.finditer(text_content):
            start, end = f"1.0+{matched.start()}c", f"1.0+{matched.end()}c"
            textbox.tag_add("strings", start, end)
