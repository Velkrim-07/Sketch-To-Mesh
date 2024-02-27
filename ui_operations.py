import bpy
import os
import cv2
import os.path
from os import path
from dataclasses import dataclass
from .image_processing import prepare_image, detect_and_describe_akaze, outline_image, match_features, draw_matches
from .bcrypt_password import hash_password
from .authentication import login_account, register_account
from .db_operations import get_files_by_user_id


@dataclass
class PlaneItem:
    PlaneFilepath = bpy.props.StringProperty(name="File Path",subtype='FILE_PATH')
    PlaneRotation = bpy.props.IntProperty(name="Rotation", default=0)
    ImagePlaneName: str
    ImagePlaneFilePath: str
    
    def __init__(self, filepath ,rotation):
        self.PlaneFilepath = filepath
        self.PlaneRotation = rotation

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
GlobalPlaneDataArray : list[PlaneItem] = [] #this will eventually replace the two array under this
  
# Operator to add a new plane item
class OBJECT_OT_add_plane_item(bpy.types.Operator):
    bl_idname = "object.add_plane_item"
    bl_label = "Add Plane Item"

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
    bl_label ="Place Images"

    def execute(self, context):
        Feature_detection(self=self, PlaneDataArray=GlobalPlaneDataArray)
        return {'FINISHED'}
    

class Reset_Input_Images(bpy.types.Operator): 
    bl_idname = "object.reset_selected_images"
    bl_label = "Reset_Images"

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
        
# TODO: remove from ui-operations to image_processing
def Feature_detection(self, PlaneDataArray : list[PlaneItem]):
    KeyPoints: list = []
    Descriptors: list = []
    Matches: list = []
    Images: list = []
    Matched_Images: list = []
    ImageNames: list = []
    
    PlaceImage(self) # processes the images

    if(PlaneDataArray.__len__() > 1):
        PlaneIndex = 0
        for PlaneData in PlaneDataArray:
            keypoints1, descriptors1 = detect_and_describe_akaze(PlaneData.PlaneFilepath)
            Images.append(cv2.imread(PlaneData.PlaneFilepath))
            KeyPoints.append(keypoints1)
            Descriptors.append(descriptors1)
            ImageNames.append("MatchedView" + str(PlaneIndex) + PlaneData.PlaneFilepath[PlaneData.PlaneFilepath.rfind("."): ] ) 

        #this should follow this format : #12 #23 #31
        DescriptionIndex = 0
        for descriptors in Descriptors:
            if(DescriptionIndex + 1 != Descriptors.__len__()): NextDesc = Descriptors[DescriptionIndex + 1] #Gets the next descriptor 
            else: NextDesc = Descriptors[0] # if we get to the last index
            Matches.append(match_features(descriptors, NextDesc, method='AKAZE')) 
            DescriptionIndex = DescriptionIndex + 1 

        IndexForKeypoints = 0
        for Keypoint in KeyPoints:
            if(IndexForKeypoints + 1 != KeyPoints.__len__()):
                NextKey = KeyPoints[IndexForKeypoints + 1] #Gets the next descriptor
                NextImage = Images[IndexForKeypoints + 1]
            else:
                NextKey = KeyPoints[0] # if we get to the last index
                NextImage = Images[0]
            Matched_Images.append(draw_matches(Images[IndexForKeypoints], Keypoint, NextImage, NextKey, Matches[IndexForKeypoints]))
            IndexForKeypoints = IndexForKeypoints + 1

        MImageIndex = 0
        for MImages in Matched_Images:
            try:
                os.chdir("Matched_Images_Folder") #changes the directory to the folder where we are going to save the file
                cv2.imwrite(ImageNames[MImageIndex], MImages) #saves the image
                os.chdir("..\\") #goes back one directory   
                print(f"Image prep done.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False

# TODO: move to blend-operations
def PlaceImage(self):
     #this will keep count of the views were have captured
        Itervalue = 0
        #this will be a folder in the sketch-to-Mesh project. This will hold the Image processed
        ImageDiretoryForNewImage = "ImageFolder"
        #this will eventually need to move to somewhere more accessable
        #this is only here for now
    
        for plane_data in GlobalPlaneDataArray : 
            if plane_data :
                #this is used for the new image. We want to save the new image as the same type of file as the first
                Extension =  plane_data.PlaneFilepath[plane_data.PlaneFilepath.rfind("."): ] 
                plane_data.ImagePlaneName = "View" + str(Itervalue) #this is the file name for the image we are creating
                # allows us to access the plane after creation
                outline_image(plane_data.PlaneFilepath, Extension, plane_data.ImagePlaneName, ImageDiretoryForNewImage)
                #this creates a new file path to the image we just saved
                plane_data.ImagePlaneFilePath = os.path.abspath(ImageDiretoryForNewImage + "\\" + plane_data.ImagePlaneName + Extension) 
                
                if plane_data.ImagePlaneFilePath:
                    filename = os.path.basename(plane_data.ImagePlaneFilePath)
                    FileDirectory = plane_data.ImagePlaneFilePath[: plane_data.ImagePlaneFilePath.rfind("\\")] + "\\"
                    #bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    #we set the rotation and location of each plane
                    bpy.data.objects[plane_data.ImagePlaneName].select_set(True)
                    match Itervalue :
                        case 1: bpy.ops.transform.translate(value=(-0.01, 0 , 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, alt_navigation=True)
                        case 2: bpy.context.object.rotation_euler[2] = 0
                else:
                    match Itervalue:
                        case 0: MissingView = "FrontView"
                        case 1: MissingView = "BackView"
                        case 2: MissingView = "SideView"
                    self.report({'ERROR'}, "No inputted Image for" + MissingView)
                Itervalue = Itervalue + 1
            else:
                self.report({'ERROR'}, "No inputted Image.")
                Itervalue = Itervalue + 1

