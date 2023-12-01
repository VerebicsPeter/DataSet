import copy

from transformations.equivalent.transformation import (
    AST, NodeTransformation, NodeVisitor
)

from transformations.equivalent.visitors import (
    ForTransformer,IfTransformer,FunctionDefTransformer,
    LogicTransformer
)

from transformations.equivalent.rules import (
    # for rules
    ForToListComprehension,
    ForToDictComprehension,
    ForToSum,
    # if rules
    InvertIf,
    # function def rules
    ExtractFunctionDefGuard,
    # logic rules
    DoubleNegation,DeMorgan
)

class TransformationBuilder:
    
    def __init__(self, initial_ast: AST) -> None:
        self.ast =initial_ast
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

    def apply_for_to_comprehension(self):
        (
            TransformationBuilder(self.ast)
            .add(ForTransformer(ForToListComprehension()))
            .add(ForTransformer(ForToDictComprehension()))
            .add(ForTransformer(ForToSum()))
            .run()
        )
        return self

    def apply_invert_if(self):
        (
            TransformationBuilder(self.ast)
            .add(IfTransformer(InvertIf()))
            .run()
        )
        return self
    
    def apply_invert_def(self):
        (
            TransformationBuilder(self.ast)
            .add(FunctionDefTransformer(ExtractFunctionDefGuard()))
            .run()
        )
        return self
    
    def apply_logic_rules(self):
        (
            TransformationBuilder(self.ast)
            .add(LogicTransformer(DoubleNegation()))
            .add(LogicTransformer(DeMorgan()))
            .run()
        )
        return self
