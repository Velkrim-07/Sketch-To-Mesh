from datetime import datetime

# in MongoDb, if we don't specify objetId it is automatically created, so no need to touch it here.

# objectId (this will be the userId)
# username : string
# hashPassword : string (password is hashed) - thank you mr. obvious!
# insertedDate : datetime
# TODO: maybe in the future we will add editing user information, like changing passwords. for that, we will
# need to add a updatedDate field here.
def create_user_document(email, hash_password):
    user_document = {
    "username": email,
    "hashPassword": hash_password,
    "insertedDate": datetime.now() # current datetime in ISO format
}
    
    return user_document

# objectId is an unique identifier. it will be created by mongodb
# userId (objectId from user document in Users Collection)
# fileName
# fileBinaryData
# insertedDate
def create_file_document(userId, file_name, file_bin_data):
    file_document = {
    "userId": userId,
    "fileName": file_name,
    "fileEncoded": file_bin_data,
    "insertedDate": datetime.now() # current datetime in ISO format
}
    
    return file_document