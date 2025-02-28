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
    object_split: bpy.props.BoolProperty(
        name="Separate objects",
        default=True,
        description="Objects will have different files"
    )
    
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
        obj_split = context.scene.multiobj_tool.object_split
        scale = context.scene.multiobj_tool.scale
        fwdaxis = context.scene.multiobj_tool.fwd_axis
        upaxis = context.scene.multiobj_tool.up_axis
        
        if dir == '':
            self.report({'ERROR'},"Invalid export path")
            return {'CANCELLED'}
        
        if not os.path.exists(dir):
            os.mkdir(dir)
            
        nexports = 0

        new_obj = {}
        
        for obj in objects:
            if not obj.visible_get() or obj.type != 'MESH':
                continue
            
            name = (obj.name.split(".")[0]+"_" if obj_split else "")+(obj.active_material.name if obj.active_material != None else "nomaterial")
            if name in new_obj:
                new_obj[name].append(obj)
            else:
                new_obj[name] = [obj]
        
        bpy.ops.object.select_all(action='DESELECT')
        for name,group in new_obj.items():
            for obj in group:
                obj.select_set(True)
                
            bpy.ops.wm.obj_export(filepath=dir+name+'.obj',export_materials=False,global_scale=scale,
            export_selected_objects=True,forward_axis=fwdaxis,up_axis=upaxis,path_mode='ABSOLUTE')
            
            bpy.ops.object.select_all(action='DESELECT')
            nexports += 1
        
        
        
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
        layout.separator()
        
        layout.prop(tool,"object_split")
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
