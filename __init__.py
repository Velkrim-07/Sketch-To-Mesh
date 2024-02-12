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
    
import bpy
import cv2
import numpy as np
import os
from dataclasses import dataclass
from .db_operations import test_connection
#this import is not used ye
# from typing import Set 


globalPlaneArray = []
globalfilePathsArray = []

#FutureReference
#@dataclass
#class FilePathStructure:
    #filePath: bpy.props.StringProperty(subtype="FILE_PATH")
    #Description: str



def outline_image(image_path, Extension, ImgName, Filedirectory):
    """Read an image from a path, outline it, calculate the center of mass for the outlines, and draw a blue dot there."""
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found or unable to load.")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contours were found
    if contours:
        # Draw contours on the original image
        cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

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
            cv2.circle(image, (cX, cY), 5, (255, 0, 0), -1)
        else:
            print("Error: Combined center of mass could not be calculated.")
    else:
        print("Error: No contours found.")
        
    os.chdir(Filedirectory) #changes the directory to the folder where we are going to save the file
    cv2.imwrite(ImgName + Extension, image) #saves the image
    os.chdir("..\\") #goes back one directory



#Image to plane code
#       bpy.ops.import_image.to_plane(files=[{"name":"A'shla1.jpg", "name":"A'shla1.jpg"}], directory="C:\\Users\\judah\\Pictures\\Art\\A'shala\\", relative=False)
#

class PlaceImageIn3D(bpy.types.Operator):
    bl_idname = "object.place_image_in_space"
    bl_label ="Reset"

    PlaneArray = globalPlaneArray
    filePathsArray = globalfilePathsArray

    def execute(self, context):
        # holds the rotation for each View
        RotationValue = (0, 0, 0) 
        #this will keep count of the views were have captured
        Itervalue = 0
        #this will be a folder in the sketch-to-Mesh project. This will hold the Image processed
        ImageDiretoryForNewImage = "ImageFolder"
        #this will eventually need to move to somewhere more accessable
        #this is only here for now
        filePathsArray = [bpy.context.scene.front_views_file_path, bpy.context.scene.back_views_file_path,  bpy.context.scene.side_views_file_path ]
    

        for file_path in filePathsArray : 
            NewFilePath: bpy.props.StringProperty(subtype="FILE_PATH")

            if file_path:
                #this is used for the new image. We want to save the new image as the same type of file as the first
                Extension =  file_path[file_path.rfind("."): ] 

                # this decides depending on the view the rotation of the plane object
                match Itervalue :
                    case 0: RotationValue = (90, 0, 0)
                    case 1: RotationValue = (90, 90, 0)
                    case 2: RotationValue = (0, 0, 0)

                #this is the file name for the image we are creating
                ImgName = "View" + str(Itervalue)

                #this is where we want to save the picture so i can be reaccessed
                outline_image(file_path, Extension, ImgName, ImageDiretoryForNewImage)
                #this creates a new file path to the image we just saved
                NewFilePath = os.path.abspath(ImageDiretoryForNewImage + "\\" + ImgName + Extension) 
                
                if NewFilePath:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.paint.texture_paint_toggle()
                    bpy.ops.mesh.primitive_plane_add(size=4, enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=RotationValue, scale=(20, 20, 20))
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    
                    filename = os.path.basename(NewFilePath)
                    FileDirectory = NewFilePath[: NewFilePath.rfind("\\")] + "\\"
                    
                    #bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)

                    plane = bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    self.planeArray.insert(plane) # allows us to access the plane after creation
                else:
                    self.report({'ERROR'}, "No inputted Image.")
                Itervalue = Itervalue + 1
            else:
                self.report({'ERROR'}, "No inputted Image.")
                Itervalue = Itervalue + 1

        return {'FINISHED'}
    
    

# this contains the main layout for the Sketch to mesh program
 # right now the program will not really do anything. 
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

# import cv2
from .image_processing import prepare_image # the . is on purpose. do not remove
class StMTestImagePrep(bpy.types.Operator):
    bl_idname = "wm.prepare_image_operator"
    bl_label = "Test Image Prep"

    def execute(self, context):
        
        path = 'C:/Users/RAFAEL MUITO ZIKA/Desktop/Test/front.png'
        success = prepare_image(path)
        if success:
            self.report({'INFO'}, "Image Prep Succesful!")
        else:
            self.report({'ERROR'}, "Failed to Image Prep.")

        return {'FINISHED'}
     


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
        row.operator("wm.test_connection_operator", text="Test Connection")



class DoImg(bpy.types.Operator):
    bl_idname = "object.do_img"
    bl_label = "Place Image"

    #Property that holds the filepath that will be used to insert the image
    myFilePath: bpy.props.StringProperty(subtype="FILE_PATH")

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


        row.operator("wm.prepare_image_operator", text="Test Image Prep")


class VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel(bpy.types.Panel):  
    bl_label = "AlignViews"
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
    bpy.types.Scene.front_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Front View")
    bpy.types.Scene.back_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Back View")
    bpy.types.Scene.side_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH", description="Side View")
    bpy.types.Scene.poly_count_range = bpy.props.IntProperty(name="Poly Count", default=10, min=0, max=100)
    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_X = bpy.props.IntProperty(name="Image Center X", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_Y = bpy.props.IntProperty(name="Image Center Y", default=10, min=0, max=100)
    bpy.types.Scene.FileName_Input = bpy.props.StringProperty(name="FileName", default="STMFile")
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.register_class(PlaceImageIn3D)
    bpy.utils.register_class(DoImg)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel) 
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    # ralf changes
    bpy.utils.register_class(StMTestConnectionOperator)
    
   # db test connection and image prep
    bpy.utils.register_class(StMTestConnectionOperator) 
    bpy.utils.register_class(StMTestImagePrep)  


def unregister():
    del bpy.types.Scene.front_views_file_path
    del bpy.types.Scene.back_views_file_path
    del bpy.types.Scene.side_views_file_path
    del bpy.types.Scene.poly_count_range
    del bpy.types.Scene.mesh_rating
    del bpy.types.Scene.Image_Center_X
    del bpy.types.Scene.Image_Center_Y
    del bpy.types.Scene.FileName_Input
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.unregister_class(PlaceImageIn3D)
    bpy.utils.unregister_class(DoImg)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    # ralf changes
    bpy.utils.unregister_class(StMTestConnectionOperator)

    # db test connection and image prep
    bpy.utils.unregister_class(StMTestImagePrep)
    bpy.utils.unregister_class(StMTestConnectionOperator)

if __name__ == "__main__":
    register()