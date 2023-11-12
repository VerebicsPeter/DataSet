# Implementations of rules

from abc import ABC, abstractmethod

from redbaron import RedBaron, Node, ForNode

from patterns import (
    for_to_list_comprehension,
    for_to_list_comprehension_if,
    for_to_dict_comprehension,
    for_to_dict_comprehension_if,
    for_to_numpy_sum
)

from changes import (
    ForToListComprehensionChange,
    ForToDictComprehensionChange,
    ForToNumpySumChange
)

from utils import *


class Rule(ABC):
    """ Abstract base class for transformation rules, such as `ForToListComprehension`, `ForToDictComprehension`
    """
    
    @abstractmethod
    def match(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def change(self, *args, **kwargs) -> tuple | None:
        pass


class ForToListComprehension(Rule):
    
    def match(self, node: ForNode) -> bool:
        return (
            match_node(node, for_to_list_comprehension)
            or
            match_node(node, for_to_list_comprehension_if)
        )
    
    def change(self, node: ForNode) -> tuple | None:
        change = ForToListComprehensionChange(node)
        return change.get_change()


class ForToDictComprehension(Rule):
    
    def match(self, node: ForNode) -> bool:
        return (
            match_node(node, for_to_dict_comprehension)
            or
            match_node(node, for_to_dict_comprehension_if)
        )
    
    def change(self, node: ForNode) -> tuple | None:
        change = ForToDictComprehensionChange(node)
        return change.get_change()


class ForToNumpySum(Rule):
    
    def __init__(self, ast: RedBaron) -> None:
        self.ast   = ast
        self.numpy = get_module_name(ast, 'numpy')

    def match(self, node: ForNode) -> bool:
        return (
            self.numpy is not None and
            match_node(node, for_to_numpy_sum)
        )

    def change(self, node: ForNode) -> tuple | None:
        change = ForToNumpySumChange(node, self.numpy)
        return change.get_change()
