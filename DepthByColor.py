import math
import cv2
from .image_processing import PlaneItem
from dataclasses import dataclass

@dataclass
class EdgeData:
    Point = [] #this will hold the coordinate of the center point
    NextPoint = []#this holds the next point in the shape
    slope:float #this holds the slope of the line with the first one and the next point
    Yintercept = [] #this holds the Yintercept of the line between the first and next point
    PointToBeCheckedForColor = {}
    AllSurrondingPoints = []
    AverageColor:tuple
    ZValue:int
    LinePoints = {}

    def __init__(self, Point ,NextPoint):
        self.Point = Point
        self.NextPoint = NextPoint
        self.slope = GetSlope(Point, NextPoint) #gets the slope of each edge
        self.Yintercept = calucalateYIntercept(Point, self.slope )
        self.LinePoints = calculateLine(Point, NextPoint, self.slope, self.Yintercept)

#starts from space out pixels
def GenerateShapeEdges(FullVertList:dict, radius:int, plane:PlaneItem):
    CombinedVertList = {}
    XList = []; YList = []
    GreatestYx = 0

    #this should combine all of the sides into one list 
    for sides in FullVertList:
        for point in FullVertList[sides]:
            CombinedVertList[point[0]] = point[1]
            XList.append(point[0]); YList.append(point[1])

    MaxX = max(XList)
    GreatestX = (MaxX, CombinedVertList[MaxX])

    MinX = min(XList)
    SmallestX = (MinX, CombinedVertList[MinX])

    SmallestYx = YList[0]
    SavedX = XList[0]

    for Xvalue in CombinedVertList:
        if (max(YList) == CombinedVertList[Xvalue]): 
            GreatestYx = Xvalue #saves the X value to a varible so we can find both x and y of this point later

        if ( SmallestYx > CombinedVertList[Xvalue] ): 
            SmallestYx =  CombinedVertList[Xvalue] #saves the X value to a varible so we can find both x and y of this point 
            SavedX = Xvalue

    GreatestY = (GreatestYx, CombinedVertList[GreatestYx]) 
    SmallestY = (SavedX , CombinedVertList[SavedX])

    GreatestPointvalues = (MinX, CombinedVertList[MinX]); 
    SmallestPointvalues = ( MinX, CombinedVertList[MinX]); 
    GreatestXsmallestY = (MinX, CombinedVertList[MinX]); 
    GreatestYsmallestX = (MinX, CombinedVertList[MinX])

    for Xvalue in CombinedVertList:
        YAxis = CombinedVertList[Xvalue] #saves the y value of the list to a more readable varible
        Pointvalues = Xvalue + YAxis # we add the two values together to figure out which values is the biggest and smallest overall
        if(Pointvalues > GreatestPointvalues[0] + GreatestPointvalues[1]): GreatestPointvalues = (Xvalue, YAxis)
        if(Pointvalues < SmallestPointvalues[0] + SmallestPointvalues[1]): SmallestPointvalues = (Xvalue, YAxis)
        #we also what the hightest of the Xvalue with the Lowest of Y values and Vice versa
        if ( CalculateGreatestAxisWithsmallestAxis((Xvalue,YAxis), GreatestXsmallestY, "X")) : GreatestXsmallestY = (Xvalue, YAxis)
        if (CalculateGreatestAxisWithsmallestAxis((Xvalue,YAxis), GreatestXsmallestY, "Y")): GreatestYsmallestX = (Xvalue, YAxis)

    #GreatestY -> GreatestX ->GreatestXGreatestY ->GreatestXsmallestY -> SmallestY -> SmallestXSmallestY ->SmallestXGreatestY -> smallestX
    #we make the list in this order so they match up
    EdgeList = [GreatestY, GreatestX , GreatestPointvalues, GreatestXsmallestY, SmallestY, SmallestPointvalues, GreatestYsmallestX, SmallestX]
    
    #we then check for any repeated values
    FinishedList = []
    FinishedList.append(EdgeList[0]) #we add the first element in the array to get it started
    for CheckingEdge in EdgeList:
        AddThis = False
        RepeatValue = False
        for elements in FinishedList:
            if CheckingEdge != elements and RepeatValue == False:  AddThis = True
            else: RepeatValue = True
        if AddThis and RepeatValue ==False: FinishedList.append(CheckingEdge)
                
    return CreateEdgeData(FinishedList, radius, plane)

def CreateEdgeData(FinishedList:list, radius:int, plane:PlaneItem):
    iter = 1
    EdgeDataList = {}
    for edgepoint in FinishedList: #collects line information for the edgedata list
        #we first get the next point in the list
        #if we get to the lest place in the array that means we've come to the point right before the beginning
        if iter >= FinishedList.__len__(): NextPoint = FinishedList[0]
        else : NextPoint = FinishedList[iter] 
        EdgeDataList[edgepoint] = EdgeData(edgepoint, NextPoint)
        iter = iter + 1
    return CalculateLocationsOfAvaliblePixelsAroundPoint(EdgeDataList, radius, plane)

def CalculateLocationsOfAvaliblePixelsAroundPoint(EdgeDataList:dict, radius:int, plane:PlaneItem):
    image = cv2.imread(plane.ImagePlaneFilePath)
    imagedata = [image.shape[0], image.shape[1]]
    #we need to check for 
    #if the distance from the point is polycount(10 ) away from the radius
    #if we can remove the pixels that are not inside the shape using the angles
    #if the point we are checking is within the shape (last option)

    for points in EdgeDataList:
        # NextPointsSlope = EdgeDataList[EdgeDataList[points].NextPoint].slope
        # AreaWehave = CalculateArcArea(CalculateAnglesBetweenLines(EdgeDataList[points].slope, NextPointsSlope), radius)
        EdgeDataList[points].AllSurrondingPoints = GetAllSurroundingValues(EdgeDataList[points], radius)
        iterator  = 0
        for pointsToCheck in EdgeDataList[points].AllSurrondingPoints:
            if CalculateCollision(EdgeDataList, pointsToCheck, imagedata): #we check if the points are inside the shape
                #if the points are within the shape we add them into a dictionary (x = key, y = value) to get there color value checked
                EdgeDataList[points].PointToBeCheckedForColor[pointsToCheck[0]] = pointsToCheck[1] #the point we want check for color
            iterator = iterator + 1
    return CycleThroughEdgePointsForColor(EdgeDataList, image)

def CycleThroughEdgePointsForColor(EdgeDataList, image):
    for edges in EdgeDataList:
        EdgeDataList[edges] = GetAverageOfSurroundingValues(EdgeDataList[edges], image)
    EdgeDataList = CalculateZAxis(EdgeDataList)

    outputlist = []
    for edges in EdgeDataList:
        outputlist.append(round(EdgeDataList[edges].ZValue))
    return outputlist

def GetAverageOfSurroundingValues(EdgePoint:EdgeData, image):
    AverageColors = []
    Colorvalues = [0, 0, 0]
    for points in EdgePoint.PointToBeCheckedForColor: 
                        #Values Saved         #X              #Y
        Colorvalues = [Colorvalues[0] + int(image[points, EdgePoint.PointToBeCheckedForColor[points]][0]), 
                       Colorvalues[1] + int(image[points, EdgePoint.PointToBeCheckedForColor[points]][1]), 
                       Colorvalues[2] + int(image[points, EdgePoint.PointToBeCheckedForColor[points]][2])]
    for Colors in Colorvalues:
        AverageColors.append(Colors / EdgePoint.PointToBeCheckedForColor.__len__())
    EdgePoint.AverageColor = (AverageColors[0], AverageColors[1], AverageColors[2])
    return EdgePoint

def CalculateZAxis(EdgeDataList:dict):
    ZValuesList = []
    for points in EdgeDataList:
        NextPointsColors = EdgeDataList[EdgeDataList[points].NextPoint].AverageColor
        iterator  = 0
        AveragedColorValue = []
        for ColorsVals in EdgeDataList[points].AverageColor: AveragedColorValue.append((ColorsVals - NextPointsColors[iterator]))

        EdgeDataList[points].AverageColor = AveragedColorValue
        ZValuesList.append((round(AveragedColorValue[0]) + round(AveragedColorValue[1]) + round(AveragedColorValue[2])) / 3)

    #Normalises the Z data so the values match the values in the orginal function
    ZValuesList = NormaliseData(ZValuesList)

    #saves the Z values with there edgePoints
    iterator = 0
    for points in EdgeDataList: 
        EdgeDataList[points].ZValue = ZValuesList[iterator]
        iterator = iterator + 1
    return EdgeDataList

#this function gets all of the values surrounding a point
def GetAllSurroundingValues(EdgePoint:EdgeData, radius:int):
    SurroundingValues = []
    for Xvalues in range(radius):
        Yvalues = radius - Xvalues
        UpperRightPoint = EdgePoint.Point[0] + Xvalues, EdgePoint.Point[1] + Yvalues #gets teh values to the upper right of the point
        LowerRightPoint = EdgePoint.Point[0] + Xvalues, EdgePoint.Point[1] - Yvalues #gets teh values to the upper right of the point
        UpperLeftPoint = EdgePoint.Point[0] - Xvalues, EdgePoint.Point[1] + Yvalues #gets the values to lower left of the point
        LowerLeftPoint = EdgePoint.Point[0] - Xvalues, EdgePoint.Point[1] - Yvalues #gets the values to lower left of the point

        CurrSurroundingVals = [UpperRightPoint, LowerRightPoint, UpperLeftPoint, LowerLeftPoint]
        for CurrVals in CurrSurroundingVals:
            if IsWithinRadius(EdgePoint.Point, CurrVals, radius): #checks if the points are within the radius
                SurroundingValues.append(CurrVals) #this goes to the left of the point
    return SurroundingValues #we add all the points to the list

def CalculateCollision(EdgeDataList, pointWeCheck:list, imagedata:list): #use when we grab the colors surronding each edge
    #we only want points that are found within the shape
    XCheck = pointWeCheck[0]
    XCheckCollisonCount = 0
    ReturnBool = False

    while ( XCheckCollisonCount < 2 and XCheck <= imagedata[0]):
        for point in EdgeDataList:
            edgepoint:EdgeData = EdgeDataList[point]
            if edgepoint.LinePoints.get(XCheck) == pointWeCheck[1]: # checks if any of the points
                XCheckCollisonCount = XCheckCollisonCount + 1 # Checks how many times our point collides with the shape
                #more than two we know the point is outside of the shape
                #one we know the point is inside of the shape
                #Zero we know the point is outside the shape
        XCheck = XCheck + 1
    if XCheckCollisonCount == 1: ReturnBool = True

    return ReturnBool

def IsWithinRadius(EdgePointPoint, PointToCheck, radius):
    ReturnBool = False
    XDistance = abs((PointToCheck[0] - EdgePointPoint[0])^2) # gets the X part of the Distance formula
    YDistance = abs((PointToCheck[1] - EdgePointPoint[1])^2) # gets the Y part of the Distance formula
    if XDistance+ YDistance <= radius: ReturnBool = True
    return ReturnBool 

def GetAnglesFromMeshStructure( MeshStructure:dict):
    Angles = []
    iterator = 0
    for slopes in MeshStructure[3]:  #designed list of slopes
        if iterator >= MeshStructure[3].__len__():
            Angles.append(CalculateAnglesBetweenLines(slopes, MeshStructure[3][0]))
        else:
            Angles.append(CalculateAnglesBetweenLines(slopes, MeshStructure[3][iterator]))
            iterator = iterator + 1
    return Angles

def calculateLine(Point, NextPoint, slope, Yintercept):
    LineData = {}
    for XValue in range(NextPoint[0] - Point[0]): #we loop through the x ranges
        XValue:int = NextPoint[0] - Point[0] + XValue
        Yvalue:int = (slope * XValue) + Yintercept #we use the y = mx + c formula to find the points in the line
        LineData[round(XValue)] = round(Yvalue) #assigns the Y value to the Xkey
    return LineData
    
def CalculateArcArea(Angle, radius): 
    return (Angle / 360) * (math.pi * (radius ^ 2))

def calucalateYIntercept(Point, slope):
    return( Point[1] - (Point[0] * slope) )

def CalculateAnglesBetweenLines(slope1, slope2):
    angle = 0
    if slope1 != math.nan and slope2 == math.nan: angle = math.atan(abs(1 / slope1)) #if the first slope is undefined than we use a different formula
    elif slope2 != math.nan and slope1 == math.nan: angle = math.atan(abs(1 / slope2))#if the first slope is undefined than we use a different formula
    else: angle = math.atan(abs((slope2 - slope1) / (1 + slope1 * slope2)))#if the values we get are both good we find the angle normally
    return angle

def GetSlope(point1:list, point2:list):
    return (point2[1] - point1[1]) / (point2[0] - point1[0])

def CalculateGreatestAxisWithsmallestAxis(Point1:list, Point2:list, GreaterVal:str):
    if GreaterVal == "X":
        GreaterVal = 0
        SmallVal = 1
    else:
        GreaterVal = 1
        SmallVal = 0
    
    if Point1[GreaterVal] > Point2[GreaterVal]:
        if Point1[SmallVal] < Point2[SmallVal]: return True
        else:
            distX = Point1[GreaterVal] - Point2[GreaterVal]
            distY = Point1[SmallVal] - Point2[SmallVal]
            if distX > distY: return True
            else: return False
    else:
        if Point1[1] < Point2[1]:
            distX = Point2[0] - Point1[0]
            distY = Point1[1] - Point2[1]
            if distX > distY: return True
            else: return False
        else: return False
                
def NormaliseData(List:list):
    NewList = []
    if not List: return False
    else: 
        for element in List:  
            norm = (element - min(List)) / (max(List) - min(List))
            NewList.append(norm)
    return NewList

def GenerateEdges(VertList:list, request:str):
    MeshStructure = {}
    edgeList = []
    iterator = 1
    if request == "BlenderPoints":
        for verts in range(VertList.__len__()-1): #this will get the vertical edges for the mesh.
            if iterator >=  VertList.__len__()-1: edgeList.append((0, iterator))
            else:
                edgeList.append((verts, iterator))
                iterator = iterator + 1

    elif request == "2DPoints":
        for verts in VertList: #this will get the vertical edges for the mesh.
            if iterator >=  VertList.__len__() : edgeList.append((0, iterator))
            else:
                edgeList.append(verts)
                iterator = iterator + 1

    MeshStructure[0] = VertList
    MeshStructure[1] = edgeList

    return MeshStructure