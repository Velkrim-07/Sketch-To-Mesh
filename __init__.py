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
import cv2
import numpy as np
import os
from dataclasses import dataclass
from .db_operations import test_connection, save_file_to_db
from .image_processing import prepare_image, test_feature_detection # the . is on purpose. do not remove
#this import is not used yet
# from typing import Set 

#FutureReference
#this will contain the filepath and the image plane name
#this has not been implemented yet
# Dataclass to store file path and rotation
@dataclass
class PlaneItem:
    PlaneFilepath = bpy.props.StringProperty(name="File Path",subtype='FILE_PATH')
    PlaneRotation = bpy.props.IntProperty(name="Rotation", default=0)
    ImagePlaneName: str
    
    def __init__(self, filepath ,rotation):
        self.PlaneFilepath = filepath
        self.PlaneRotation = rotation



GlobalPlaneDataArray : list[PlaneItem] = [] #this will eventually replace the two array under this
UserSignedIn = False



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



def outline_image(image_path, Extension, ImgName, Filedirectory):
    """Read an image from a path, outline it, calculate the center of mass for the outlines, and draw a blue dot there."""
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Image not found or unable to load.")
        return
    
    # temporary file size. adjusting files to the same scale can be beneficial for feature detectors
    resized_image = cv2.resize(image, (800, 600))  
    # grayscale reduces computational load
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) 
    # noise reduction
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    # canny edge detection emphasizes edges in the image
    # we will most likely be using one of the two as feature detectors: ORB, AKAZE.
    # both feature detection algorithms have positive results from this as they often rely on edge information to find key points.
    edges = cv2.Canny(blurred_image, 50, 15, apertureSize=3)
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours were found
    if contours:
        # Draw contours on the original image
        cv2.drawContours(resized_image, contours, -1, (0, 255, 0), 2)
        # Calculate the combined center of mass for all contours
        totalX, totalY, totalArea = 0, 0, 0

        for contour in contours:
            M = cv2.moments(contour)

            if M["m00"] != 0:
                totalX += int(M["m10"])
                totalY += int(M["m01"])
                totalArea += M["m00"]

        if totalArea != 0:
            cX = int(totalX / totalArea)
            cY = int(totalY / totalArea)
            # Draw a blue dot at the combined center of mass
            cv2.circle(resized_image, (cX, cY), 5, (255, 0, 0), -1)
        else:
            print("Error: Combined center of mass could not be calculated.")
    else:
        print("Error: No contours found.")

    os.chdir(Filedirectory) #changes the directory to the folder where we are going to save the file
    cv2.imwrite(ImgName + Extension, resized_image) #saves the image
    os.chdir("..\\") #goes back one directory



class PlaceImageIn3D(bpy.types.Operator):
    bl_idname = "object.place_image_in_space"
    bl_label ="Place Images"

    def execute(self, context):
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
                #this is the file name for the image we are creating
                plane_data.ImagePlaneName = "View" + str(Itervalue)
                # allows us to access the plane after creation
                #this is where we want to save the picture so i can be reaccessed
                outline_image(plane_data.PlaneFilepath, Extension, plane_data.ImagePlaneName, ImageDiretoryForNewImage)
                #this creates a new file path to the image we just saved
                NewFilePath = os.path.abspath(ImageDiretoryForNewImage + "\\" + plane_data.ImagePlaneName + Extension) 
                
                if NewFilePath:
                    filename = os.path.basename(NewFilePath)
                    FileDirectory = NewFilePath[: NewFilePath.rfind("\\")] + "\\"
                    #bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    #we set the rotation and location of each plane
                    bpy.data.objects[plane_data.ImagePlaneName].select_set(True)
                    match Itervalue :
                        case 1: bpy.ops.transform.translate(value=(-0.01, 0 , 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False, alt_navigation=True)
                        case 2: bpy.context.object.rotation_euler[2] = 0
                else:
                    match Itervalue:
                        case 0: MissingView = "FontView"
                        case 1: MissingView = "BackView"
                        case 2: MissingView = "SideView"
                    self.report({'ERROR'}, "No inputted Image for" + MissingView)
                Itervalue = Itervalue + 1
            else:
                self.report({'ERROR'}, "No inputted Image.")
                Itervalue = Itervalue + 1

        return {'FINISHED'}



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



class Reset_Input_Images(bpy.types.Operator): 
    bl_idname = "object.reset_selected_images"
    bl_label = "Reset_Images"

    def execute(self, context):
        Itervalue = 0

        for plane_data in GlobalPlaneDataArray :
            #Finds the Images Saved
            ImageFilePath = os.path.abspath("ImageFolder\\" + "View" + str(Itervalue) + plane_data.PlaneFilepath[plane_data.PlaneFilepath.rfind("."): ] ) 
            # if we find that file we will delete it
            if ImageFilePath: os.remove(ImageFilePath)
            # selects the image plane in the array 
            bpy.data.objects[plane_data.ImagePlaneName].select_set(True)
            #deletes the image plane in the array
            bpy.ops.object.delete(use_global=False, confirm=False)
            #increases the itervale to reach the next View string
            Itervalue = Itervalue + 1 

        # clears the PlaneData Array
        GlobalPlaneDataArray.clear() 
        return {'FINISHED'}
    


class StMTestSaveFileToDb(bpy.types.Operator):
    bl_idname = "wm.save_file_to_db_operator"
    bl_label = "Test Saving File"

    def execute(self, context):
        save_file_to_db("123") # needs a file path but are not using
        
        #success = prepare_image(path)
        #if success:
        #    self.report({'INFO'}, "Image Prep Succesful!")
        #else:
        #    self.report({'ERROR'}, "Failed to Image Prep.")

        return {'FINISHED'}
    

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
        row.prop(context.scene, "PlaneFilePath", text="FilePath : ") 
        row = layout.row()
        row.prop(context.scene, "PlaneRotation", text="Rotation : ", slider=True) 

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel(bpy.types.Panel):  
    bl_label = "FilePath List"
    bl_idname = "_PT_Views_File_Path"
    bl_parent_id = "_PT_Views" 
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # List current plane items
        for item in GlobalPlaneDataArray:
            box = layout.box()
            col = box.row()
            filename = os.path.basename(item.PlaneFilepath)
            col.label(text="Name: " + filename + "Rotation: " + str(item.PlaneRotation))

        row = layout.row()
        row.operator("object.reset_selected_images", text="Reset Images")



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
    bl_label = "Test Image Prep"

    DBUserNameInput = ""
    DBPasswordInput = ""

    def execute(self, context):
        # this will send the information to the database
        self.DBUserNameInput = bpy.context.scene.DB_Username
        self.DBPasswordInput = bpy.context.scene.DB_Password# password will be encrypted
        return {'FINISHED'}
    
    def draw(self, context):    
        layout = self.layout   
        row = layout.row()
        row.prop(context.scene, "DB_Username", text="User Name: ", slider=True) 
        row = layout.row()
        row.prop(context.scene, "DB_Password", text="Password: ", slider=True) 

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
    bpy.utils.register_class(StMTestConnectionOperator) 
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Testing)
    # db test connection and image prep
    bpy.utils.register_class(StMTestImagePrep)  
    # StMTestSaveFileToDb
    bpy.utils.register_class(StMTestSaveFileToDb) 

def unregister():
    del bpy.types.Scene.poly_count_range
    del bpy.types.Scene.mesh_rating
    del bpy.types.Scene.Image_Center_X
    del bpy.types.Scene.Image_Center_Y
    del bpy.types.Scene.FileName_Input
    #Classes
    bpy.utils.unregister_class(OBJECT_OT_add_plane_item)
    bpy.utils.unregister_class(DataBaseLogin)
    bpy.utils.unregister_class(Reset_Input_Images)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_FilePath_Panel)
    bpy.utils.unregister_class(PlaceImageIn3D)
    bpy.utils.unregister_class(DoImg)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    #bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Location_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    bpy.utils.unregister_class(StMTestConnectionOperator)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Testing)
    # db test connection and image prep
    bpy.utils.unregister_class(StMTestImagePrep)
    #StMTestSaveFileToDb
    bpy.utils.unregister_class(StMTestSaveFileToDb)

if __name__ == "__main__":
    register()