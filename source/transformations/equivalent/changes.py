# Implementations of rules' change return types

import ast

from dataclasses import dataclass

@dataclass
class InPlaceChange:
    r_node: ast.AST

@dataclass
class ForChange:
    target: ast.Assign
    remove: ast.For
    r_node: ast.AST
