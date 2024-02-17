import bpy
import os
from dataclasses import dataclass
from .testing_operations import outline_image

# bpy.ops.wm.save_as_mainfile(filepath="c:\Users\James Burns\Documents\TestFile.blend")

# this will be called once the images are ready
#FutureReference
#this will contain the filepath and the image plane name
#this has not been implemented yet
@dataclass
class FilePathStructure:
    filePath: str
    ImagePlaneName: str

GlobalFileImageStructArray = [] #this will eventually replace the two array under this
globalPlaneArray = [] # a list of the names of the planes in Blender
globalfilePathsArray = [] # a list of the file path we wan to keep track of

UserSignedIn = False

class Reset_Input_Images(bpy.types.Operator): 
    bl_idname = "object.reset_selected_images"
    bl_label = "Reset_Images"
    
    myFilePathArray = globalfilePathsArray # saves the entries in the global list to be deleted
    ImagePanelArray = globalPlaneArray
    globalPlaneArray.clear()
    globalfilePathsArray.clear() # clears the global list 

    def execute(self, context):
        Itervalue = 0

        for filePath in self.myFilePathArray :
            #Finds the Images Saved
            ImageFilePath = os.path.abspath("ImageFolder\\" + "View" + str(Itervalue) + filePath[filePath.rfind("."): ] ) 
            # if we find that file we will delete it
            if ImageFilePath:
                os.remove(ImageFilePath)

        for images in self.ImagePanelArray:
            # selects the image plane in the array 
            bpy.data.objects[images].select_set(True)
            #deletes the image plane in the array
            bpy.ops.object.delete(use_global=False, confirm=False)
        return {'FINISHED'}
    

class PlaceImageIn3D(bpy.types.Operator):
    bl_idname = "object.place_image_in_space"
    bl_label ="Place Images"

    PlaneArray = globalPlaneArray
    filePathsArray = globalfilePathsArray

    def execute(self, context):
        #this will keep count of the views were have captured
        Itervalue = 0
        #this will be a folder in the sketch-to-Mesh project. This will hold the Image processed
        ImageDiretoryForNewImage = "ImageFolder"
        #this will eventually need to move to somewhere more accessable
        #this is only here for now
        filePathsArray = [bpy.context.scene.front_views_file_path, bpy.context.scene.back_views_file_path,  bpy.context.scene.side_views_file_path ]
    
        for file_path in filePathsArray : 
            if file_path :
                #this is used for the new image. We want to save the new image as the same type of file as the first
                Extension =  file_path[file_path.rfind("."): ] 

                #this is the file name for the image we are creating
                ImgName = "View" + str(Itervalue)
                self.PlaneArray.insert(Itervalue, ImgName) # allows us to access the plane after creation

                #this is where we want to save the picture so i can be reaccessed
                outline_image(file_path, Extension, ImgName, ImageDiretoryForNewImage)

                #this creates a new file path to the image we just saved
                NewFilePath = os.path.abspath(ImageDiretoryForNewImage + "\\" + ImgName + Extension) 
                
                if NewFilePath:
                    filename = os.path.basename(NewFilePath)
                    FileDirectory = NewFilePath[: NewFilePath.rfind("\\")] + "\\"

                    #bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=FileDirectory, relative=False)
                    #we set the rotation and location of each plane
                    bpy.data.objects[ImgName].select_set(True)
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
