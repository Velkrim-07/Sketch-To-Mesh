bl_info = {
    "name": "Sketch_To_Mesh",
    "author": "LuckyNinjas",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > My Custom Panel category",
    "description": "The Inital UI skeleton",
    "category": "Development",
}
    # 3D Viewport area (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items)
    # Sidebar region (find list of values here https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items)
    # bpy.ops.wm.save_as_mainfile(filepath="c:\Users\James Burns\Documents\TestFile.blend")
    
import bpy
import numpy

from .UI_Operation import OBJECT_OT_add_plane_item,  Reset_Input_Images, VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel, PlaceImageIn3D
from .testing_operations import DoImg, StMTestImagePrep, StMTestSaveFileToDb, StMTestConnectionOperator, StMTestGetFileFromDbFromUserId, StMTestDeleteFileFromDbFromUserId

from .db_operations import test_connection, save_file_to_db, get_files_by_user_id, delete_files_by_object_id # the . is on purpose. do not remove
from .image_processing import prepare_image, test_feature_detection # the . is on purpose. do not remove
from .bcrypt_password import hash_password
from .authentication import login_account, register_account
import bcrypt # unsure

#FutureReference
#this will contain the filepath and the image plane name
#this has not been implemented yet
# Dataclass to store file path and rotation

UserSignedIn = False

# this contains the main layout for the Sketch to mesh program
# to link up functions with the buttons
# first create the operator 
# find the panel you want the funciton in(this cannot be inside the main function since everything is not inside the main panel except for the other panels)
# use ( row.operator("(the operator you want)", text="(the name of the button)"))
# for now all of the button will create a cube
class VIEW3D_PT_Sketch_To_Mesh_Panel(bpy.types.Panel):  
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"  
    bl_idname = "_PT_Sketch_To_Mesh_Main_Panel" 

    bl_category = "S-T-M"  # Sidebar cName
    bl_label = "Sketch-To-Mesh"  # found at the top of the Panel

    def draw(self, context): 
        layout = self.layout



        
class VIEW3D_PT_Sketch_To_Mesh_Views_Panel(bpy.types.Panel):  
    bl_label = "View"
    bl_idname = "_PT_Views"
    bl_parent_id = "_PT_Sketch_To_Mesh_Main_Panel" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Button to add a new plane item
        row = layout.row()
        layout.operator("object.add_plane_item")



class VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel(bpy.types.Panel):  
    bl_label = "Align Images"
    bl_idname = "_PT_AlignViews"
    bl_parent_id = "_PT_Views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.place_image_in_space", text="Align Image")



class VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel(bpy.types.Panel):  
    bl_label = "MeshSettings"
    bl_idname = "_PT_MeshSettings"
    bl_parent_id = "_PT_Sketch_To_Mesh_Main_Panel"  # Set the parent panel ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Mesh Settings")
        row = layout.row()
        row.prop(context.scene, "poly_count_range", text="Poly Count", slider=True)
        row = layout.row()
        row.operator("mesh.primitive_cube_add", text="Regenerate Preview Mesh")
        row = layout.row()
        row.operator("mesh.primitive_cube_add", text="Export Preview")
        row = layout.row()
        row.prop(context.scene, "mesh_rating", text="Mesh Rating", slider=True)
        row = layout.row()
        layout.label(text="Save Mesh")
        row = layout.row()
        layout.prop(context.scene, "FileName_Input", text="")
        row = layout.row()
        row.operator("mesh.primitive_cube_add", text="Export Mesh")

        
        
class DataBaseLogin(bpy.types.Operator):
    bl_idname = "wm.database_login_popup"
    bl_label = "Database Register/Login"

    DBUserNameInput = ""
    DBPasswordInput = ""

    def execute(self, context):
        # this will send the information to the database
        self.DBUserNameInput = bpy.context.scene.DB_Username
        self.DBPasswordInput = hash_password(bpy.context.scene.DB_Password.encode('utf-8')) # being sent to encryption as bytes. never stored as string!
        
        # now we register/login
        # we try to login first. if none exist, we register it.
        register_result = register_account(self.DBUserNameInput, self.DBPasswordInput)
        
        # currently like this. once we have a new button it will be easier!
        # TODO: refactor this.
        if register_result == -1: # check console error
            self.report({'INFO'}, "Registration error. Check console for more information.")
            
        if register_result == 1: # account/user document created. log in again
            self.report({'INFO'}, "Registration Successful. Please Log in again to access DB.")
            
        if register_result == 0: # account already created. redirect to login
            byte_password = bpy.context.scene.DB_Password.encode('utf-8') # we need to compare plaintext and the hash! not hash against hash...
            user, result = login_account(self.DBUserNameInput, byte_password)
            
            # will be refactored!
            if result == 0: # credentials incorrect
                self.report({'INFO'}, "Credentials Incorrect.")
            if result == 1:
                self.report({'INFO'}, "Login Successful.")
            if result == -1:
                self.report({'INFO'}, "Unregistered account. Please register")    

        return {'FINISHED'}
    
    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        row.prop(context.scene, "DB_Username", text="Username", slider=True) 
        row = layout.row()
        row.prop(context.scene, "DB_Password", text="Password", slider=True) 

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



###this is a example class ###
class ExampleOperator(bpy.types.Operator):
    bl_idname = "load.ExampleName" #the first word is the type of thing your doing(probally should look this up) follow by '.' and the name you want to use to call the operator
    bl_label = "Load Image"
    bl_options = {'REGISTER', 'UNDO'}

    #properities go here

    #this is where you define what you want to happen
    def execute(self, context):
      # Do Something
        return {'FINISHED'}
    
    #this is how you would call the operators in other classes
    #layout.operator("load.ExampleName", text="")
    #text is what you want displayed

    #there need to be called in the register and unregister definetions respectively close to the bottom of the script
    #bpy.utils.register_class(LoadImageOperator) 
    #bpy.utils.unregister_class(LoadImageOperator)
    ###this is the end of the example class ###



def register():
    bpy.types.Scene.poly_count_range = bpy.props.IntProperty(name="Poly Count", default=10, min=0, max=100)
    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_X = bpy.props.IntProperty(name="Image Center X", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_Y = bpy.props.IntProperty(name="Image Center Y", default=10, min=0, max=100)
    bpy.types.Scene.FileName_Input = bpy.props.StringProperty(name="FileName", default="STMFile")
    #Database Properties
    bpy.types.Scene.DB_Username = bpy.props.StringProperty(name="DBUsername", default="")
    bpy.types.Scene.DB_Password = bpy.props.StringProperty(name="DBPassword", default="")
    #Plane data Properites
    bpy.types.Scene.PlaneFilePath = bpy.props.StringProperty(name="File Path",subtype='FILE_PATH')
    bpy.types.Scene.PlaneRotation = bpy.props.IntProperty(name="Image Center Y", default=0, min=-180, max=180)
    #Classes
    bpy.utils.register_class(OBJECT_OT_add_plane_item)
    bpy.utils.register_class(DataBaseLogin)
    bpy.utils.register_class(Reset_Input_Images)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel)
    bpy.utils.register_class(PlaceImageIn3D)
    bpy.utils.register_class(DoImg)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel) 
    # bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Location_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    bpy.utils.register_class(testing_operations.VIEW3D_PT_Sketch_To_Mesh_Testing)
    
    # Tests
    bpy.utils.register_class(StMTestImagePrep)  
    bpy.utils.register_class(StMTestSaveFileToDb) 
    bpy.utils.register_class(StMTestConnectionOperator) 
    bpy.utils.register_class(StMTestGetFileFromDbFromUserId) 
    bpy.utils.register_class(StMTestDeleteFileFromDbFromUserId) 

def unregister():
    del bpy.types.Scene.poly_count_range
    del bpy.types.Scene.mesh_rating
    del bpy.types.Scene.Image_Center_X
    del bpy.types.Scene.Image_Center_Y
    del bpy.types.Scene.FileName_Input
    #Classes
    bpy.utils.unregister_class(UI_Operation.OBJECT_OT_add_plane_item)
    bpy.utils.unregister_class(DataBaseLogin)
    bpy.utils.unregister_class(UI_Operation.Reset_Input_Images)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.unregister_class(UI_Operation.VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel)
    bpy.utils.unregister_class(UI_Operation.PlaceImageIn3D)
    bpy.utils.unregister_class(testing_operations.DoImg)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    #bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Location_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    bpy.utils.unregister_class(testing_operations.VIEW3D_PT_Sketch_To_Mesh_Testing)
    # db test connection and image prep
    # Tests
    bpy.utils.unregister_class(StMTestImagePrep)
    bpy.utils.unregister_class(StMTestConnectionOperator)
    bpy.utils.unregister_class(StMTestSaveFileToDb)
    bpy.utils.unregister_class(StMTestGetFileFromDbFromUserId)
    bpy.utils.unregister_class(StMTestDeleteFileFromDbFromUserId) 

if __name__ == "__main__":
    register()