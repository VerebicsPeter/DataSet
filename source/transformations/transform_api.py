import copy

from transformations.equivalent.t_complex import (
    AST, NodeTransformation, NodeVisitor
)

from transformations.equivalent.visitors import (
    ForTransformer,
    IfTransformer,
    LogicTransformer
)

from transformations.equivalent.rules import (
    ForToListComprehension,
    ForToDictComprehension,
    InvertIfOrElse,
    RemoveDoubleNegation,
)


class TransformationQueue:
    
    def __init__(self, initial_ast: AST) -> None:
        self.ast = initial_ast
        self.queue = []
        self.transformation = NodeTransformation(initial_ast)
    
    def add(self, visitor: NodeVisitor):
        self.queue.append(visitor)
        return self
    
    def run(self):
        while self.queue:
            visitor = self.queue.pop(0)
            self.transformation.transform_nodes(visitor)


class TransformationChain():

    def __init__(self, ast: AST):
        self.ast = copy.deepcopy(ast)

    def for_to_comprehension(self):
        transformation = TransformationQueue(self.ast)
        (
            transformation
            .add(ForTransformer(ForToListComprehension()))
            .add(ForTransformer(ForToDictComprehension()))
            .run()
        )
        return self

    def invert_if_orelse(self):
        transformation = TransformationQueue(self.ast)
        (
            transformation
            .add(IfTransformer(InvertIfOrElse()))
            .add(LogicTransformer(RemoveDoubleNegation()))
            .run()
        )
        return self
