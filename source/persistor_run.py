import os

import autopep8

from pymongo import MongoClient

from persistance.persistor import RefactoringStore

from transformations import transformation_api as api

import utils

if __name__ == "__main__":
    # create client
    client = MongoClient()
    # select database
    db = client['refactoring']
    # select collection from database
    scripts_collection = db['equi_tuples']
    
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
        root : str = script['root']
        path : str = script['path']
        file : str = script['file']

        # file name (hash calculeted when the file was copied)
        script['hash'] = file.split('.')[0]
        if not script['hash']:
            continue

        # file contents 
        with open(path) as f: script['source'] = f.read()
        if not script['source']:
            continue

        store = RefactoringStore(script['hash'], script['source'])
        
        # No AST transformations

        store.add_result(
            {
                "method": "autopep",
                "result": autopep8.fix_code(script['source'])
            }
        )
        
        # AST transformations
        
        parsed = api.safe_parse(script['source'])
        if not parsed:
            continue
        
        store.add_result(
            {
                "method": "autopep+for_to_comp",
                "result": autopep8.fix_code(
                    api.CopyTransformer(parsed)
                    .apply_for_to_comprehension()
                    .change()
                )
            }, strict=True
        )
        
        store.add_result(
            {
                "method": "autopep+ast_all",
                "result": autopep8.fix_code(
                    api.CopyTransformer(parsed)
                    .apply_all()
                    .change()
                )
            }, strict=False
        )
        
        # TODO: add more refactorings here
        
        print(' --- store ID:', store.id)
        print(' --- number of results:', len(store.results))

        store.save(scripts_collection)
