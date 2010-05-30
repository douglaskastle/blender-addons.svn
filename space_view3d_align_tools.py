# AlingTools.py (c) 2009, 2010 Gabriel Beaudin (gabhead)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_addon_info = {
    'name': '3D View: Align Tools',
    'author': 'Gabriel Beaudin (gabhead)',
    'version': '0.1',
    'blender': (2, 5, 3),
    'location': 'Tool Shelf',
    'description': 'Align selected objects to the active object',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
           'Scripts/',
    'category': '3D View'}

import bpy

##interface
######################
class View3DPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

class AlignUi(View3DPanel):
    bl_label = "Align Tools"
    bl_context = "objectmode"
    

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj != None:
            row = layout.row()
            row.label(text="Active object is: " + obj.name, icon='OBJECT_DATA')
        
        box = layout.separator()
        
        col = layout.column()
        col.label(text="Align Location and Rotation:", icon='MANIPUL')

        
        col = layout.column(align=False)
        col.operator("object.AlignObjects",text="XYZ")
        
        col = layout.column()
        col.label(text="Align Location:", icon='MAN_TRANS')

        col = layout.column_flow(columns=5,align=True)
        col.operator("object.AlignObjectsLocationX",text="X")
        col.operator("object.AlignObjectsLocationY",text="Y")
        col.operator("object.AlignObjectsLocationZ",text="Z")
        col.operator("object.AlignObjectsLocationAll",text="All")

        col = layout.column()
        col.label(text="Align Rotation:", icon='MAN_ROT')

        col = layout.column_flow(columns=5,align=True)
        col.operator("object.AlignObjectsRotationX",text="X")
        col.operator("object.AlignObjectsRotationY",text="Y")
        col.operator("object.AlignObjectsRotationZ",text="Z")
        col.operator("object.AlignObjectsRotationAll",text="All")
        
        col = layout.column()
        col.label(text="Align Scale:", icon='MAN_SCALE')

        col = layout.column_flow(columns=5,align=True)
        col.operator("object.AlignObjectsScaleX",text="X")
        col.operator("object.AlignObjectsScaleY",text="Y")
        col.operator("object.AlignObjectsScaleZ",text="Z")
        col.operator("object.AlignObjectsScaleAll",text="All")


        
    
##Ops
##################

## Def

##Align all
def main(context):
    for i in bpy.context.selected_objects:
        i.location = bpy.context.active_object.location
        i.rotation_euler = bpy.context.active_object.rotation_euler

## Align Location

def LocAll(context):
    for i in bpy.context.selected_objects:
        i.location = bpy.context.active_object.location

def LocX(context):
    for i in bpy.context.selected_objects:
        i.location.x = bpy.context.active_object.location.x

def LocY(context):
    for i in bpy.context.selected_objects:
        i.location.y = bpy.context.active_object.location.y

def LocZ(context):
    for i in bpy.context.selected_objects:
        i.location.z = bpy.context.active_object.location.z

## Aling Rotation
def RotAll(context):
    for i in bpy.context.selected_objects:
        i.rotation_euler = bpy.context.active_object.rotation_euler

def RotX(context):
    for i in bpy.context.selected_objects:
        i.rotation_euler.x = bpy.context.active_object.rotation_euler.x

def RotY(context):
    for i in bpy.context.selected_objects:
        i.rotation_euler.y = bpy.context.active_object.rotation_euler.y

def RotZ(context):
    for i in bpy.context.selected_objects:
        i.rotation_euler.z = bpy.context.active_object.rotation_euler.z
## Aling Scale
def ScaleAll(context):
    for i in bpy.context.selected_objects:
        i.Scale = bpy.context.active_object.Scale

def ScaleX(context):
    for i in bpy.context.selected_objects:
        i.Scale.x = bpy.context.active_object.Scale.x

def ScaleY(context):
    for i in bpy.context.selected_objects:
        i.Scale.y = bpy.context.active_object.Scale.y

def ScaleZ(context):
    for i in bpy.context.selected_objects:
        i.Scale.z = bpy.context.active_object.Scale.z

## Classes

## Align All Rotation And Location
class AlignOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjects"
    bl_label = "Align Selected To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        main(context)
        return {'FINISHED'}

#######################Align Location########################
## Align LocationAll
class AlignLocationOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsLocationAll"
    bl_label = "Align Selected Location To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        LocAll(context)
        return {'FINISHED'}
## Align LocationX
class AlignLocationXOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsLocationX"
    bl_label = "Align Selected Location X To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        LocX(context)
        return {'FINISHED'}
## Align LocationY
class AlignLocationYOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsLocationY"
    bl_label = "Align Selected Location Y To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        LocY(context)
        return {'FINISHED'}
## Align LocationZ
class AlignLocationZOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsLocationZ"
    bl_label = "Align Selected Location Z To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        LocZ(context)
        return {'FINISHED'}

#######################Align Rotation########################
## Align RotationAll
class AlignRotationOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsRotationAll"
    bl_label = "Align Selected Rotation To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        RotAll(context)
        return {'FINISHED'}
## Align RotationX
class AlignRotationXOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsRotationX"
    bl_label = "Align Selected Rotation X To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        RotX(context)
        return {'FINISHED'}
## Align RotationY
class AlignRotationYOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsRotationY"
    bl_label = "Align Selected Rotation Y To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        RotY(context)
        return {'FINISHED'}
## Align RotationZ
class AlignRotationZOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsRotationZ"
    bl_label = "Align Selected Rotation Z To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        RotZ(context)
        return {'FINISHED'}
#######################Align Scale########################
## Scale All
class AlignScaleOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsScaleAll"
    bl_label = "Align Selected Scale To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        ScaleAll(context)
        return {'FINISHED'}
## Align ScaleX
class AlignScaleXOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsScaleX"
    bl_label = "Align Selected Scale X To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        ScaleX(context)
        return {'FINISHED'}
## Align ScaleY
class AlignScaleYOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsScaleY"
    bl_label = "Align Selected Scale Y To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        ScaleY(context)
        return {'FINISHED'}
## Align ScaleZ
class AlignScaleZOperator(bpy.types.Operator):
    ''''''
    bl_idname = "object.AlignObjectsScaleZ"
    bl_label = "Align Selected Scale Z To Active"

    def poll(self, context):
        return context.active_object != None

    def execute(self, context):
        ScaleZ(context)
        return {'FINISHED'}

## registring
def register():
        bpy.types.register(AlignUi)
        bpy.types.register(AlignOperator)
        bpy.types.register(AlignLocationOperator)
        bpy.types.register(AlignLocationXOperator)
        bpy.types.register(AlignLocationYOperator)
        bpy.types.register(AlignLocationZOperator)
        bpy.types.register(AlignRotationOperator)
        bpy.types.register(AlignRotationXOperator)
        bpy.types.register(AlignRotationYOperator)
        bpy.types.register(AlignRotationZOperator)
        bpy.types.register(AlignScaleOperator)
        bpy.types.register(AlignScaleXOperator)
        bpy.types.register(AlignScaleYOperator)
        bpy.types.register(AlignScaleZOperator)


def unregister():
        bpy.types.unregister(AlignUi)
        bpy.types.unregister(AlignOperator)
        bpy.types.unregister(AlignLocationOperator)
        bpy.types.unregister(AlignLocationXOperator)
        bpy.types.unregister(AlignLocationYOperator)
        bpy.types.unregister(AlignLocationZOperator)
        bpy.types.unregister(AlignRotationOperator)
        bpy.types.unregister(AlignRotationXOperator)
        bpy.types.unregister(AlignRotationYOperator)
        bpy.types.unregister(AlignRotationZOperator)
        bpy.types.unregister(AlignScaleOperator)
        bpy.types.unregister(AlignScaleXOperator)
        bpy.types.unregister(AlignScaleYOperator)
        bpy.types.unregister(AlignScaleZOperator)

if __name__ == "__main__":
    register()