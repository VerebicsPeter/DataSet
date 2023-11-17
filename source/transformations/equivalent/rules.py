# Implementations of rules

# TODO: maybe move rules from here to their own transformation file

from abc import ABC, abstractmethod

from redbaron import RedBaron #, ForNode

from redbaron.nodes import *

from .patterns import (
    for_to_list_comprehension,
    for_to_list_comprehension_if,
    for_to_dict_comprehension,
    for_to_dict_comprehension_if,
    for_to_numpy_sum
)

from .changes import (
    ForToListComprehensionChange,
    ForToDictComprehensionChange,
    ForToNumpySumChange
)

from ..utils.node import *


class Rule(ABC):
    """ Abstract base class for transformation rules, such as `ForToListComprehension`, `ForToDictComprehension`
    """
    
    @abstractmethod
    def match(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def change(self, *args, **kwargs) -> object | None:
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


class ElevateAssignment(Rule):
    
    def match(self, node: AssignmentNode):
        return (
            node.parent is not None
            and 
            len(node.parent)
            and
            node.index_on_parent != 0
        )
    
    # TODO: FORD. PROG. algoritmus maybe
    def change(self, node: AssignmentNode):
        parent = node.parent
        
        names = [x.value for x in node.value.find_all('name')]

        first, last = parent.filtered()[0], None

        i = node.index_on_parent
        
        if i is not None:
            for x in node.parent[0: i]:
                if any(node_mentions(x, name) for name in names):
                    last = x
        
        p = node.dumps()
        
        if last is None:
            first.insert_before(p)
        else:
            last.insert_after(p)
            
        parent.remove(node)
