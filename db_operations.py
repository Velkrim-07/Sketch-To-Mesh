import bpy
import io
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from .file_conversion import encode_file, decode_file

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

# db, collection and file path temporarily hardcoded
def save_file_to_db(file_path_db):

    mClient = connect_to_db()
    db = mClient['StM-dev']
    collection = db['Test']

    # ideally this is going to be file_path_db; the file we want to convert to binary and save in the database. since this is not currently connected to the workflow of the
    # plugin, we left hardcoded to be able to perform a demonstration.
    blend_file_path = r"C:\Users\Rafael\Desktop\Exampel\IMG_1363.jpg" 
    blend_file_name = blend_file_path.split("\\")[-1] # just grabs the end of the file path so we can properly describe it in the DB

    file_encoded = encode_file(blend_file_path)

    data = {"filename": blend_file_name, "data": file_encoded.getvalue()}

    collection.insert_one(data)

    mClient.close()

# run the test when this module is executed
if __name__ == "__main__":
    test_connection()