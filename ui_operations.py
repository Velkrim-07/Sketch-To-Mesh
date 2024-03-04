import bpy
import os
import os.path
import blf
import bpy.types
from os import path
import numpy as np
from dataclasses import dataclass
from .image_processing import Feature_detection, PlaneItem
from .bcrypt_password import hash_password
from .authentication import login_account, register_account
from .db_operations import get_files_by_user_id
from .blender_operations import DrawAllMeshesToScreen

@dataclass
class UserData:
    UserSignedIn = False
    user_info = []
    user_documents = []
    def __init__(self, SignIn):
        self.user_info = []
        self.user_documents = [] # testing
        self.UserSignedIn = SignIn

User: UserData = UserData(False)
GlobalPlaneDataArray : list[PlaneItem] = [] # this will eventually replace the two array under this

def draw_callback_px(self, context, message):
    font_id = 0
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20)
    blf.draw(font_id, message)
    
class NotificationPopup(bpy.types.Operator):
    bl_idname = "wm.toast_notification"
    bl_label = "Show Toast Notification"
    
    message: bpy.props.StringProperty(name="Message",description="The message to display in the toast",default="Toast Notification!" )

    def execute(self, context):
        args = (self, context, self.message)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        self.report({'INFO'}, "OK Pressed")
        return {'FINISHED'}

    def invoke(self, context, event):    
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        self.layout.label(text=self.message)
  
# Operator to add a new plane item
# adds new image to be analyzed
class OBJECT_OT_add_plane_item(bpy.types.Operator):
    bl_idname = "object.add_plane_item"
    bl_label = "Add Plane Item"
    bl_description = "Select and add new images to be processed"

    def execute(self, context):
        #adds the plane Itme to the Plane Item List
        NewFileRotationPair = PlaneItem(bpy.context.scene.PlaneFilePath, bpy.context.scene.PlaneRotation )
        GlobalPlaneDataArray.append(NewFileRotationPair)
        return {'FINISHED'}

    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        row.prop(context.scene, "PlaneFilePath", text="FilePath ") 
        row = layout.row()
        row.prop(context.scene, "PlaneRotation", text="Rotation ", slider=True) 

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel(bpy.types.Panel):  
    bl_label = "Views"
    bl_idname = "_PT_Views_File_Path"
    bl_parent_id = "_PT_Sketch_To_Mesh_Main_Panel" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self,context):
        return context.mode == 'OBJECT'
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.operator("object.add_plane_item", text="Add Image")

        box = layout.box()

        # List current plane items
        for item in GlobalPlaneDataArray:
            col = box.row()
            col.label(text="Name: " + os.path.basename(item.PlaneFilepath) + "Rotation: " + str(item.PlaneRotation))

        row = layout.row()
        row.operator("object.place_image_in_space", text="Confirm Images")
        row = layout.row()
        row.operator("object.reset_selected_images", text="Reset Images")


class PlaceImageIn3D(bpy.types.Operator):
    bl_idname = "object.place_image_in_space"
    bl_label = "Place Images"
    bl_description = "Sends images to feature detection" # rework possibly?

    def execute(self, context):
        Feature_detection(self=self, PlaneDataArray=GlobalPlaneDataArray)
        return {'FINISHED'}


class Reset_Input_Images(bpy.types.Operator): 
    bl_idname = "object.reset_selected_images"
    bl_label = "Reset_Images"
    bl_description = "Reset previously selected images"

    def execute(self, context):
        Itervalue = 0

        for plane_data in GlobalPlaneDataArray :
            #Finds the Images Saved
            ImageFilePath = os.path.abspath("ImageFolder\\" + "View" + str(Itervalue) + plane_data.PlaneFilepath[plane_data.PlaneFilepath.rfind("."): ] ) 
            if path.exists(ImageFilePath): 
                os.remove(ImageFilePath) # if we find that file we will delete it
                # selects the image plane in the array 
                bpy.data.objects[plane_data.ImagePlaneName].select_set(True)
                #deletes the image plane in the array
                bpy.ops.object.delete(use_global=False, confirm=False)
                #increases the itervale to reach the next View string
            Itervalue = Itervalue + 1 

        # clears the PlaneData Array
        GlobalPlaneDataArray.clear() 
        return {'FINISHED'}


class DataBaseLogin(bpy.types.Operator):
    bl_idname = "wm.database_login"
    bl_label = "Database Login"
    bl_description = "Login into the Database in order to access user stored data"

    DBUserNameInput = ""
    DBPasswordInput = ""

    def execute(self, context):
        # this will send the information to the database
        self.DBUserNameInput = bpy.context.scene.DB_Username
        self.DBPasswordInput = hash_password(bpy.context.scene.DB_Password.encode('utf-8')) # being sent to encryption as bytes. never stored as string!
           
        byte_password = bpy.context.scene.DB_Password.encode('utf-8') # we need to compare plaintext and the hash! not hash against hash...
        user, result = login_account(self.DBUserNameInput, byte_password)

        User.user_info = user # saving the user id to the user
            
            # will be refactored!
        if result == 0: # credentials incorrect
            self.report({'INFO'}, "Credentials Incorrect.")
        if result == 1:
            
            bpy.ops.wm.toast_notification('INVOKE_DEFAULT', message="Login Successful")
            
            self.report({'INFO'}, "Login Successful.")
            User.UserSignedIn = True
        if result == -1:
            self.report({'INFO'}, "Unregistered account. Please register")    

        return {'FINISHED'}
    
    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        row.prop(context.scene, "DB_Username", text="Username", slider=True) 
        row = layout.row()
        row.prop(context.scene, "DB_Password", text="Password", slider=True, ) 


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class DataBaseLogout(bpy.types.Operator):
    bl_idname = "wm.user_logout"
    bl_label = "Logout"
    bl_description = "Logout from the Database"
    
    def execute(self, context):
    
        User.user_documents = []
        User.user_info = []
        User.UserSignedIn = False
        
        # Use the provided context for consistency
        for area in context.screen.areas: # redraw changes
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, "Logout Successful.")
        return {'FINISHED'}

class DataBaseRegister(bpy.types.Operator):
    bl_idname = "wm.database_register"
    bl_label = "Database Register"
    bl_description = "Register new account to utilize Database services"

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
            self.report({'INFO'}, "Account already Registered.")
        return {'FINISHED'}
    
    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        row.prop(context.scene, "DB_Username", text="Username", slider=True) 
        row = layout.row()
        row.prop(context.scene, "DB_Password", text="Password", slider=True) 


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class DataBaseUIMenu(bpy.types.Panel):
    bl_idname = "wm.database_ui_menu"
    bl_label = "Database Menu"
    bl_parent_id = "_PT_Testing_Panel" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self,context):
        return context.mode == 'OBJECT'

    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        if User.UserSignedIn == False :
            row.operator("wm.database_register", text="Register User")
            row = layout.row()
            row.operator("wm.database_login", text="Login User")
        else :
            row.operator("wm.database_access_menu", text="Access Database") 
            row = layout.row()
            row.operator("wm.user_logout", text="Logout") # TODO: logout function in authentication
    

class DocumentItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Document Name")

# scenario: user is logged in and clicked AccessDB button. 
# functionality: we already have user information saved in the data structure. now we must just get his documents from db
class UserAccessDb(bpy.types.Operator):
    bl_idname = "wm.database_access_menu"
    bl_label = "Access Database"
    bl_description = "Retrieve or upload documents into the Database"

    def execute(self, context):
        
        object_id_str = str(User.user_info[0]['_id'])
        userId = object_id_str # we only want the id string. the object saved is the entire objectId
        User.user_documents = get_files_by_user_id(userId)
        
        if not hasattr(context.scene, "my_document_collection"): # we need to make sure it exists in this scene
            # create the document collection property
            bpy.types.Scene.my_document_collection = bpy.props.CollectionProperty(type=DocumentItem)
            bpy.types.Scene.my_document_index = bpy.props.IntProperty()
        
        document_collection = context.scene.my_document_collection
        document_collection.clear()
        for doc in User.user_documents:
            item = document_collection.add()
            item.name = doc['fileName']
    
    
        bpy.ops.wm.window_new()
        new_window = context.window_manager.windows[-1]
        
        # find a scripting screen or use a fallback
        scripting_screen = bpy.data.screens.get('Scripting')
        if scripting_screen is None:
            scripting_screen = bpy.data.screens.get('Layout')  # 'Layout' is a default screen in blender

        # demonic line of codes. will be removed
        if scripting_screen is not None:
            new_window.screen = scripting_screen
            text_editor_area = None
            for area in new_window.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    text_editor_area = area
                    break

            if text_editor_area is None and new_window.screen.areas:

                new_window.screen.areas[0].type = 'TEXT_EDITOR'
        else:
            self.report({'WARNING'}, "No 'Scripting' or 'Layout' screen found. Cannot open the desired screen.")
            return {'CANCELLED'}
        return {'FINISHED'}
        

class TestPlaceMesh(bpy.types.Operator):
    bl_idname = "wm.place_mesh"
    bl_label ="Place Mesh"

    def execute(self, context):
        DrawAllMeshesToScreen((0, 255, 0), 5, self, GlobalPlaneDataArray)
        return {'FINISHED'}
