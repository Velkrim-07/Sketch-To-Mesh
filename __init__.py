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
from .db_operations import test_connection
from typing import Set
from bpy.types import Context

class DoImg(bpy.types.Operator):
    bl_idname = "object.do_img"
    bl_label = "Place Image"
    
    #Property that holds the filepath that will be used to insert the image
    myFilePath: bpy.props.StringProperty(subtype="FILE_PATH")

    #This is the function that inserts the image into blender
    def execute(self, context):
        file_path = self.myFilePath
                
        if file_path: # Checks if the file path is not empty
            bpy.ops.image.open(filepath=file_path) # opens the image file
            loaded_image = bpy.data.images.get(bpy.path.basename(file_path))

            if loaded_image:
                # Display the image in the Image Editor
                bpy.context.area.type = 'IMAGE_EDITOR'
                bpy.context.space_data.image = loaded_image
        
        return {'FINISHED'}
    
    #This is a function that opens a file explorer
    #THIS DOES NOT DO ANYTHING I just think its going to be useful to have later
    def invoke(self, context, event):
        # Open a file browser to select a file
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    


class Create_Alignment_Window(bpy.types.Operator):
    bl_idname = "load.open_align_image" 
    bl_label = "Align Image"
    bl_options = {'REGISTER', 'UNDO'}

    #Property that holds the filepath that will be used to insert the image
    FilePath: bpy.props.StringProperty(subtype="FILE_PATH")

    #this is where you define what you want to happen
    def execute(self, context):
        layout = self.layout
        self.FilePath = context.scene.front_views_file_path.filepath
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "FilePath")

        row = layout.row()
        if self.FilePath != FileNotFoundError:  row.operator("object.do_img", text="Align Image").myFilePath = self.FilePath

        row = layout.row()
        row.prop(context.scene, "Image_Center_X", text="Image X center", slider=True)

        row = layout.row()
        row.prop(context.scene, "Image_Center_Y", text="Image Y Center", slider=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    

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
    bl_idname = "PT_Sketch_To_Mesh_Main_Panel"

    bl_category = "S-T-M"  # Sidebar cName
    bl_label = "Sketch-To-Mesh"  # found at the top of the Panel

    def draw(self, context): 
        layout = self.layout



class StMTestConnectionOperator(bpy.types.Operator):
    bl_idname = "wm.test_connection_operator"
    bl_label = "Test Database Connection"

    def execute(self, context):
        # Call the test_connection function
        success = test_connection()
        if success:
            self.report({'INFO'}, "Connection to MongoDB successful!")
        else:
            self.report({'ERROR'}, "Failed to connect to MongoDB.")
        return {'FINISHED'}
     


class VIEW3D_PT_Sketch_To_Mesh_Views_Panel(bpy.types.Panel):  
    bl_label = "View"
    bl_idname = "PT_Views"
    bl_parent_id = "PT_Sketch_To_Mesh_Main_Panel" 
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
        

class VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel(bpy.types.Panel):  
    bl_label = "AlignViews"
    bl_idname = "PT_AlignViews"
    bl_parent_id = "PT_Views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        row.operator("load.open_align_image", text="Align Image")

       

class VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel(bpy.types.Panel):  
    bl_label = "MeshSettings"
    bl_idname = "PT_MeshSettings"
    bl_parent_id = "PT_Sketch_To_Mesh_Main_Panel"  # Set the parent panel ID
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

    bpy.types.Scene.front_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.back_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.side_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.poly_count_range = bpy.props.IntProperty(name="Poly Count", default=10, min=0, max=100)
    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_X = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.Image_Center_Y = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)

    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.FileName_Input = bpy.props.StringProperty(name="FileName", default="STMFile")
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.register_class(DoImg)
    bpy.utils.register_class(Create_Alignment_Window)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel) 
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    # ralf changes
    bpy.utils.register_class(StMTestConnectionOperator)
    
 


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
    bpy.utils.unregister_class(DoImg)
    bpy.utils.unregister_class(Create_Alignment_Window)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)
    # ralf changes
    bpy.utils.unregister_class(StMTestConnectionOperator)
  


if __name__ == "__main__":
    register()