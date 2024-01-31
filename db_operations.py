import bpy
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient

def connect_to_db():
    
    uri = "mongodb+srv://devdb:dev123@cluster0.aukmt1u.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri) # creates client from dev db account
    return client

def test_connection():
    
    db_name = 'StM-dev' # db name we are currently working with

    client = connect_to_db()
    db = client[db_name]

    try:
        
        # its just going to try to connect and list db collection names
        collection_names = db.list_collection_names()
        print(f"Connected to MongoDB. Collections: {collection_names}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        
        client.close()

# run the test when this module is executed
if __name__ == "__main__":
    test_connection()
