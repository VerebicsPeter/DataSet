import os

from pymongo import MongoClient

import utils

# Refactorings implemented:
# - autopep (formatter), isort (import sorter), modernize (2to3 wrapper)

class ScriptRefactoringStore:


    def __init__(self, id, source: str):
        self.id = id
        self.source = source
        self.refactorings = []


    def add_refactoring(self, refactoring: dict[str, str]) -> None:
        if ("method" not in refactoring or 
            "result" not in refactoring): 
            return
        self.refactorings.append(refactoring)


    def save(self, collection) -> None:
        # return if there is nothing to save
        if len(self.refactorings) == 0: return
        
        # insert
        if collection.find_one({"_id":self.id}) is None:
            # try to save the script refactoring
            try:
                script_ref = {r['method']:r['result'] for r in self.refactorings}
                script_ref['_id']    = self.id
                script_ref['source'] = self.source
                                
                collection.insert_one(script_ref)
                
                print('Inserting record.')
            except Exception as err:
                print("Something went wrong while saving the refactoring!\n", err)
        # update
        else:
            # try to update the refactorings
            try:
                refactorings = {r['method']:r['result'] for r in self.refactorings}
                                
                collection.update_one({"_id":self.id}, {"$set": refactorings})
                
                print('Updating record.')
            except Exception as err:
                print("Something went wrong while updating the refactoring!\n", err)


    # adds a refactoring result to an instance:
    # script_id should be the hash of the file
    # scripts   should be the list of filepaths to the refactored files
    @staticmethod
    def add_refactoring_with_method(
        instance, method: str, script_hash: str, scripts: list[str]) -> None:
        
        script_name = f"{script_hash}.{method}.py"

        if any(method == m for m in ["_id", "source"]):
            print(f'"{method}" method is not allowed!')
            return
        
        if all(script_name != s['file'] for s in scripts):
            print(f'{script_name} not found!')
            return

        with open(f"{root}/{script_name}") as f:
            content = f.read()
            if len(content): instance.add_refactoring({
                "method": method, "result": content
            })

if __name__ == "__main__":
    # create client
    client = MongoClient()
    # select database
    db = client['refactoring']
    # collection from database
    scripts_collection = db.scripts

    HOME = os.path.expanduser('~')
    PATH = f"{HOME}/Documents/DataSet/resources/scripts"

    scripts = utils.get_python_scripts_at(PATH)

    for script in scripts:
        # skip the refactored scripts
        if len(script['file'].split('.')) != 2: continue

        root = script['root']
        path = script['path']
        file = script['file']

        # original script name (hash)
        script_hash = file.split('.')[0]
        # original script content
        script_source = ''

        with open(path) as f: script_source = f.read()
        # continue if reading failed or file is empty
        if not len(script_source): continue

        refactoring = ScriptRefactoringStore(script_hash, script_source)

        ScriptRefactoringStore.add_refactoring_with_method(
            refactoring, 'autopep',   script_hash, scripts)
        ScriptRefactoringStore.add_refactoring_with_method(
            refactoring, 'isort',     script_hash, scripts)
        ScriptRefactoringStore.add_refactoring_with_method(
            refactoring, 'modernize', script_hash, scripts)
        
        print('>>> refactoring ID:', refactoring.id)
        print('>>> refactorings *:', len(refactoring.refactorings))

        refactoring.save(scripts_collection)
