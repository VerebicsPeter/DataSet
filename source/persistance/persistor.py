    # TODO: having the refactoring scripts in shell scripts is dumb, do everything in a module

from pymongo.collection import Collection 

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
        if not result['result']:  # return if the result is an empty string
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
