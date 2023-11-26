import copy

from transformations.equivalent.t_complex import (
    ForNodeTransformation,
    ForTransformer,
    AST
)

from transformations.equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension
)

def for_to_comprehension(ast: AST):
    ast_copy = copy.deepcopy(ast)
    transformation = ForNodeTransformation(ast_copy)
    transformation.transform_nodes(ForTransformer(ForToListComprehension()))
    transformation.transform_nodes(ForTransformer(ForToDictComprehension()))
    return transformation.ast
