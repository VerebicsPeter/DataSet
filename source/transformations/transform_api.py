import copy

from transformations.equivalent.t_complex import (
    ForTransformation, ForTransformer,
    IfTransformation, IfTransformer,
    LogicTransformation, LogicTransformer,
    AST
)

from transformations.equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension,
    InvertIfOrElse,
    EliminateDoubleNegation
)

def for_to_comprehension(ast: AST):
    ast_copy = copy.deepcopy(ast)
    transformation = ForTransformation(ast_copy)
    transformation.transform_nodes(ForTransformer(ForToListComprehension()))
    transformation.transform_nodes(ForTransformer(ForToDictComprehension()))
    return transformation.ast

def invert_if_orelse(ast: AST):
    ast_copy = copy.deepcopy(ast)
    transformation = IfTransformation(ast_copy)
    transformation.transform_nodes(IfTransformer(InvertIfOrElse()))
    return transformation.ast

def doulbe_negation(ast: AST):
    ast_copy = copy.deepcopy(ast)
    transformation = LogicTransformation(ast_copy)
    transformation.transform_nodes(LogicTransformer(EliminateDoubleNegation()))
    return transformation.ast
