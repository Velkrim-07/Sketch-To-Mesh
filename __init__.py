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
from .ui_operations import PlaceImageIn3D, Reset_Input_Images, DataBaseLogin
from .base_ui import VIEW3D_PT_Sketch_To_Mesh_Panel, VIEW3D_PT_Sketch_To_Mesh_Views_Panel, VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel, VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel, VIEW3D_PT_Sketch_To_Mesh_Testing

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