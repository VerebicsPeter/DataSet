import os
import pprint
# pymongo for persisting data
from pymongo import MongoClient

# create client
client = MongoClient()
# select database
db = client['refactoring']
# collection from database
collection = db.scripts

print(f"Collections: {db.list_collection_names()}")

PATH = "/home/peter/Documents/DataSet/resources/scripts"

def get_python_scripts_at(path: str) -> list[dict]:
    result = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.split('.')[-1] != "py": continue
            result.append({
                "root": root,
                "file": file,
                "path": f"{root}/{file}"
            })
    return result

scripts = get_python_scripts_at(PATH)

for script in scripts: print(script['path'])

for script in scripts:
    # skip the refactored scripts
    if len(script['file'].split('.')) != 2: continue

    root = script['root']
    path = script['path']
    file = script['file']

    script_o = '' # original script string
    script_m = '' # modernized script string

    with open(path) as f: script_o = f.read()
        
    fn_o = file.split('.')[0] # original script name
    fn_m = f"{fn_o}.modernize.py" # modernized script name

    if any(s['file'] == fn_m for s in scripts):
        with open(f"{root}/{fn_m}") as f: script_m = f.read()
    
    if len(script_m):
        refacoring = {
            "_id": fn_o,
            "source": script_o,
            "modernize": script_m,
        }
        collection.insert_one(refacoring)