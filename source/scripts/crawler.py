import os
import uuid

import utils

# path to home directory
HOME = os.path.expanduser('~')
# path to source folder containing repositories
SOURCE = f"{HOME}/Documents/DataSet/resources/repos"
# path to destination folder containing python scripts
DEST = f"{HOME}/Documents/DataSet/resources/scripts"

scripts = utils.get_python_scripts_at(SOURCE)

for script in scripts:
    os.popen(f"cp {script['path']} {DEST}/{uuid.uuid4()}.py")