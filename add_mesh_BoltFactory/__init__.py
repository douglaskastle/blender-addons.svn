
bl_addon_info = {
    'name': 'Add Mesh: Bolt',
    'author': 'Aaron Keith',
    'version': '3.9',
    'blender': (2, 5, 3),
    'location': 'add Mesh',
    'url': 'http://sourceforge.net/projects/boltfactory/',
    'category': 'Add Mesh'}


import bpy
from add_mesh_BoltFactory.Boltfactory import add_mesh_bolt




################################################################################
##### REGISTER #####

add_mesh_bolt_button = (lambda self, context: self.layout.operator
            (add_mesh_bolt.bl_idname, text="BOLT", icon="PLUGIN"))

classes = [
add_mesh_bolt
    ]

def register():
    register = bpy.types.register
    for cls in classes:
        register(cls)

    bpy.types.INFO_MT_mesh_add.append(add_mesh_bolt_button)
    bpy.types.VIEW3D_PT_tools_objectmode.prepend(add_mesh_bolt_button) #just for testing

def unregister():
    unregister = bpy.types.unregister
    for cls in classes:
        unregister(cls)

    bpy.types.INFO_MT_mesh_add.remove(add_mesh_bolt_button)
    bpy.types.VIEW3D_PT_tools_objectmode.remove(add_mesh_bolt_button) #just for testing
    
if __name__ == "__main__":
    register()