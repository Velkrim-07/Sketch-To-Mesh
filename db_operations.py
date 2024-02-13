import bpy
import io
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient

def connect_to_db():
    
    # username: dev | password: dev123
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
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        
        client.close()

def save_file_to_db():
    mClient = MongoClient('mongodb+srv://devdb:dev123@cluster0.aukmt1u.mongodb.net/?retryWrites=true&w=majority')
    db = mClient['StM-dev']
    collection = db['Test']

    blend_file_path = r"C:\Users\James Burns\Documents\untitled.blend"

    with open(blend_file_path, "rb") as file:
        blend_file_contents = io.BytesIO(file.read())

    data = {"filename": "untitled.blend", "data": blend_file_contents.getvalue()}

    collection.insert_one(data)

    mClient.close()

# run the test when this module is executed
if __name__ == "__main__":
    test_connection()