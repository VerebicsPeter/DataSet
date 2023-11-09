# Implementations of code transformations
# NOTE: Use 'match ... case' for readability
# TODO: typing and callable
# TODO: maybe define two methods (get_changes, apply_changes) in transformation classes
# Other
# TODO: Tamásnak írni a csoportban a githubos cuccal kapcsolatban

from abc import ABC, abstractmethod

import redbaron.nodes as rb

from redbaron import RedBaron, Node

from utils import (
    match_node,
    node_assigns,
    node_mentions,
    node_is_empty_list,
    get_last_node_before,
    get_module_name
)

from patterns import (
    for_to_list_comprehension,
    for_to_list_comprehension_if,
    for_to_numpy_sum
)


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
        name_nodes = atomtrailers.value.find_all('name')
        
        list_name = name_nodes[0].name.value
        
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
        name_nodes = atomtrailers.value.find_all('name')
        
        list_name = name_nodes[0].name.value
        
        # last node to assign to 'list_name'
        last_assign  = get_last_node_before(node, list_name, node_assigns)
        # last node to mention 'list_name'
        last_mention = get_last_node_before(node, list_name, node_mentions)
        # type and value checks for assignment node
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


class ForToNumpySum(Rule):
    
    def __init__(self, ast: RedBaron) -> None:
        self.ast = ast
        self.numpy = get_module_name(ast, 'numpy')

    def match(self, node: Node) -> bool:
        return self.numpy is not None and match_node(node, for_to_numpy_sum)

    def change(self, node: Node) -> tuple | None:
        iterator, target = node.iterator, node.target

        for_assignment = node.value.find('assignment')
        # inc variable's name
        inc_name = for_assignment.value.find('name')
        # sum variable's name
        sum_name = for_assignment.target.value
        
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
                if (_node.value.value != '0'
                    or 
                    not isinstance(_node.value, rb.IntNode)
                ):  return None
        
        target_last_mention = get_last_node_before(last_assign, target.value, node_mentions)
        # if target is not in scope return None
        if target_last_mention is None: return None
        
        result = f"{self.numpy}.sum({target})"
        return (last_assign, result)


class ForNodeTransformation():
    def __init__(self, ast: RedBaron, rule: Rule, params: dict | None = None) -> None:
        self.ast    = ast
        self.rule   = rule
        self.params = params
    
    def transform_nodes(self):
        # print source lines before
        print(self.ast)
        print('-'*150)
        
        for_nodes = self.ast.find_all('for')
        
        for for_node in for_nodes:
            # skip if node does not match
            if not self.rule.match(for_node): continue
            
            result = None
            # get change
            if self.params is None:
                result = self.rule.change(for_node)
            else:
                result = self.rule.change(for_node, self.params)
            
            # skip if there is no change to be applied
            if result is None: continue
            
            # apply the change
            result[0].value = result[1]
            # unlink the for node
            parent = for_node.parent
            parent.remove(for_node)
        
        # print source lines after
        print(self.ast)
        changed = self.ast.dumps()  # this is the dump of the changed source code
        print('-'*150)
        print(changed)
