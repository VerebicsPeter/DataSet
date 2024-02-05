#----------------
import os
import autopep8
#----------------
import utils
#----------------
import db
from persistance.refactoring import RefactoringStore
#----------------
from transformations import transformation_api as api
#----------------

if __name__ == "__main__":
    client = db.connect("localhost", 27017)
    
    if not client: exit(1)
    
    # select database
    database = client['refactoring']
    # select collection from database
    collection = database['equivalent']
    
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
        if not parsed: continue
        
        store.add_result(
            {
                "method": "autopep+for_to_comp",
                "result": autopep8.fix_code(
                    api.CopyTransformer(parsed)
                    .apply_preset(api.for_to_comprehension)
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
        
        rules = api.all_visitor_names()
        rules.remove("Invert if")
        store.add_result(
            {
                "method": "autopep+ast_all_but_invert_if",
                "result": autopep8.fix_code(
                    api.CopyTransformer(parsed)
                    .apply_visitors([api.create_visitor(name) for name in rules])
                    .change()
                )
            }, strict=False
        )
        
        # TODO: add more refactorings here
        
        print(' --- store ID:', store.id)
        print(' --- number of results:', len(store.results))

        store.save(collection)
