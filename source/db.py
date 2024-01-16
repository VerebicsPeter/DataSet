import os

from pymongo import MongoClient

import persistance.utils as utils

from persistance.persistor import RefactoringStore

from transformations import transformation_api as api

if __name__ == "__main__":
    # create client
    client = MongoClient()
    # select database
    db = client['refactoring']
    # collection from database
    scripts_collection = db.scripts

    # path to this script
    FILE = __file__
    DATA = os.path.abspath(os.path.join(FILE, "..", "..", "data")
    )
    PATH = os.path.abspath(os.path.join(DATA, "scripts")
    )
    print(DATA)
    print(PATH)

    scripts = utils.get_python_scripts_at(PATH)

    for script in scripts:
        root = script['root']
        path = script['path']
        file = script['file']

        # original script's name (hash)
        script_hash = file.split('.')[0]

        with open(path) as f: script_source = f.read()
        # continue if reading failed or file is empty
        if not len(script_source): continue

        store = RefactoringStore(script_hash, script_source)

        # TODO: add refactorings here

        api.greet()

        print(' --- storeID:', store.id)
        print(' --- methods:', len(store.refactorings))

        #store.save(scripts_collection)
