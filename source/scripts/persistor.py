import os
# pprint for logging
import pprint
# pymongo for persisting data
from pymongo import MongoClient

import utils

# Refactorings implemented:
# - autopep8 and isort (formatter and import sorter)
# - modernize (2to3 wrapper)

class Refactoring:

    def __init__(self, id, source: str, refactorings: list[dict[str,str]] = []):
        self.id = id
        self.source = source
        self.refactorings = refactorings
    
    def add_refactoring(self, refactoring: dict[str, str]):
        if "method" not in refactoring or "result" not in refactoring: return
        self.refactorings.append(refactoring)

    def save(self, collection):
        # return if there's nothing to save
        if len(self.refactorings) == 0: return

        try:
            refactoring = {"_id": self.id, "source": self.source}

            for r in self.refactorings:
                refactoring[r['method']] = r['result']
            
            collection.insert_one(refacoring)
        except:
            print("Something went wrong when saving the refactoring.")

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
    script_fn = file.split('.')[0]
    # original script string
    script_string = ''

    with open(path) as f: script_string = f.read()
    
    refacoring = Refactoring(script_fn, script_string)
    
    script_fn_a = f"{script_fn}.autopep_isort.py" # autopep and isort modified script name
    script_fn_m = f"{script_fn}.modernize.py"     # modernized script name

    if any(s['file'] == script_fn_m for s in scripts):
        with open(f"{root}/{script_fn_m}") as f: 
            content = f.read()
            if len(content): refacoring.add_refactoring({
                "method": "modernize", "result": content
            })

    if any(s['file'] == script_fn_a for s in scripts):
        with open(f"{root}/{script_fn_a}") as f: 
            content = f.read()
            if len(content): refacoring.add_refactoring({
                "method": "autopep_isort", "result": content
            })
                
    refacoring.save(scripts_collection)