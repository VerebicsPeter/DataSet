#----------------
from pymongo import MongoClient
#----------------
from .bases import *
#----------------


def catch_all(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            print("catch all caught:", error)
    return wrapper


def row_data(doc, keys):
    return { key: doc[key] if key in doc else None 
         for key in keys }


class Client(MonoState, Observable):

    def __init__(self):
        super().__init__()
        # initialize the state of each attribute if not present
        self.__init_state()


    def __init_state(self):
        # NOTE: Beware of name mangling when using brog attributes like this (__ mangles the name)
        if not hasattr(self, "client"    ): self.client     = None
        if not hasattr(self, "equivalent"): self.equivalent = None
        if not hasattr(self, "observers" ): self.observers : list[Observer] = []


    def attach(self, observer):
        self.observers.append(observer)


    def notify(self, event_type: str):
        for observer in self.observers:
            observer.on_update(event_type)


    @catch_all
    def set_client(self, client: MongoClient):
        self.client = client
        self.equivalent = client.refactoring.equivalent
        self.notify("client_change")

    @catch_all
    def get_client_info(self) -> str | None:
        if self.client is None: return
        return f"{self.client.HOST}:{self.client.PORT}"
    
    @catch_all
    def get_document_count(self) -> int | None:
        if self.client is None: return
        return self.equivalent.count_documents({})
    
    @catch_all
    def find_one(self, id: str):
        if self.client is None: return
        return self.equivalent.find_one({"_id": id})
    
    @catch_all    
    def find_all(self, skip: int, limit: int):
        if self.client is None: return
        return self.equivalent.find({}).skip(skip).limit(limit)
    
    @catch_all
    def table_data(self, skip = 0, limit = 0):
        if self.client is None: return
        
        docs = list(self.find_all(skip, limit))
        
        key_set = set()
        for keys in [doc.keys() for doc in docs]: key_set.update(keys)
        keys = list(key_set)
        keys.sort()
        
        return keys, [ row_data(doc, keys) for doc in docs ]
