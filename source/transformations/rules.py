# Implementations of rules

from abc import ABC, abstractmethod

from redbaron import RedBaron, Node

from patterns import (
    for_to_list_comprehension,
    for_to_list_comprehension_if,
    for_to_dict_comprehension,
    for_to_dict_comprehension_if,
    for_to_numpy_sum
)

from utils import *


class Rule(ABC):
    """ Abstract base class for transformation rules, such as `ForToListComprehension`, `ForToListComprehensionIf`
    """
    @abstractmethod
    def match(self, *args, **kwargs) -> bool:
        pass
    @abstractmethod
    def change(self, *args, **kwargs) -> tuple | None:
        pass


class ForToListComprehension(Rule):
    
    def match(self, node: Node) -> bool:
        return match_node(node, for_to_list_comprehension)
    
    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target
        
        atomtrailers = node.value.find('atomtrailers')
        
        list_name = atomtrailers.value.find('name').value
        
        last_assign  = get_last_node_before(node, list_name, node_assigns)
        last_mention = get_last_node_before(node, list_name, node_mentions)

        match last_assign:
            case None:
                return None
            case Node() as _node:
                if last_mention is not _node:
                    return None
                if not node_is_empty_list(_node.value):
                    return None
        
        call = atomtrailers.value.find('call')
        
        match call:
            case Node() as _node:
                if not len(_node.value) == 1:
                    return None
                if not node_mentions(_node, iterator.value):
                    return None
        
        result = f'[{call.value[0]} for {iterator} in {target}]'
        return (last_assign, result)


class ForToListComprehensionIf(Rule):
    
    def match(self, node: Node) -> bool:
        return match_node(node, for_to_list_comprehension_if)
    
    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target
        
        if_node = node.value.find('ifelseblock').value.find('if')
        
        test = if_node.test
        
        match test:
            case Node() as _node:
                if not node_mentions(_node, iterator.value):
                    return None
        
        atomtrailers = if_node.value.find('atomtrailers')
        
        list_name = atomtrailers.value.find('name').value
        
        last_assign  = get_last_node_before(node, list_name, node_assigns)
        last_mention = get_last_node_before(node, list_name, node_mentions)
        
        match last_assign:
            case None:
                return None
            case Node() as _node:
                if last_mention is not _node:
                    return None
                if not node_is_empty_list(_node.value):
                    return None
        
        call = atomtrailers.value.find('call')
        
        match call:
            case Node() as _node:
                if not len(_node.value) == 1:
                    return None
                if not node_mentions(_node, iterator.value):
                    return None
        
        result = f'[{call.value[0]} for {iterator} in {target} if {test}]'
        return (last_assign, result)


class ForToDictComprehension(Rule):
    
    def match(self, node: Node) -> bool:
        return match_node(node, for_to_dict_comprehension)
    
    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target
        
        for_assignment = node.value.find('assignment')
        
        assignment_target = for_assignment.target
        assignment_value  = for_assignment.value
        
        get_item = assignment_target.find('getitem')
        
        match get_item:
            case Node() as _node:
                if not node_mentions(_node, iterator.value):
                    return False
        
        dict_name = assignment_target.find('name').value
        
        last_assign  = get_last_node_before(node, dict_name, node_assigns)
        last_mention = get_last_node_before(node, dict_name, node_mentions)
        
        match last_assign:
            case None:
                return None
            case Node() as _node:
                if last_mention is not _node:
                    return None
                if not node_is_empty_dict(_node.value):
                    return None
        
        result = '{'+f'{get_item.value} : {assignment_value} for {iterator} in {target}'+'}'
        return (last_assign, result)


class ForToDictComprehensionIf(Rule):
    
    def match(self, node: Node) -> bool:
        return match_node(node, for_to_dict_comprehension_if)
    
    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target
        
        if_node = node.value.find('ifelseblock').value.find('if')
        
        test = if_node.test
        
        match test:
            case Node() as _node:
                if not node_mentions(_node, iterator.value):
                    return None
        
        assignment = if_node.value.find('assignment')
        
        assignment_target = assignment.target
        assignment_value  = assignment.value
        
        get_item = assignment_target.find('getitem')
        
        match get_item:
            case Node() as _node:
                if not node_mentions(_node, iterator.value):
                    return False
        
        dict_name = assignment_target.find('name').value
        
        last_assign  = get_last_node_before(node, dict_name, node_assigns)
        last_mention = get_last_node_before(node, dict_name, node_mentions)
        
        match last_assign:
            case None:
                return None
            case Node() as _node:
                if last_mention is not _node:
                    return None
                if not node_is_empty_dict(_node.value):
                    return None
        
        result = '{'+f'{get_item.value} : {assignment_value} for {iterator} in {target} if {test}'+'}'
        return (last_assign, result)


class ForToNumpySum(Rule):
    
    def __init__(self, ast: RedBaron) -> None:
        self.ast = ast
        self.numpy = get_module_name(ast, 'numpy')

    def match(self, node: Node) -> bool:
        return self.numpy is not None and match_node(node, for_to_numpy_sum)

    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target

        assignment = node.value.find('assignment')

        inc_name = assignment.value.find('name')   
        sum_name = assignment.target.value
        
        match iterator:
            case Node() as _node:
                if inc_name.value != _node.value: return None
        
        last_assign  = get_last_node_before(node, sum_name, node_assigns)
        last_mention = get_last_node_before(node, sum_name, node_mentions)
        
        match last_assign:
            case None:
                return None
            case Node() as _node:
                if last_mention is not _node:
                    return None
                if node_is_zero_numeric(node):
                    return None
        
        target_last_mention = get_last_node_before(last_assign, target.value, node_mentions)
        # if target is not in scope return None
        if target_last_mention is None: return None
        
        result = f"{self.numpy}.sum({target})"
        return (last_assign, result)
