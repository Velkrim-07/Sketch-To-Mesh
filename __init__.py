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

class VIEW3D_PT_Sketch_To_Mesh_Panel(bpy.types.Panel):  
    # this contains the main layout for the Sketch to mesh program
    # right now the program will not really do anything. 
    # to link up functions with the buttons
        # first create the operator 
        # find the panel you want the funciton in(this cannot be inside the main function since everything is not inside the main panel except for the other panels)
        # use ( row.operator("(the operator you want)", text="(the name of the button)"))
    # for now all of the button will create a cube

    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"  
    bl_idname = "PT_Sketch_To_Mesh_Main_Panel"

    bl_category = "S-T-M"  # Sidebar cName
    bl_label = "Sketch-To-Mesh"  # found at the top of the Panel

    def draw(self, context): 
        layout = self.layout
        
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
        

class VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel(bpy.types.Panel):  
    bl_label = "AlignViews"
    bl_idname = "PT_AlignViews"
    bl_parent_id = "PT_Views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout


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

def register():
    bpy.types.Scene.front_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.back_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.side_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.poly_count_range = bpy.props.IntProperty(name="Poly Count", default=10, min=0, max=100)
    bpy.types.Scene.mesh_rating = bpy.props.IntProperty(name="Mesh Rating", default=10, min=0, max=100)
    bpy.types.Scene.FileName_Input = bpy.props.StringProperty(name="FileName", default="STMFile")
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    bpy.utils.register_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)


def unregister():
    del bpy.types.Scene.front_views_file_path
    del bpy.types.Scene.back_views_file_path
    del bpy.types.Scene.side_views_file_path
    del bpy.types.Scene.poly_count_range
    del bpy.types.Scene.mesh_rating
    del bpy.types.Scene.FileName_Input
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Views_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_Align_Views_Panel)
    bpy.utils.unregister_class(VIEW3D_PT_Sketch_To_Mesh_MeshSettings_Panel)


if __name__ == "__main__":
    register()