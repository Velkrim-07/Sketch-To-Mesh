import io
import os
import base64
import tempfile

def encode_file(file_path):
    
   with open(file_path, "rb") as file:
        blend_file_contents = io.BytesIO(file.read())
        return blend_file_contents
   
def decode_file(file_path, file_extension):
    #decode the data from base64
    binary_data = base64.b64decode(file_path)

    #write the data into a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) #we'll probably have to add another parameter here for the file extension or soemthing else)
    temp_file.write(binary_data)
    temp_file.close()

    if file_extension == ".blend":
        blend_opener(temp_file)
    else:
        fbx_opener(temp_file)

    #remove the temp file
    os.unlink(temp_file.name)

    #if we are returning just the file back then cases checking will have to happen outside of this method
    return 0

def blend_opener(file):
    # open up the blend file here
    return 0

def fbx_opener(file):
    # open up the .fbx file here
    return 0