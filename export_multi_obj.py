bl_info = {
    "name": "Multi OBJ Export",
    "blender": (4, 3, 2),
    "category": "Import-Export",
    "author": "Some1else{}"
}

import bpy
import os

axes = (('X','X',''),('Y','Y',''),('Z','Z',''))

class MultiOBJProperties(bpy.types.PropertyGroup):
    scale: bpy.props.FloatProperty(
        name="Output scale",
        default=1.0,
        description="Global scaling",
        min=0.0001,
        max=10000
    )
    
    dir: bpy.props.StringProperty(
        name="Export directory",
        description="Where all the OBJ files will be created",
        subtype='DIR_PATH'
    )
    
    fwd_axis: bpy.props.EnumProperty(
        name="Forward axis",
        items=axes,
        default='X',
        description="Desired forward axis"
    )
    
    up_axis: bpy.props.EnumProperty(
        name="Up axis",
        items=axes,
        default='Z',
        description="Desired up axis"
    )

class MultiOBJ(bpy.types.Operator):
    """Export the model as separate OBJs for each material"""
    bl_idname = "object.multi_obj"
    bl_label = "Multi OBJ Export"

    def execute(self, context):
        objects = bpy.context.scene.objects
        
        if len(objects) == 0:
            self.report({'ERROR'},"Nothing to export")
            return {'CANCELLED'}
        
        dir = bpy.path.abspath(context.scene.multiobj_tool.dir)
        scale = context.scene.multiobj_tool.scale
        fwdaxis = context.scene.multiobj_tool.fwd_axis
        upaxis = context.scene.multiobj_tool.up_axis
        
        if dir == '':
            self.report({'ERROR'},"Invalid export path")
            return {'CANCELLED'}
        
        if not os.path.exists(dir):
            os.mkdir(dir)
            
        nexports = 0
        
        mats = bpy.data.materials
        for n in range(len(mats)+1):
            mat = mats[n] if n < len(mats) else None
            matname = mats[n].name if n < len(mats) else "nomaterial"
            i = 0
            for obj in objects:
                if obj.type == 'MESH' and obj.active_material == mat:
                    obj.select_set(True)
                    i += 1
                    
            if i > 0:
                bpy.ops.wm.obj_export(filepath=dir+matname+'.obj',export_materials=False,global_scale=scale,
                export_selected_objects=True,forward_axis=fwdaxis,up_axis=upaxis,path_mode='ABSOLUTE')
                nexports += 1
            
            bpy.ops.object.select_all(action='DESELECT')
        
        
        self.report({'INFO'},"Exported "+str(nexports)+" models")
        return {'FINISHED'}
    
class SeparateModel(bpy.types.Operator):
    """Separate the model by material into submodels"""
    bl_idname = "object.separate_model"
    bl_label = "Separate by material"
    
    def execute(self,context):
        return bpy.ops.mesh.separate(type='MATERIAL')
                    
class MultiOBJTab(bpy.types.Panel):
    bl_label = "Multi OBJ Export"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        tool = context.scene.multiobj_tool
        
        row = layout.row()
        row.operator(SeparateModel.bl_idname)
        
        layout.prop(tool,"scale")
        
        row = layout.row()
        row.label(text="Forward axis")
        row.prop(tool,"fwd_axis",expand=True)
        
        row = layout.row()
        row.label(text="Up axis")
        row.prop(tool,"up_axis",expand=True)
        
        layout.prop(tool,"dir")
        
        layout.separator()
        row = layout.row()
        row.operator(MultiOBJ.bl_idname,text="Export")
        
        
classes = (MultiOBJProperties,MultiOBJ,SeparateModel,MultiOBJTab)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.multiobj_tool = bpy.props.PointerProperty(type=MultiOBJProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.multiobj_tool
    
if __name__ == "__main__":
    register()
