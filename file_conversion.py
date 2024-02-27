import bpy
import io
import os
import tempfile

def encode_file(file_path):
    
   with open(file_path, "rb") as file:
        blend_file_contents = io.BytesIO(file.read())
        return blend_file_contents

# TODO: return something that is not 0. case handling and error handling, as well as completed and noncompleted states.
def decode_file(file_path, file_extension):
    #Apparently the data doesn't need to be decoded so we will handle the different
    #file extensions handled here instead of outside the file_conversion.py file

    #write the data into a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) #we'll probably have to add another parameter here for the file extension or soemthing else)
    temp_file.write(file_path)
    temp_file.close()

    #Deal with the separate file extensions
    if file_extension == ".blend":
        blend_opener(temp_file.name)
    else:
        fbx_opener(temp_file.name)

    #remove the temp file
    os.unlink(temp_file.name)

    #if we are returning just the file back then cases checking will have to happen outside of this method
    return 0

# TODO: move to blend-operations
# TODO: return something that is not 0. case handling and error handling, as well as completed and noncompleted states.
def blend_opener(file_path):
    # open up the blend file here
    bpy.ops.wm.open_mainfile(filepath=file_path)
    return 0

# TODO: move to blend-operations
# TODO: return something that is not 0. case handling and error handling, as well as completed and noncompleted states.
def fbx_opener(file_path):
    # open up the .fbx file here
    bpy.ops.import_scene.fbx(filepath=file_path)
    return 0