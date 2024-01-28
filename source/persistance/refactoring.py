    # TODO use proper monostate pattern

from pymongo.collection import Collection
from pymongo import MongoClient


class Client:
    __client : MongoClient = None
    # collection
    equivalent : Collection = None
    
    @classmethod
    def set_client(cls, client):
        try:
            cls.__client   = client
            cls.equivalent = client.refactoring.equivalent
        except Exception as err:
            print(err)
    
    @classmethod
    def get_client(cls): return cls.__client
    
    @classmethod
    def get_client_info(cls):
        return f"{cls.__client.HOST}:{cls.__client.PORT}" if cls.__client else ""
    
    @classmethod
    def count_documents(cls):
        if     cls.equivalent is None: return
        return cls.equivalent.count_documents({})


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
