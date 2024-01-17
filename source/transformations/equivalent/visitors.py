
import ast

from ast import AST, NodeVisitor, NodeTransformer, fix_missing_locations

from functools import wraps

from .changes import ForChange, InPlaceChange

from .rules import (
    ForToListComprehension,
    ForToDictComprehension,
    ForToSetComprehension,
    ForToSum,
    ForToSumNumpy,
    InvertIf,
    ExtractFunctionDefGuard,
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
        self,rule: ForToListComprehension
                 | ForToDictComprehension
                 | ForToSetComprehension
                 | ForToSum
                 | ForToSumNumpy
        ):
        self.rule = rule
        # node on which the transformer last ran
        self.node = None
        # init changed 
        self.changed = False
        # init results
        self.resutls : list[ForChange] = []
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
            # first visit to gather results
            self.visit(self.node)
            self.got_results = True
    
    # Set the results
    def __set_results(self) -> None:
        if self.got_results:
            for result in self.resutls:
                result.target.value = result.r_node
                self.changed = True
                print("Applyied:", result)  # TODO logger
            # visit again to remove for nodes
            self.visit(self.node)
            # this is neccessary to tell if there are any changes
            self.changed = bool(self.resutls)
    
    # Visitor for Assignment nodes
    def visit_Assign(self, node: AST):
        if self.got_results:
            return node
        
        print('-'*100)
        print(ast.dump(node, indent=2))
        print()
        
        result = self.rule.change(node)
        if result:
            self.resutls.append(result)
            
        print('-'*100)
        
        return node
    
    # Visitor for For nodes
    def visit_For(self, node: AST):
        if self.got_results:
            # remove the node if necessary
            if node in [result.remove for result in self.resutls]:
                return None
        # leave the node
        return node


class TIf(NodeTransformer):
    
    def __init__(
        self,rule: InvertIf
        ):
        self.rule = rule
        self.changed = False
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.changed = False
        self.visit(node)
    
    # Visitor for if nodes
    def visit_If(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        print()
        
        result = self.rule.change(node)
        
        if result:
            self.changed = True
            return result.r_node
        # leave unchanged        
        return node


class TFunctionDef(NodeTransformer):
    
    def __init__(
        self,rule: ExtractFunctionDefGuard
        ):
        self.rule = rule
        self.changed = False

    def transform_ast(self, node: AST):
        self.changed = False
        self.visit(node)
        # NOTE: IT'S VERY IMPORTANT TO FIX LOCATIONS OF GENERATED NODES
        # (ExtractFunctionDefGuard rule inserts an if statement into the generated function def)
        fix_missing_locations(node)
    
    # visit function definition
    def visit_FunctionDef(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        if result:
            self.changed = True
            return result.r_node
        # leave unchanged
        return node


class TLogic(NodeTransformer):
    
    def __init__(
        self,rule: DoubleNegation | DeMorgan
        ):
        self.rule = rule
        self.changed = False
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.changed = False
        self.visit(node)
    
    # Visitor for unary operators
    def visit_UnaryOp(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        
        if result:
            self.changed = True
            return result.r_node
        # leave unchanged
        return node
