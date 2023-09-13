import os
import uuid

# path to destination folder containing python scripts
DEST = "/home/peter/Documents/DataSet/resources/scripts"
# path to source folder containing repositories
SOURCE = "/home/peter/Documents/DataSet/resources/repos"

def get_python_scripts(path: str) -> list[dict]:
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

scripts = get_python_scripts(SOURCE)

for script in scripts:
    os.popen(f"cp {script['path']} {DEST}/{uuid.uuid4()}.py")