
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
        # init starting node to None
        self._start_node = None
        # init results
        self.results: list[ForChange] = []
        self.got_results = False
    
    # Transform the AST in one call
    @context_parent
    def transform_ast(self, node: AST):
        self._start_node = node
        self.__get_results()
        self.__set_results()
    
    # Get the results by calling visitor
    def __get_results(self) -> None:
        if self._start_node:
            self.results = []
            self.got_results = False
            self.visit(self._start_node)
            self.got_results = True
    
    # Set the results
    def __set_results(self) -> None:
        if self.got_results:
            for result in self.results:
                print("Applying:", result)
                result.target.value = result.r_node
            # visit again to remove for nodes
            self.visit(self._start_node)
    
    # Visitor for Assignment nodes
    def visit_Assign(self, node: AST):
        if self.got_results:
            return node
        
        print('-'*100)
        print(ast.dump(node, indent=2))
        print()
        
        result = self.rule.change(node)
        # if the result matches, do semantic checks and store if possible
        if result:
            self.results.append(result)
            
        print('-'*100)
        
        return node
    
    # Visitor for For nodes
    def visit_For(self, node: AST):
        if self.got_results:
            # remove the node if necessary
            if node in [result.remove for result in self.results]:
                return None
        # leave the node
        return node


class TIf(NodeTransformer):
    
    def __init__(
        self,rule: InvertIf
        ):
        self.rule = rule
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.visit(node)
    
    # Visitor for if nodes
    def visit_If(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        print()
        
        result = self.rule.change(node)
        
        if result: return result.r_node
        # leave unchanged        
        return node


class TFunctionDef(NodeTransformer):
    
    def __init__(
        self,rule: ExtractFunctionDefGuard
        ):
        self.rule = rule

    def transform_ast(self, node: AST):
        self.visit(node)
        # NOTE: IT'S VERY IMPORTANT TO FIX LOCATIONS OF GENERATED NODES
        # (ExtractFunctionDefGuard rule inserts an if statement into the generated function def)
        fix_missing_locations(node)
    
    # visit function definition
    def visit_FunctionDef(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        if result: return result.r_node
        # leave unchanged
        return node


class TLogic(NodeTransformer):
    
    def __init__(
        self,rule: DoubleNegation | DeMorgan
        ):
        self.rule = rule
    
    # Transform the AST
    def transform_ast(self, node: AST):
        self.visit(node)
    
    # Visitor for unary operators
    def visit_UnaryOp(self, node: AST):
        print('-'*100)
        print(ast.dump(node, indent=2))
        
        result = self.rule.change(node)
        
        if result: return result.result
        # leave unchanged
        return node
