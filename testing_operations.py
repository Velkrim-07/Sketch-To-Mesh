import bpy
import cv2
import os
from .db_operations import test_connection, save_file_to_db, get_files_by_user_id, delete_files_by_object_id # the . is on purpose. do not remove
from .image_processing import prepare_image, test_feature_detection # the . is on purpose. do not remove

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
    

class StMTestGetFileFromDbFromUserId(bpy.types.Operator):
    bl_idname = "wm.get_file_from_db_operator"
    bl_label = "Test Getting File"

    def execute(self, context):
        
        result = get_files_by_user_id("123") # 123 since the only document in the db is 123
        
        for document in result:
            # removed the bin data because it was too annoying as the output. fileEncoded: {document['fileEncoded']}
            print(f"objectId: {document['_id']}, filename: {document['fileName']}, userId: {document['userId']}, insertedDate: {document['insertedDate']}")

        return {'FINISHED'}
    

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
        save_file_to_db("123") # needs a file path but are not using

        return {'FINISHED'}
    

    # wth is this? why is this here and not in a proper file? why does this method even exists? sigh.

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
