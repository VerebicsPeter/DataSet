import os
# pprint for logging
import pprint
# pymongo for persisting data
from pymongo import MongoClient

import utils

# Refactorings implemented:
# - isort (import sorter)
# - modernize (2to3 wrapper)

class Refactoring:

    def __init__(self, id, source: str):
        self.id = id
        self.source = source
        self.refactorings = []
    
    def add_refactoring(self, refactoring: dict[str, str]) -> None:
        if "method" not in refactoring or "result" not in refactoring: return
        self.refactorings.append(refactoring)

    def save(self, collection) -> None:
        # return if there's nothing to save
        if len(self.refactorings) == 0: return
        # else try to save the refactoring
        try:
            refactoring_dict = {"_id": self.id, "source": self.source}
            for r in self.refactorings:
                refactoring_dict[r['method']] = r['result']
            
            collection.insert_one(refactoring_dict)
        except Exception as err:
            print("Something went wrong while saving the refactoring!\n", err)
    
    @staticmethod
    def add_refactoring_with_method(
        instance, method: str, script_id: str, scripts: list[str]) -> None:
        
        script_fn = f"{script_id}.{method}.py"
    
        if all(s['file'] != script_fn for s in scripts):
            print(f'{script_fn} not found!')
            return

        with open(f"{root}/{script_fn}") as f:
            content = f.read()
            if len(content): instance.add_refactoring({
                "method": method, "result": content
            })

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

    # original script name (uuid)
    script_id = file.split('.')[0]
    # original script string
    script_source = ''

    with open(path) as f: script_source = f.read()
    # continue if reading failed or file is empty
    if not len(script_source): continue

    refactoring = Refactoring(script_id, script_source)

    Refactoring.add_refactoring_with_method(
        refactoring,'isort',     script_id, scripts)
    Refactoring.add_refactoring_with_method(
        refactoring,'autopep',   script_id, scripts)
    Refactoring.add_refactoring_with_method(
        refactoring,'modernize', script_id, scripts)
    
    print('>>> refactoring ID:'  , refactoring.id)
    print('>>> refactorings  :', len(refactoring.refactorings))

    refactoring.save(scripts_collection)