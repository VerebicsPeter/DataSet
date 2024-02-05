import os

BUFFER = 65536  # 64kb chunks

def get_hash(path: str, hash) -> None:
    with open(path, 'rb') as f:
        while data := f.read(BUFFER):
            # update the hash with the chunk read
            hash.update(data)


# TODO: change this to a generator
def get_python_scripts_at(path: str) -> list[dict]:
    results = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.split('.')[-1] != "py": continue
            results.append({
                "root": root,
                "file": file,
                "path": f"{root}/{file}"
            })
    return results
