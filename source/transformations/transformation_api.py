import copy

from transformations.transformation import (
    AST, NodeTransformation, NodeVisitor
)

from transformations.equivalent.visitors import (
    ForTransformer, IfTransformer, FunctionDefTransformer, LogicTransformer
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
    DoubleNegation,DeMorgan
)


class TransformationBuilder:
    
    def __init__(self, initial_ast: AST = None) -> None:
        self.queue = []
        self.__ast = initial_ast
    
    def set_ast(self, initial_ast: AST) -> None:
        self.__ast = initial_ast
    
    def get_ast(self) -> AST | None: return self.__ast
    
    def add(self, visitor: NodeVisitor):
        self.queue.append(visitor)
        return self
    
    def run(self):
        if not self.__ast:
            print("AST needed for running the transformation!")
            return
        
        transformation = NodeTransformation(self.__ast)
        
        while self.queue:
            visitor = self.queue.pop(0)
            transformation.transform_nodes(visitor)


class CopyTransformer():

    def __init__(self, ast: AST):
        self.ast = copy.deepcopy(ast)

    def apply_for_to_comprehension(self):
        (
            TransformationBuilder(self.ast)
            .add(ForTransformer(ForToListComprehension()))
            .add(ForTransformer(ForToDictComprehension()))
            .add(ForTransformer(ForToSetComprehension()))
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
