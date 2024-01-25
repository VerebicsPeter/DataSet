#----------------
import os
import sys
import hashlib
#----------------
import utils
#----------------

if __name__ == "__main__":
    
    # path to this script
    FILE = __file__
    print("FILE:", FILE)
    DATA = os.path.abspath(os.path.join(FILE, "..", "..", "data")
    )
    print("DATA:", DATA)
    DEST = os.path.abspath(os.path.join(DATA, "scripts")
    )
    print("DEST:", DEST)

    if not os.path.isdir(DATA):
        os.mkdir(DATA); print("created directory: 'data'")
    if not os.path.isdir(DEST):
        os.mkdir(DEST); print("created directory: 'scripts'")

    if len(sys.argv) == 2:
        # path provided as argument
        path = sys.argv[1]

        if os.path.isdir(path):
            SRCS = path
        else:
            print("The specified path is not a directory.")
            sys.exit(1)
    else:
        SRCS = os.path.abspath(os.path.join(DATA, "repos"))
        if not os.path.isdir(SRCS):
            os.mkdir(SRCS)
            print("Default 'repos' directory created at 'data/repos'. Please provide files.")
            sys.exit(1)

    scripts = utils.get_python_scripts_at(SRCS)

    for script in scripts:
        hash = hashlib.sha256()
        path = script['path']
        utils.get_hash(path, hash)
        os.popen(f"cp {path} {DEST}/{hash.hexdigest()}.py"); print(f"copying {path} to destination")
