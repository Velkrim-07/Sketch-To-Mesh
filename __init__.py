bl_info = {
    "name": "Sketch_To_Mesh",
    "author": "LuckyNinjas",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > My Custom Panel category",
    "description": "The Inital UI skeleton",
    "category": "Development",
}
    
import bpy
import numpy as np

from .testing_operations import StMTestImagePrep, StMTestConnectionOperator, DoImg, StMTestGetFileFromDbFromUserId, StMTestDeleteFileFromDbFromUserId, StMTestSaveFileToDb
from .ui_operations import PlaceImageIn3D, Reset_Input_Images
from .bcrypt_password import hash_password
from .authentication import login_account, register_account
   
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
        row = layout.row()
        row.prop(context.scene, "front_views_file_path", text="Front View")
        row = layout.row()
        row.prop(context.scene, "back_views_file_path", text="Back View")
        row = layout.row()
        row.prop(context.scene, "side_views_file_path", text="Side View")
        row = layout.row()
        row.operator("object.reset_selected_images", text="Reset Images")


class VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel(bpy.types.Panel):  
    bl_label = "Align_Location"
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


class VIEW3D_PT_Sketch_To_Mesh_Testing(bpy.types.Panel):  
    bl_label = "Testing"
    bl_idname = "_PT_Testing_Panel"
    bl_parent_id = "_PT_Sketch_To_Mesh_Main_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.test_connection_operator", text="Test Connection")
        row = layout.row()
        row.operator("wm.database_login_popup", text="Access Database")
        row = layout.row()
        row.operator("wm.prepare_image_operator", text="Test Image Prep")
        row = layout.row()
        row.operator("wm.save_file_to_db_operator", text="Save File to DB")
        row = layout.row()
        row.operator("wm.get_file_from_db_operator", text="Get File from DB")
        row = layout.row()
        row.operator("wm.delete_file_from_db_operator", text="Delete File from DB")


def register():
    bpy.types.Scene.front_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Front View")
    bpy.types.Scene.back_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Back View")
    bpy.types.Scene.side_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Side View")
    bpy.types.Scene.poly_count_range = bpy.props.IntProperty(name="Poly Count", default=10, min=0, max=100)
    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_X = bpy.props.IntProperty(name="Image Center X", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_Y = bpy.props.IntProperty(name="Image Center Y", default=10, min=0, max=100)
    bpy.types.Scene.FileName_Input = bpy.props.StringProperty(name="FileName", default="STMFile")
    
    #Database Properties
    bpy.types.Scene.DB_Username = bpy.props.StringProperty(name="DBUsername", default="")
    bpy.types.Scene.DB_Password = bpy.props.StringProperty(name="DBPassword", default="")


    bpy.utils.register_class(DataBaseLogin)
    bpy.utils.register_class(Reset_Input_Images)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.register_class(PlaceImageIn3D)
    bpy.utils.register_class(DoImg)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel) 
    # bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Location_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Testing)
    
    # Tests
    bpy.utils.register_class(StMTestImagePrep)  
    bpy.utils.register_class(StMTestSaveFileToDb) 
    bpy.utils.register_class(StMTestConnectionOperator) 
    bpy.utils.register_class(StMTestGetFileFromDbFromUserId) 
    bpy.utils.register_class(StMTestDeleteFileFromDbFromUserId) 


def unregister():
    del bpy.types.Scene.front_views_file_path
    del bpy.types.Scene.back_views_file_path
    del bpy.types.Scene.side_views_file_path
    del bpy.types.Scene.poly_count_range
    del bpy.types.Scene.mesh_rating
    del bpy.types.Scene.Image_Center_X
    del bpy.types.Scene.Image_Center_Y
    del bpy.types.Scene.FileName_Input

    bpy.utils.unregister_class(DataBaseLogin)
    bpy.utils.unregister_class(Reset_Input_Images)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.unregister_class(PlaceImageIn3D)
    bpy.utils.unregister_class(DoImg)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    #bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Location_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Testing)

    # Tests
    bpy.utils.unregister_class(StMTestImagePrep)
    bpy.utils.unregister_class(StMTestConnectionOperator)
    bpy.utils.unregister_class(StMTestSaveFileToDb)
    bpy.utils.unregister_class(StMTestGetFileFromDbFromUserId)
    bpy.utils.unregister_class(StMTestDeleteFileFromDbFromUserId) 

if __name__ == "__main__":
    register()