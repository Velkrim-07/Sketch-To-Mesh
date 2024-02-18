import bpy

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

