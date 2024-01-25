import ast

from ast import parse, unparse, dump, iter_child_nodes, AST

import copy

from typing import Protocol

from transformations.transformation import (
    AST, NodeVisitor
)

from transformations.equivalent.visitors import (
    TFor, TIf, TFunctionDef, TLogic
)

from transformations.equivalent.rules import (
    # for rules
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    # if rules
    InvertIf,
    # function def rules
    ExtractFunctionDefGuard,
    # logic rules
    DoubleNegation,
    DeMorgan
)

class CustomVisitor(Protocol):
    # changed indicates whether the visitor made any changes to the AST
    changed: bool
    
    def transform_ast(node: AST):
        ...

class TransformationBuilder:
    
    def __len__(self): return len(self._queue)
    
    def __init__(self, ast: AST = None) -> None:
        self._ast = ast
        self._queue: list[CustomVisitor] = []
        self.changed = False
    
    def set_ast(self, ast: AST) -> None:
        self._ast = ast
    
    def get_ast(self) -> AST | None: return self._ast
    
    def add_one(self, visitor: NodeVisitor):
        self._queue.append(visitor)
        return self
    
    def add(self, *visitors: NodeVisitor):
        self._queue.extend(visitors)
        return self
    
    def run(self):
        if not self._ast:
            print("AST needed for running the transformation!")
            return
        
        while self._queue:
            visitor = self._queue.pop(0)
            visitor.transform_ast(self._ast)
            self.changed = self.changed or visitor.changed
        return self


class CopyTransformer():

    def __init__(self, ast: AST):
        self.ast = copy.deepcopy(ast)
        self.changed = False
    
    def change(self) -> str:
        """Returns the changed source if any changes occured, or an empty string otherwise.
        """
        if not self.changed:
            return ""
        return unparse(self.ast)
    
    def apply_all(self):
        diff= all_transformations(self.ast)
        self.changed = self.changed or diff
        return self

    def apply_visitors(self, visitors):
        diff= transform(self.ast, visitors)
        self.changed = self.changed or diff
        return self

    def apply_preset(self, function):
        diff= function(self.ast)
        self.changed = self.changed or diff
        return self


def safe_parse(source: str):
    try:
        return ast.parse(source)
    except Exception as exception: print(exception)

# Transformations

def all_transformations(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(*[create_visitor(name) for name in all_visitor_names()])\
        .run()
    return t.changed

def transform(node: AST, visitors) -> bool:
    t = TransformationBuilder(node).add(*visitors).run()
    return t.changed

# Transformation "presets"

def for_to_comprehension(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(TFor(ForToListComprehension()))\
        .add(TFor(ForToDictComprehension()))\
        .add(TFor(ForToSetComprehension()))\
        .add(TFor(ForToSum()))\
        .run()
    return t.changed

def invert_if(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(TIf(InvertIf()))\
        .run()
    return t.changed

def def_guard(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(TFunctionDef(ExtractFunctionDefGuard()))\
        .run()
    return t.changed
    
def logic_rules(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(TLogic(DoubleNegation()))\
        .add(TLogic(DeMorgan()))\
        .run()
    return t.changed

# Helpers

def all_visitor_names() -> list[str]:
    return [
        "For to list comprehension",
        "For to dict comprehension",
        "For to set comprehension",
        "For to sum",
        "Extract guard",
        "Invert if",
        "Double negation",
        "De Morgan's law",
    ]

def create_visitor(name: str):
    if name == "For to list comprehension":
        return TFor(ForToListComprehension())
    elif name == "For to dict comprehension":
        return TFor(ForToDictComprehension())
    elif name == "For to set comprehension":
        return TFor(ForToSetComprehension())
    elif name == "For to sum":
        return TFor(ForToSum())
    elif name == "Extract guard":
        return TFunctionDef(ExtractFunctionDefGuard())
    elif name == "Invert if":
        return TIf(InvertIf())
    elif name == "Double negation":
        return TLogic(DoubleNegation())
    elif name == "De Morgan's law":
        return TLogic(DeMorgan())
    else:
        raise ValueError(f"Unknown visitor name: {name}")
