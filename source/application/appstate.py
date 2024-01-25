#---------------
import logging
import uuid  # for generating generating treeview ids
from typing import Protocol
#---------------
from transformations import transformation_api as api
#----------------

class Observable(Protocol):
    @classmethod
    def attach(observer):
        ...
    @classmethod
    def notify():
        ...


class Observer(Protocol):
    def on_update(self):
        ...


class AppState(Observable):
    ast_source = None
    ast_result = None
    observers: list[Observer] = []
    visitors: list[api.NodeVisitor] = []
    
    @classmethod
    def get_settings(cls) -> str:
        return "custom" if len(cls.visitors) else "default (all)"
    
    @classmethod
    def parse_ast(cls, source: str, target: str) -> None:
        if target not in {'source', 'result'}: return
        
        try:
            parsed = api.parse(source)
        except Exception as exception:
            print('Error while parsing:')
            print(exception)
            raise exception
        
        if target=='source':
            cls.ast_source = parsed
        if target=='result':
            cls.ast_result = parsed
        
        logging.debug('-'*100)
        logging.debug(parsed)
        logging.debug('-'*100)
        logging.debug(f"\n{api.dump(parsed, indent=2)}")
        logging.debug('-'*100)
    
    @classmethod
    def transform_ast(cls) -> str:
        if visitors:= cls.visitors:
            AppState.ast_result = api.CopyTransformer(AppState.ast_source)\
                .apply_visitors(visitors)\
                .ast
        else:
            AppState.ast_result = api.CopyTransformer(AppState.ast_source)\
                .apply_all()\
                .ast
        # maybe use a try block
        return api.unparse(AppState.ast_result)
    
    @classmethod
    def attach(cls, observer):
        cls.observers.append(observer)

    @classmethod
    def notify(cls):
        for observer in cls.observers:
            observer.on_update()
    
    @classmethod
    def add_visitor(cls, name: str) -> None:
        visitor =api.create_visitor(name)
        # TODO: error handling
        cls.visitors.append(visitor)
        cls.notify()
    
    @classmethod
    def pop_visitor(cls) -> object:
        # TODO
        pass
    
    @classmethod
    def clear_visitors(cls):
        cls.visitors.clear()
        cls.notify()

    @classmethod
    def treeview_data(cls, target: str) -> list:
        data = []
        
        root = None
        if target not in {'source', 'result'}: return data
        if target == 'source': root = cls.ast_source
        if target == 'result': root = cls.ast_result
        
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
