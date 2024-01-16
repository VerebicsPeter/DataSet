    # TODO: having the refactoring scripts in shell scripts is dumb, do everything in a module

class RefactoringStore:

    def __init__(self, id: str, source: str):
        self.refactorings = []
        self.id     = id
        self.source = source


    def add_refactoring(self, refactoring: dict[str, str]) -> None:
        if ("method" not in refactoring or
            "result" not in refactoring):
            return
        self.refactorings.append(refactoring)
    

    def save(self, collection) -> None:
        # return if there is nothing to save
        if len(self.refactorings) == 0: return
        
        # insert
        if not collection.find_one({"_id": self.id}):
            # try to save the script refactoring
            try:
                script_ref = { r['method']:r['result'] for r in self.refactorings }
                script_ref['_id']    = self.id
                script_ref['source'] = self.source

                collection.insert_one(script_ref)
                
                print('Inserting refactoring.')
            except Exception as err:
                print("Something went wrong while saving the refactoring!\n", err)
        # update
        else:
            # try to update the refactorings
            try:
                refactorings = { r['method']:r['result'] for r in self.refactorings }
                # TODO: check for hash collisions
                collection.update_one({"_id": self.id}, {"$set": refactorings})
                
                print('Updating refactoring.')
            except Exception as err:
                print("Something went wrong while updating the refactoring!\n", err)
