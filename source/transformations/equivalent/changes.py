# Implementations of changes

# TODO: define function to decide if a node is before another

from abc import ABC, abstractmethod

from redbaron import (Node, IntNode, FloatNode, ForNode, ListNode, DictNode, NameNode)

from transformations.utils.node import *


class ForChange(ABC):
    """ Abstract base class for change implementation
    """

    def __init__(self, node: ForNode) -> None:
        self.for_node = node
        self.iterator = node.iterator
        self.target   = node.target
        self.if_node  = node.value.find('if')
        self.test     = self.if_node.test if self.if_node else None
    
    @abstractmethod
    def get_change(self) -> tuple | None:
        pass

    def _get_main_operation(self, child_type: str) -> Node | None:
        operation_node = None
        match self.test:
            case None:
                operation_node = self.for_node.value.find(child_type)
            case Node() as _node:
                if not node_mentions(_node, self.iterator.value):
                    return None
                operation_node = self.if_node.value.find(child_type)
        return  operation_node
    
    def _get_init_assignment(self, name: str) -> Node | None:
        last_mention = get_last_node_before(self.for_node, name, node_mentions)
        last_assign  = get_last_node_before(self.for_node, name, node_assigns)
        
        match last_assign:
            case None:
                return None
            case Node() as _node:
                if _node is not last_mention:
                    return None
                if not ForChange._has_valid_init_value(_node):
                    return None
        
        if isinstance(self.target, NameNode):
            # this checks if the initializied node is
            # before the for target's last mention
            last_mention_between = get_last_node_between(
                last_mention, self.for_node, self.target.value, node_mentions
            )
            if  last_mention_between: return None
        
        return last_assign

    @staticmethod
    def _has_valid_init_value(node) -> bool:
        match node.value:
            case ListNode() as _node:
                return node_is_empty_collection(_node)
            case DictNode() as _node:
                return node_is_empty_collection(_node)
            case IntNode()  as _node:
                return node_is_zero_numeric(_node)
            case FloatNode() as _node:
                return node_is_zero_numeric(_node)
            case _: return False


class ForToListComprehensionChange(ForChange):
    
    def __init__(self, node: ForNode) -> None:
        super().__init__(node)
    
    def get_change(self) -> tuple | None:
        atomtrailers = self._get_main_operation('atomtrailers')
        if not atomtrailers: return None
        
        arg = atomtrailers.value.find('call').find('call_argument')
        match arg:
            case Node() as _node:
                if not node_mentions(_node, self.iterator.value):
                    return None
        
        list_name = atomtrailers.value.find('name').value
        init_node = self._get_init_assignment(list_name)
        if init_node is None: return None
        
        result  = f'{arg} for {self.iterator} in {self.target}'
        
        result += f' if {self.test}' if self.test is not None else ''
        
        return (init_node, '['+result+']')


class ForToDictComprehensionChange(ForChange):
    
    def __init__(self, node: ForNode) -> None:
        super().__init__(node)
    
    def get_change(self) -> tuple | None:
        assignment = self._get_main_operation('assignment')
        if not assignment: return None

        key = assignment.target.find('getitem').value
        match key:
            case Node() as _node:
                if not node_mentions(_node, self.iterator.value):
                    return None
        
        dict_name = assignment.target.find('name').value
        init_node = self._get_init_assignment(dict_name)
        if not init_node: return None
        
        result  = f'{key} : {assignment.value} for {self.iterator} in {self.target}'

        result += f' if {self.test}' if self.test is not None else ''
        
        return (init_node, '{'+result+'}')


class ForToNumpySumChange(ForChange):
    
    def __init__(self, node: ForNode, numpy: str) -> None:
        super().__init__(node)
        self.numpy = numpy
    
    def get_change(self) -> tuple | None:
        
        assignment = self._get_main_operation('assignment')
        
        inc_name = assignment.value.find('name')
        match inc_name:
            case Node() as _node:
                if _node.value != self.iterator.value: return None
        
        sum_name = assignment.target.value
        init_node = self._get_init_assignment(sum_name)
        if not init_node: return None
        
        result = f"{self.numpy}.sum({self.target})"
        return (init_node, result)
