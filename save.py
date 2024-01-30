import bpy

def main(context):
    bpy.ops.wm.save_as_mainfile(filepath="c:\Users\James Burns\Documents\TestFile.blend")

class Save(bpy.types.Operator):
    bl_idname = "object.Save"
    bl_label = "Place Image"

    def execute(self, context):
        main(context)
        return {'FINISHED'}

class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Layout Demo"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        layout.label(text="Big Button:")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.Save")
        
        #front file path
        row = layout.row()
        row.prop(context.scene, "front_views_file_path", text="Front View")

        #right file path
        row = layout.row()
        row.prop(context.scene, "right_views_file_path", text="Right View")

        #left file path
        row = layout.row()
        row.prop(context.scene, "left_views_file_path", text="Left View")

        #back file path
        row = layout.row()
        row.prop(context.scene, "back_views_file_path", text="Back View")

        #top file path
        row = layout.row()
        row.prop(context.scene, "top_views_file_path", text="Top View")

        #bottom file path
        row = layout.row()
        row.prop(context.scene, "bottom_views_file_path", text="Bottom View")


def register():
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.types.Scene.front_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.right_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.left_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.back_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.top_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")
    bpy.types.Scene.bottom_views_file_path = bpy.props.StringProperty(subtype="FILE_PATH")


def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.types.Scene.front_views_file_path
    bpy.types.Scene.right_views_file_path
    bpy.types.Scene.left_views_file_path
    bpy.types.Scene.back_views_file_path
    bpy.types.Scene.top_views_file_path
    bpy.types.Scene.bottom_views_file_path 



if __name__ == "__main__":
    register()