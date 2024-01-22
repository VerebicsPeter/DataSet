from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def connect(host: str, port: int):
    # create client
    client = MongoClient(host, port)
    
    try:
        client.admin.command('ping')
    except ConnectionFailure:
        print("\nConnection to database failed.")
        return None
    
    print("\nConnected to database.")
    return client
