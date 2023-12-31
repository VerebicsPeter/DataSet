# TODO: this should handle parsing the ast not the application


import copy

from transformations.transformation import (
    AST, NodeVisitor,
    NodeTransformation
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


class TransformationBuilder:
    
    def __init__(self, initial_ast: AST = None) -> None:
        self.queue = []
        self.__ast = initial_ast
    
    def set_ast(self, initial_ast: AST) -> None:
        self.__ast = initial_ast
    
    def get_ast(self) -> AST | None: return self.__ast
    
    def add_one(self, visitor: NodeVisitor):
        self.queue.append(visitor)
        return self
    
    def add(self, *visitors: NodeVisitor):
        self.queue.extend(visitors)
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
            .add(TFor(ForToListComprehension()))
            .add(TFor(ForToDictComprehension()))
            .add(TFor(ForToSetComprehension()))
            .add(TFor(ForToSum()))
            .run()
        )
        return self

    def apply_invert_if(self):
        (
            TransformationBuilder(self.ast)
            .add(TIf(InvertIf()))
            .run()
        )
        return self
    
    def apply_invert_def(self):
        (
            TransformationBuilder(self.ast)
            .add(TFunctionDef(ExtractFunctionDefGuard()))
            .run()
        )
        return self
    
    def apply_logic_rules(self):
        (
            TransformationBuilder(self.ast)
            .add(TLogic(DoubleNegation()))
            .add(TLogic(DeMorgan()))
            .run()
        )
        return self
