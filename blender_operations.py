import bpy
import os
import math
import cv2
from .db_operations import save_file_to_db
from .image_processing import PlaneItem



def saveObj():
    filepath = os.path.abspath("ExportFolder\\TempExport.fbx")
    bpy.ops.object.select_all()
    bpy.ops.export_mesh.stl(filepath=filepath,  check_existing=True, use_selection=True)

    save_file_to_db(filepath)

def GetlistOfPixels(ColorWeAreLookingFor, GlobalPlaneDataArray:list[PlaneItem]): #[0, 255, 0] # Green at the moment.
    ImageDictionary = {}
    for plane in GlobalPlaneDataArray:
        image = cv2.imread(plane.ImagePlaneFilePath)
        imageSize = image.size
        imagedata = [image.shape[0], image.shape[1]]
        

    # 0 = left, 1 = right, 2 = middle right, 3 =middle left
    for iterator in range(3):
        PixelsList: list = [] #we want our list ot be reset at the start of every cycle
        row = 0; column = 0
        match iterator: # this will loop through the image and gather the green pxiels outlined on each side
            case 0: # this will get the pixels lining the left side
                for Pixel in range(imageSize): # this just counts for now
                    if not(Pixel == [0, 0]):  Pixel = [row, column] # if we are not at the beginning we want to start at last pixel 
                    elif Pixel[1] == imagedata[1]: # if we get to the end of the row
                        row = row + 1; column = 0  #row is increase to get to the next row and column is reset
                    elif image[Pixel] == ColorWeAreLookingFor: # if we find the color green 
                        PixelsList.append((row, column)) # if we find a pixel we are looking for we add it to the pixel List
                        row = row + 1; column = 0  #row is increase to get to the next row and column is reset
                    elif Pixel == imageSize: break; #we get to the end of the list
                column = column + 1 #column is increase at the end of everycycle

            case 1: # this will get the pixel lining the right side
               for Pixel in reversed(range(imageSize)): # this just counts for now
                    if not(Pixel == [imagedata[0], imagedata[1]]):  Pixel = [row, column] # if we are not at the beginning we want to start at last pixel 
                    elif Pixel[1] == 0: # if we get to the end of the row
                        row = row + 1;  imagedata[1]  #row is increase to get to the next row and column is reset
                    elif image[Pixel] == ColorWeAreLookingFor: # if we find the color green 
                        PixelsList.append((row, column)) # if we find a pixel we are looking for we add it to the pixel List
                        row = row + 1;  imagedata[1]  #row is increase to get to the next row and column is reset
                    elif Pixel == imageSize: break; #we get to the end of the list
                    column = column - 1 #column is increase at the end of everycycle
            case 2: 
                DefineInsidePixels(Pixel, imageSize, imagedata, image, ColorWeAreLookingFor, "Right")
            case 3:
                DefineInsidePixels(Pixel, imageSize, imagedata, image, ColorWeAreLookingFor, "Left")               
        ImageDictionary[iterator] = PixelsList #the pixel list is added at in the dictionary
    return ImageDictionary

def DefineInsidePixels(Pixel, imageSize, imagedata:list, image, ColorWeAreLookingFor, Direction):
    PixelsList: list = []

    #we want to cut the image in half and have one case go one way and the other go the opposite way
    if imagedata[0] % 2 == 0: halfImageData = int((imagedata[0] /2))
    else : halfImageData =  int((imagedata[0] /2) + 0.5) #moves the half point to the next interger

    if Direction == "Right":
        imagedataRange = range(imagedata[0])[: halfImageData ] # we get the right half of the image list
        row = 0;  column = 0
        for Pixel in imagedataRange: # this just counts for now
            if not(Pixel == [0, 0]):  Pixel = [row, column] # if we are not at the beginning we want to start at last pixel 
            elif Pixel[1] == imagedata[1]: # if we get to the end of the row
                row = row + 1; column = 0  #row is increase to get to the next row and column is reset
            elif image[Pixel] == ColorWeAreLookingFor: # if we find the color green 
                PixelsList.append((row, column)) # if we find a pixel we are looking for we add it to the pixel List
                row = row + 1; column = 0  #row is increase to get to the next row and column is reset
            elif Pixel == imageSize: break; #we get to the end of the list
            column = column + 1 #column is increase at the end of everycycle

    elif Direction == "Left":
        imagedataRange = range(imagedata[0])[halfImageData:] # we get the right half of the image list
        for Pixel in reversed(imagedataRange): # this just counts for now
            if not(Pixel == [imagedata[0], imagedata[1]]):  Pixel = [row, column] # if we are not at the beginning we want to start at last pixel 
            elif Pixel[1] == 0: # if we get timagedataRangeo the end of the row
                row = row + 1;  imagedata[1]  #row is increase to get to the next row and column is reset
            elif image[Pixel] == ColorWeAreLookingFor: # if we find the color green 
                PixelsList.append((row, column)) # if we find a pixel we are looking for we add it to the pixel List
                row = row + 1;  imagedata[1]  #row is increase to get to the next row and column is reset
            elif Pixel == imageSize: break; #we get to the end of the list
        column = column - 1 #column is increase at the end of everycycle

def SeparatePixels(ColorWeAreLookingFor, PolyCount, GlobalPlaneDataArray:list[PlaneItem]):
    ImageDictionary = GetlistOfPixels(ColorWeAreLookingFor, GlobalPlaneDataArray)
    FullVertList = {}
    NarrowedNormalisedVertList = []

    sideCount = 0 #this keeps a count of the sides we parse through. We need this because we dont have a value that indicates the side we are currently on.
    for Sides in ImageDictionary:
        iterator = 0 # keeps count of the value we are on, so we can get the next value in the list
        VertList: list = [] #the vertList saves the verts that are out of the poly count distance. The vert list is kept here so it will be reset fro each side
        for pixels in ImageDictionary[Sides]: # left side of image
            # we need to calculate the distance between the point we are at and the point we are trying to remove.
            #if the point is too close then we will rmove the point
            #if the point if far away enough we will add that point to a list
            if math.sqrt(((Sides[iterator + 1][0] - pixels[0])^2) + ((Sides[iterator + 1][1] - pixels[1])^2)) >= PolyCount : VertList.append(pixels)
            iterator = iterator + 1 
        FullVertList[sideCount] = VertList # we save the vert list we get from the going through the pixels to the dictionary
   
    xArray = []
    yArray = []

    #since we know that there are only are only 4 sides in the FullVertList we can add all of th points into a new list
    for VertList in FullVertList:
        for verts in FullVertList[VertList]: # we separate the X and Y values so we can normalise the data sets
            xArray.append(verts[0]) 
            yArray.append(verts[1])

    xArray = NormaliseData(xArray) # normalising the arrays 
    yArray = NormaliseData(yArray)

    if xArray or yArray == False:# if any of the arrays are empty
        return False

    for count in xArray.__len__(): # we then take the separted normal data na dput them back into coordinates and add them to the array
        NarrowedNormalisedVertList.append(xArray[count], yArray[count], 1) # we add the one into the list so the list will have the Z coordinate.

    NarrowedNormalisedVertList.append(verts) # at the end og this function we will have the list of verts we want to draw to the screen
    return NarrowedNormalisedVertList   

def NormaliseData(List:list):
    if not List: return False
    else: 
        norm = (List - min(List)) / (max(List) - min(List))
        return norm

def CreateEdges(ColorWeAreLookingFor, PolyCount, GlobalPlaneDataArray:list[PlaneItem]):
    MeshStructure = {}
    VertList = SeparatePixels(ColorWeAreLookingFor, PolyCount, GlobalPlaneDataArray)
    if VertList == False: 
        return False #ends the function before any extra work is done

    MeshStructure[0] = VertList
    edgeList:list =[]
    iterator = 0

    for verts in VertList: #this will get the vertical edges for the mesh.
        if iterator >=  VertList.__len__():
            edgeList.append(VertList[0], VertList[iterator]) 
        else:
            edgeList.append(verts, VertList[iterator]) 
            iterator = iterator + 1
    MeshStructure[1] = edgeList
    # We also need to get the horizontal
    MeshStructure[2] = [] #this will hold the faces
    return MeshStructure

def DrawMeshToScreen(ColorWeAreLookingFor, PolyCount, self, GlobalPlaneDataArray:list[PlaneItem]):
    MeshStructure = CreateEdges(ColorWeAreLookingFor, PolyCount , GlobalPlaneDataArray)
    if MeshStructure == False:
        self.report({'ERROR'}, "Invalid Image") 
    else:
        # make mesh
        new_mesh = bpy.data.meshes.new('new_mesh')
        new_mesh.from_pydata(MeshStructure[0], MeshStructure[1], MeshStructure[2])
        new_mesh.update()
        # make object from mesh
        new_object = bpy.data.objects.new('Sketch_to_Mesh_mesh', new_mesh)
        # make collection
        new_collection = bpy.data.collections.new('Sketch_to_Mesh_Collection')
        bpy.context.scene.collection.children.link(new_collection)
        # add object to scene collection
        new_collection.objects.link(new_object)


