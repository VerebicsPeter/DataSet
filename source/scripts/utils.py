import os

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