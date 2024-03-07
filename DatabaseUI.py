import bpy
import os
from bpy.types import Context
from .bcrypt_password import hash_password
from .authentication import login_account, register_account
from .db_operations import get_files_by_user_id, delete_files_by_object_id, save_file_to_db
from .blender_operations import saveObj, decode_file
from .ui_operations import User

class DocumentItem(bpy.types.PropertyGroup): name= bpy.props.StringProperty(name="Document Name")
GlobalDatabaseScene : bpy.types.Scene

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

            bpy.ops.wm.toast_notification(message="Login Successful")
            
            self.report({'INFO'}, "Login Successful.")
            User.UserSignedIn = True
            SetDataBaseList(context, context.scene)

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


class AccessDatabase(bpy.types.Operator): 
    bl_idname = "wm.access_database"
    bl_label = "Access Database"

    def execute(self, context) :
        bpy.ops.wm.toast_notification(message="Database Done")
        return {'FINISHED'}

    def draw(self, context):    
        layout = self.layout
        row = layout.row()
        row.operator('wm.pull_from_database', text='Pull from Database')
        row = layout.row()
        row.template_list("DataBase_UIList", "Database_list", context.scene, "my_document_collection", context.scene, "my_document_index")
        row = layout.row()
        row.operator('wm.delete_from_database', text='Delete')
        row.operator('wm.add_database', text='Export')
        row.operator('wm.import_from_database', text='Import')


        

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    

class DataBase_UIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}: layout.label(text=item.name, icon = custom_icon) 
        elif self.layout_type in {'GRID'}: layout.alignment = 'CENTER'
        layout.label(text="", icon = custom_icon)


def SetDataBaseList(context, databaseScene):
    object_id_str = str(User.user_info[0]['_id'])
    userId = object_id_str # we only want the id string. the object saved is the entire objectId
    User.user_documents = get_files_by_user_id(userId)
        
    if not hasattr(context.scene, "my_document_collection"): # we need to make sure it exists in this scene
        # create the document collection property
        bpy.types.Scene.my_document_collection = bpy.props.CollectionProperty(type=DocumentItem)
    

class DataBaseUIMenu(bpy.types.Panel):
    bl_idname = "wm.database_ui_menu"
    bl_label = "Database Menu"
    bl_parent_id = "_PT_Sketch_To_Mesh_Main_Panel" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):    
        layout = self.layout
        row = layout.row()
        if User.UserSignedIn == False :
            row.operator("wm.database_register", text="Register User")
            row = layout.row()
            row.operator("wm.database_login", text="Login User")
        else :
            row.operator("wm.access_database", text="Access Database") 
            row = layout.row() 
            row.operator("wm.user_logout", text="Logout") # TODO: logout function in authentication
 

class PullFromDatabase(bpy.types.Operator):
    bl_idname = "wm.pull_from_database"
    bl_label = "Pull"

    def execute(self, context): 
        for doc in User.user_documents:
            prop = context.scene.my_document_collection.add() #0 should be the first found property
            prop.name =doc['fileName']
        return{'FINISHED'}
    

class DeleteFromDatabase(bpy.types.Operator):
    bl_idname = "wm.delete_from_database"
    bl_label = "Delete"

    def execute(self, context):
        DatabaseList = context.scene.my_document_collection
        index = context.scene.my_document_index 
        ItemToDeleteName = DatabaseList[index].name
        
        for doc in User.user_documents :
            val:str = doc['fileName']
            if val == ItemToDeleteName:
                dataToDelete = doc['_id']
                delete_files_by_object_id(dataToDelete)
                break
        #DatabaseList[index]['_id'])
        DatabaseList.remove(index) 
        context.scene.my_document_index = min(max(0, index - 1), len(DatabaseList) - 1)
        return{'FINISHED'}
    

class AddToDatabase(bpy.types.Operator):
    bl_idname = "wm.add_database"
    bl_label = "Export"

    def execute(self, context):
        DatabaseList = context.scene.my_document_collection
        filepath = saveObj() #get file name and pass that file name to the save_file_to_db
        save_file_to_db(User.user_info[0]['_id'], filepath[0], filepath[1] )

        curr_item = DatabaseList.add()
        curr_item.name = filepath[1] 
        return{'FINISHED'}
    

class ImportFromDataBase(bpy.types.Operator):
    bl_idname = "wm.import_from_database"
    bl_label = "Import"

    def execute(self, context):
        DatabaseList = context.scene.my_document_collection
        index = context.scene.my_document_index 
        ItemToImportName = DatabaseList[index].name
        ItemToImportExt = ItemToImportName[ItemToImportName.rfind("."):]
       
        for doc in User.user_documents :
            val:str = doc['fileName']
            if val == ItemToImportName:
                DataSave = doc['fileEncoded'] #the saved data from the database
                decode_file(DataSave, ItemToImportExt)
                break

        return{'FINISHED'}