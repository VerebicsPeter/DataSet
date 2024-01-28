#---------------
import logging
import uuid  # for generating generating treeview ids
from typing import Protocol
#---------------
from transformations import transformation_api as api
#----------------


def logger(func):
    def wrapper(*args, **kwargs):
        logging.debug('-'*100)
        if log := func(*args, **kwargs): logging.debug(log)
        logging.debug('-'*100)
    return wrapper


class MonoState:
    # shared state of all objects
    __shared = {}
    
    def __init__(self) -> None:
        self.__dict__ = self.__shared


class Observable(Protocol):
    def attach(observer):
        ...
    def notify():
        ...


class Observer(Protocol):
    def on_update(self):
        ...


class AppState(MonoState, Observable):
    
    def __init__(self):
        super().__init__()
        # initialize the state of each attribute if not present
        self.__init_state()
    
    
    def __init_state(self):
        if not hasattr(self, "visitors"): self.visitors : list[api.NodeVisitor] = []
        if not hasattr(self, "ast_source"): self.ast_source : api.AST = None
        if not hasattr(self, "ast_result"): self.ast_result : api.AST = None
        if not hasattr(self, "observers"): self.observers : list[Observer] = []


    @logger
    def ast_parse(self, source: str, target: str) -> api.AST:
        if target not in {'source', 'result'}: return
        
        try: parsed = api.parse(source)
        except Exception as exception:
            print('Error while parsing:')
            print(exception)
            raise exception
        
        if target=='source': self.ast_source = parsed
        if target=='result': self.ast_result = parsed
            
        return parsed
    

    def ast_transform(self) -> str:
        if visitors:= self.visitors:
            self.ast_result = api.CopyTransformer(self.ast_source)\
                .apply_visitors(visitors)\
                .ast
        else:
            self.ast_result = api.CopyTransformer(self.ast_source)\
                .apply_all()\
                .ast
        # NOTE: maybe put this in a try block
        return api.unparse(self.ast_result)


    def attach(self, observer):
        self.observers.append(observer)


    def notify(self):
        for observer in self.observers:
            observer.on_update()
    
    
    def add_visitor(self, name: str) -> None:
        visitor = api.create_visitor(name)
        # TODO: error handling
        self.visitors.append(visitor)
        self.notify()
    

    def pop_visitor(self) -> object:
        # TODO
        pass
    
    
    def clear_visitors(self):
        self.visitors.clear()
        self.notify()


    def settings_info(self) -> str:
        return "custom" if len(self.visitors) else "default (all)"
    

    def treeview_data(self, target: str) -> list:
        data = []
        root = None
        if target not in {'source', 'result'}: return data
        if target == 'source': root = self.ast_source
        if target == 'result': root = self.ast_result
        
        if not root: print("No AST provided."); return data
        
        def node_text(node):
            unparsed = api.unparse(node)
            if 30 >len(unparsed):
                return unparsed.split('\n', 1)[0]
            else:
                return unparsed[:30].split('\n', 1)[0]+'...'

        def add_node(node, parent=None):
            node_name = str(node.__class__.__name__)
            node.uuid = uuid.uuid4()
            if parent:
                data.append((parent.uuid,
                    node.uuid, node_name, (node_text(node),))
                )
            else:
                data.append(("",
                    node.uuid, node_name, (node_text(node),))
                )
            for child in api.iter_child_nodes(node):
                add_node(child, node)
        
        add_node(root)
        return data
