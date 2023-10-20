import os

BUFFER_SIZE = 65536  # 64kb chunks

def get_hash(path: str, hash) -> None:
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data: break
            hash.update(data)

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