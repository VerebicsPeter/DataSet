from pymongo.collection import Collection
from pymongo import MongoClient


def catch_all(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            print("catch all caught:", error)
    return wrapper


def parsed_data(doc, keys): return { key: doc[key] if key in doc else None for key in keys }


class Client:
    __shared = {}

    def __init__(self):
        self.__dict__ = self.__shared  # instance attributes set to shared state
        self.__init_state()


    def __init_state(self):
        # NOTE: Beware of name mangling when using brog attributes like this (__ mangles the name)
        if not hasattr(self, "client"    ): self.client     = None
        if not hasattr(self, "equivalent"): self.equivalent = None

    @catch_all
    def set_client(self, client: MongoClient):
        self.client     = client
        self.equivalent = client.refactoring.equivalent

    @catch_all
    def get_client_info(self) -> str | None:
        if self.client is None: return
        return f"{self.client.HOST}:{self.client.PORT}"
    
    @catch_all
    def get_document_count(self) -> int | None:
        if self.client is None: return
        return self.equivalent.count_documents({})
    
    @catch_all    
    def find_all(self, skip: int, limit: int):
        if self.client is None: return
        return self.equivalent.find({}).skip(skip).limit(limit)
    
    @catch_all
    def parsed_data(self, skip = 0, limit = 30):
        if self.client is None: return
        
        docs = list(self.find_all(skip, limit))
        
        key_set = set()
        for keys in [doc.keys() for doc in docs]: key_set.update(keys)
        keys = list(key_set)
        keys.sort()
        
        return keys, [ parsed_data(doc, keys) for doc in docs ]


class RefactoringStore:
    
    def __init__(self, id: str, source: str):
        self.id      = id
        self.source  = source
        self.results = []


    def add_result(self, result: dict[str, str], strict = False) -> None:
        if ("method" not in result or
            "result" not in result or
            result.get("method") in ["_id", "_source"]):
            return
        if (strict and self.source == result['result']):
            return
        if not result['result']:  # return if the result is empty
            return
        self.results.append(result)


    def save(self, collection: Collection) -> None:
        # return if there is nothing to save
        if not self.results:
            return
        
        # insert
        if not collection.find_one({"_id": self.id}):
            # try to save the script results
            try:
                refactoring = { r['method']:r['result'] for r in self.results }
                refactoring['_id']     = self.id
                refactoring['_source'] = self.source

                collection.insert_one(refactoring)
                
                print('Inserted refactoring.')
            except Exception as err:
                print("Something went wrong while saving the refactoring!\n", err)
        # update
        else:
            # try to update the results
            try:
                results = { r['method']:r['result'] for r in self.results }
                # TODO: check for hash collisions
                collection.update_one({"_id": self.id}, {"$set": results})
                
                print('Updated refactoring.')
            except Exception as err:
                print("Something went wrong while updating the refactoring!\n", err)
