# Usage

## App Usage

1) Make sure that all requirements in `requirements.txt` have been installed.
2) [Optional] Connect to a `mongodb` server with refactorings.
3) Launch the app by running the `main.py` script.

Use the app to try refactorings and browse the database.

## Script Usage

Refactorings can be added inside the  `persistor_run.py` script using `store`.

### Initialize

- `persistor_init.py` - **copy** all **.py** scripts from `data/repos` to `data/scripts`.

### Persistence

- `persistor_run.py` - **save** all **.py** scripts to mongodb database.
