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

    def apply_for_to_comprehension(self):
        diff= for_to_comprehension(self.ast)
        self.changed = self.changed or diff
        return self

    def apply_invert_if(self):
        diff= invert_if(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_def_guard(self):
        diff= def_guard(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_logic_rules(self):
        diff= logic_rules(self.ast)
        self.changed = self.changed or diff
        return self
    
    def apply_all(self):
        diff= all_transformations(self.ast)
        self.changed = self.changed or diff
        return self


def safe_parse(source: str):
    try:
        return ast.parse(source)
    except Exception as exception: print(exception)


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


def all_transformations(node: AST) -> bool:
    t = TransformationBuilder(node)\
        .add(TFor(ForToListComprehension()))\
        .add(TFor(ForToDictComprehension()))\
        .add(TFor(ForToSetComprehension()))\
        .add(TFor(ForToSum()))\
        .add(TFunctionDef(ExtractFunctionDefGuard()))\
        .add(TIf(InvertIf()))\
        .add(TLogic(DoubleNegation()))\
        .add(TLogic(DeMorgan()))\
        .run()
    return t.changed


def get_all_visitors() -> list:
    visitors = list()
    
    visitors.append({
        "name": "For to list comprehension", "visitor": TFor(ForToListComprehension())
    })
    
    visitors.append({
        "name": "For to dict comprehension", "visitor": TFor(ForToDictComprehension())
    })
    
    visitors.append({
        "name": "For to set comprehension", "visitor": TFor(ForToSetComprehension())
    })
    
    visitors.append({
        "name": "For to sum", "visitor": TFor(ForToSum())
    })
    
    visitors.append({
        "name": "Extract guard", "visitor": TFunctionDef(ExtractFunctionDefGuard())
    })
    
    visitors.append({
        "name": "Invert if", "visitor": TIf(InvertIf())
    })
    
    visitors.append({
        "name": "Double negation", "visitor": TIf(InvertIf())
    })
    
    visitors.append({
        "name": "De Morgan's law", "visitor": TIf(InvertIf())
    })
    
    return visitors
