import ast

from ast import AST, NodeVisitor, NodeTransformer, fix_missing_locations

from functools import wraps

import logging

from .changes import ReduceFor, InPlace

from .rules import (
    ForRuleMaker,
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    ForToSumNumpy,
    InvertIf,
    GuardDef,
    DoubleNegation,
    DeMorgan,
)

# wrapper function that adds parent attributes
def context_parent(method):
    @wraps(method)
    def wrapper(self, root: AST):
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        method(self, root)
    return wrapper


class TFor(NodeTransformer):
    
    def __init__(
        self,
        rule: ForToListComprehension
            | ForToDictComprehension
            | ForToSetComprehension
            | ForToSum
            | ForToSumNumpy
    ):
        self.rule = rule
        self.changed = False
        # node on which the transformer last ran
        self.node = None
        # init results
        self.resutls : list[ReduceFor] = []
        self.got_results = False
    
    # Transform the AST in one call
    @context_parent
    def transform_ast(self, node: AST):
        self.node = node
        self.changed = False
        self.__get_results()
        self.__set_results()
    
    # Get the results by calling visitor
    def __get_results(self) -> None:
        if self.node:
            self.resutls = []
            self.got_results = False
            # NOTE: first visit to gather results
            self.visit(self.node)
            self.got_results = True
    
    # Set the results
    def __set_results(self) -> None:
        if self.got_results:
            for result in self.resutls:
                result.target.value = result.changed
                self.changed = True
                logging.info(f"applied: {result}")
            # NOTE: second visit to remove for nodes
            self.visit(self.node)
            # this is neccessary to tell if there are any changes
            self.changed = bool(self.resutls)
    
    # Visitor for Assignment nodes
    def visit_Assign(self, node: AST):
        if self.got_results:
            return node
        if result := self.rule.change(node): self.resutls.append(result)
        return node
    
    # Visitor for For nodes
    def visit_For(self, node: AST):
        if self.got_results:
            # remove the node if necessary
            if node in [result.remove for result in self.resutls]:
                return None
        # leave the node
        return node


class TFor2(NodeTransformer):
    def __init__(self):
        self.rule = ForRuleMaker.for_to_list_comp()
        self.node = None
        self.changed = False
        self.results : list[ReduceFor] = []


    def transform_ast(self, node: AST):
        self.node = node
        self.changed = False
        self.__get_results()
        self.__set_results()
    
    # Get the results by calling visitor
    def __get_results(self) -> None:
        if self.node:
            self.results.clear()
            # NOTE: first visit to gather results
            self.visit(self.node)
    
    # Set the results
    def __set_results(self) -> None:
        if self.results:
            for res in self.results:
                res.target.value = res.changed
                self.changed = True
                #logging.info(f"applied: {res}")
            # NOTE: second visit to remove for nodes
            self.visit(self.node)


    def generic_visit(self, node: AST):
        #log_node(node)
        super().generic_visit(node)
        if self.results and node in [res.remove for res in self.results]:
            # remove the node
            return None
        if rs := self.rule.change(node): self.results.extend(rs)
        return node


class TSimple(NodeTransformer):
    
    def __init__(
        self,
        rule: InvertIf
            | GuardDef
            | DoubleNegation
            | DeMorgan
    ):
        self.rule = rule
        self.changed = False
    
    def transform_ast(self, node: AST):
        self.changed = False
        # start traversal
        self.visit(node)
        # NOTE: IT'S VERY IMPORTANT TO FIX LOCATIONS OF GENERATED NODES
        # (GuardDef rule inserts an if statement into the generated function def)
        fix_missing_locations(node)
    
    def generic_visit(self, node: AST):
        #log_node(node)
        super().generic_visit(node)
        if result := self.rule.change(node):
            self.changed = True
            return result.changed
        return node


def log_node(node):
    logging.debug('-'*100)
    logging.debug(f"\n{ast.dump(node, indent=2)}")
    logging.debug('-'*100)
