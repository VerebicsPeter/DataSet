# Node specific class transformations

from abc import ABC, abstractmethod

from redbaron import RedBaron

from redbaron.nodes import *

from .rules import Rule


class NodeTransformation(ABC):

    def __init__(self, ast: RedBaron, rule: Rule) -> None:
        self.ast = ast
        self.rule = rule


    def transform_nodes(self) -> None:
        # match
        nodes = self.ast.find_all(self.node_type())
        # transform matched query results
        for node in nodes:
            if self.rule.match(node): self.transform_node(node)

    @abstractmethod
    def node_type(self) -> str:
        pass

    @abstractmethod
    def transform_node(self) -> None:
        pass


class AssignmentNodeTransformation(NodeTransformation):

    def node_type(self) -> str: return 'assignment'


    def __init__(self, ast: RedBaron, rule: Rule):
        super().__init__(ast, rule)


    def transform_node(self, node: AssignmentNode) -> None:
        # change the node in place
        self.rule.change(node)


class ForNodeTransformation(NodeTransformation):

    def node_type(self) -> str: return 'for'


    def __init__(self, ast: RedBaron, rule: Rule) -> None:
        super().__init__(ast, rule)


    def transform_node(self, node: ForNode) -> None:
        result = self.rule.change(node)
        
        if not result: return None
        # apply change
        result[0].value = result[1]
        parent = node.parent
        parent.remove(node)
