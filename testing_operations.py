import bpy
from .db_operations import test_connection, save_file_to_db, get_files_by_user_id, delete_files_by_object_id # the . is on purpose. do not remove
from .image_processing import prepare_image, test_feature_detection # the . is on purpose. do not remove

# Saving info 
# bpy.ops.wm.save_as_mainfile(filepath="c:\Users\James Burns\Documents\TestFile.blend")

class StMTestDeleteFileFromDbFromUserId(bpy.types.Operator):
    bl_idname = "wm.delete_file_from_db_operator"
    bl_label = "Test Deleting File"

    def execute(self, context):
        
        objectId = "65ccec75d26b1d7703fb3a0a"
        result = delete_files_by_object_id(objectId) # 123 since the only document in the db is 123
        
        if (result == 0):
            print("No files deleted. Check ObjectID")
        if (result == 1):
            print(f"objectId: {objectId} file successfully deleted.")
            self.report({'INFO'}, "File successfully deleted.")
        
        return {'FINISHED'}
    

class StMTestSaveFileToDb(bpy.types.Operator):
        bl_idname = "wm.save_file_to_db_operator"
        bl_label = "Test Saving File"

        def execute(self, context):
            
            # using hardcoded files to test saving it into db.
            blend_file_path = "C:/Users/RAFAEL MUITO ZIKA/Desktop/Test/prepared_image.png"
            blend_file_name = blend_file_path.split("\\")[-1] # just grabs the end of the file path so we can properly describe it in the DB
            blend_file_name = blend_file_path.split("/")[-1] # for mac?

            save_file_to_db("65d60f0e839540defc6a0327", blend_file_path, blend_file_name) # needs a file path but are not using

            return {'FINISHED'}
    

class StMTestGetFileFromDbFromUserId(bpy.types.Operator):
    bl_idname = "wm.get_file_from_db_operator"
    bl_label = "Test Getting File"

    def execute(self, context):
        
        result = get_files_by_user_id("123") # 123 since the only document in the db is 123
        
        for document in result:
            # removed the bin data because it was too annoying as the output. fileEncoded: {document['fileEncoded']}
            print(f"objectId: {document['_id']}, filename: {document['fileName']}, userId: {document['userId']}, insertedDate: {document['insertedDate']}")

        return {'FINISHED'}


class StMTestImagePrep(bpy.types.Operator):
    bl_idname = "wm.prepare_image_operator"
    bl_label = "Test Image Prep"

    def execute(self, context):
        test_feature_detection()
        
        #success = prepare_image(path)
        #if success:
        #    self.report({'INFO'}, "Image Prep Succesful!")
        #else:
        #    self.report({'ERROR'}, "Failed to Image Prep.")

# class that executes test_connection from db_operations
# will be deleted in beta versions
class StMTestConnectionOperator(bpy.types.Operator):
    bl_idname = "wm.test_connection_operator"
    bl_label = "Test Database Connection"

    def execute(self, context): 
        success = test_connection()
        if success:
            self.report({'INFO'}, "Connection to MongoDB successful!")
        else:
            self.report({'ERROR'}, "Failed to connect to MongoDB.")
        return {'FINISHED'}

# TODO: finish the testing button
# TODO: import class into __init__
# TODO: register and unregister and put it together to testing buttons already registered (see examples)
class StMTestDecodeAndImport(bpy.types.Operator):
    bl_idname = "wm.test_decode_import"
    bl_label = "Test Decode And Import"


    def execute(self, context): 

        # whatever james is doing here
        success = test_connection()
        if success:
            self.report({'INFO'}, "Connection to MongoDB successful!")
        else:
            self.report({'ERROR'}, "Failed to connect to MongoDB.")
        return {'FINISHED'}

class DoImg(bpy.types.Operator):
    bl_idname = "object.do_img"
    bl_label = "Place Image"
    #Property that holds the filepath that will be used to insert the image
    myFilePath = ""
    #bpy.props.StringProperty(subtype="FILE_PATH")

    #This is the function that inserts the image into blender
    def execute(self, context):
        bpy.ops.object.load_reference_image(filepath=self.myFilePath)
        return {'FINISHED'}
    #This is a function that opens a file explorer
    #THIS DOES NOT DO ANYTHING I just think its going to be useful to have later
    def invoke(self, context, event):
        # Open a file browser to select a file
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}  
