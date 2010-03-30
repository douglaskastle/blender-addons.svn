#3d_cursor_menu.py (c) 2010 Jonathan Smith (JayDez)
#Original Script by: Mariano Hidalgo (uselessdreamer)
#contributed to by: Crouch, sim88, sam, meta-androcto
#
#Tested with r27779
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
    'name': '3d View: Dynamic Menu',
    'author': 'JayDez, sim88, meta-androcto',
    'version': '2.4',
    'blender': (2, 5, 3),
    'location': 'View3D > Mouse > Menu ',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/3d_Cursor_Menu',
    'category': '3D View'}
"Add Extended 3D Cursor Menu (Right click in View3D)"

"""
Name: '3D Cursor Menu'
Blender: 250
"""

__author__ = ["JayDez, sim88, meta-androcto, sam"]
__version__ = '2.5'
__url__ = [""]
__bpydoc__= """
3D Cursor Menu
This adds a 3D Cursor Menu in the 3DView.
May be merged with 3D Dynamic Menu script in the future...

Usage:
* Right click in an empty space in the 3D View(that means nothing
selectable is there). If your select mouse is set to left then left
click in the 3D View.

* Choose your function from the menu.

Version history:
v2.5 - (meta-androcto) - rewrite. Added editmode menu.
v2.4 - (JayDez) - Added bpydoc as well as changing to click only
    (instead of double click).
v2.3 - (JayDez) - Added revert_pivot() which allows you to change
    pivot point back to normal(which right now is median point).
v2.2 - (Crouch) - Fix in register function, fix with random quotation
    mark which crashed script.
v2.1 - (Crouch) - added unregister() and set pivot point to cursor.
v2.0 - (JayDez) - 2.5 script (initial revision)
v1.0 - Original 2.49 script

"""
import bpy
from bpy import *

class pivot_cursor(bpy.types.Operator):
    bl_idname = "view3d.pivot_cursor"
    bl_label = "Cursor as Pivot Point"
    
    def poll(self, context):
        return bpy.context.space_data.pivot_point != 'CURSOR'
    
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'CURSOR'
        return {'FINISHED'}
    
class revert_pivot(bpy.types.Operator):
    bl_idname = "view3d.revert_pivot"
    bl_label = "Reverts Pivot Point to median"

    def poll(self, context):
        return bpy.context.space_data.pivot_point != 'MEDIAN_POINT'
    
    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        #change this to 'BOUDNING_BOX_CENTER' if needed...
        return{'FINISHED'}

class VIEW3D_MT_3D_Cursor_Menu(bpy.types.Menu):
    bl_label = "Dynamic Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        ob = context
        if ob.mode == 'OBJECT':

            layout.menu("INFO_MT_mesh_add", text="Add Mesh", icon='OUTLINER_OB_MESH')
            layout.separator()
            layout.operator("transform.translate", icon='MAN_TRANS')
            layout.operator("transform.rotate", icon='MAN_ROT')
            layout.operator("transform.resize", text="Scale", icon='MAN_SCALE')
            layout.separator()
            layout.operator_menu_enum("object.lamp_add", "type", icon="OUTLINER_OB_LAMP")
            layout.operator_menu_enum("object.curve_add", "type", icon='OUTLINER_OB_CURVE')
            layout.menu("INFO_MT_armature_add", text="Add Armature", icon='OUTLINER_OB_ARMATURE')
            layout.operator("object.add", text="Add Empty", icon='OUTLINER_OB_EMPTY')
            layout.separator()
            layout.menu("VIEW3D_MT_object_group", icon='GROUP')
            layout.operator("object.modifier_add", icon='MODIFIER')
            layout.separator()
            layout.operator("object.parent_set", icon= 'ROTACTIVE')
            layout.separator()
            layout.operator("object.delete", text="Delete Object", icon='CANCEL')

        elif ob.mode == 'EDIT_MESH':

#create block
            bl_label = "Create"
            layout.separator()
            layout.menu("INFO_MT_mesh_add", text="Add Mesh", icon='OUTLINER_OB_MESH')
#transform block
            layout.operator("transform.translate", icon='MAN_TRANS')
            layout.operator("transform.rotate", icon='MAN_ROT')
            layout.operator("transform.resize", text="Scale", icon='MAN_SCALE')
            layout.separator()
#select block
            layout.menu("VIEW3D_MT_edit_mesh_selection_mode", icon='EDIT')
            layout.menu("VIEW3D_MT_selectS", icon='OBJECT_DATAMODE')
#edit block
            layout.menu("VIEW3D_MT_edit_mesh_vertices", icon='VERTEXSEL')
            layout.menu("VIEW3D_MT_edit_mesh_edges", icon='EDGESEL')
            layout.menu("VIEW3D_MT_edit_mesh_faces", icon='FACESEL')
            layout.operator("mesh.loopcut_slide",text="Loopcut", icon= 'EDIT_VEC')
#tools block
            layout.menu("VIEW3D_MT_edit_mesh_specials", icon='MODIFIER')
            layout.menu("VIEW3D_MT_uv_map", icon='MOD_UVPROJECT')
            layout.operator("mesh.delete", icon='CANCEL')
#History block
        layout.menu("VIEW3D_MT_undoS", icon='ARROW_LEFTRIGHT')
        layout.separator()
        layout.operator("transform.snap_type", text="Snap Tools", icon= 'SNAP_ON')
        layout.menu("VIEW3D_MT_curs", icon= 'CURSOR')
        layout.separator()
        layout.operator("object.editmode_toggle", icon='EDITMODE_HLT')

class VIEW3D_MT_selectS(bpy.types.Menu):
    bl_label = "Selections"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.select_all")
        layout.operator("mesh.select_inverse")
        layout.operator("mesh.select_more")
        layout.operator("mesh.select_less")
        layout.operator("view3d.select_circle")
        layout.operator("view3d.select_border")


class VIEW3D_MT_undoS(bpy.types.Menu):
    bl_label = "Undo/Redo"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("ed.undo", icon='TRIA_LEFT')
        layout.operator("ed.redo", icon='TRIA_RIGHT')


class VIEW3D_MT_curs(bpy.types.Menu):
    bl_label = "Cursor Menu"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("view3d.snap_cursor_to_center", text="Snap Cursor to Center")
        layout.operator("view3d.snap_cursor_to_grid", text="Snap Cursor to Grid")
        layout.operator("view3d.snap_cursor_to_selected", text="Snap Cursor to Selected")
        layout.operator("view3d.snap_selected_to_cursor", text="Snap Selected to Cursor")
        layout.separator()
        layout.operator("view3d.pivot_cursor", text="Set Cursor as Pivot Point")
        layout.operator("view3d.revert_pivot", text="Revert Pivot Point")


class VIEW3D_MT_editM_Edge(bpy.types.Menu):
    bl_label = "Edges"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.separator()
        layout.operator("mesh.mark_seam")
        layout.operator("mesh.mark_seam", text="Clear Seam").clear = True
        layout.separator()
        layout.operator("mesh.mark_sharp")
        layout.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
        layout.operator("mesh.extrude_move_along_normals",text="Extrude")
        layout.separator()
        layout.operator("mesh.edge_rotate", text="Rotate Edge CW").direction = 'CW'
        layout.operator("mesh.edge_rotate", text="Rotate Edge CCW").direction = 'CCW'
        layout.separator()
        layout.operator("TFM_OT_edge_slide", text="Edge Slide")
        layout.operator("mesh.loop_multi_select", text="Edge Loop")
        layout.operator("mesh.loop_multi_select", text="Edge Ring").ring = True
        layout.operator("mesh.loop_to_region")
        layout.operator("mesh.region_to_loop")

def register():
    bpy.types.register(VIEW3D_MT_3D_Cursor_Menu)
    bpy.types.register(pivot_cursor)
    bpy.types.register(revert_pivot)
    bpy.types.register(VIEW3D_MT_curs)
    bpy.types.register(VIEW3D_MT_editM_Edge)
    bpy.types.register(VIEW3D_MT_selectS)
    bpy.types.register(VIEW3D_MT_undoS)
    km = bpy.context.manager.active_keyconfig.keymaps['3D View']
    kmi = km.add_item('wm.call_menu', 'SELECTMOUSE', 'CLICK')
    kmi.properties.name = "VIEW3D_MT_3D_Cursor_Menu"

def unregister():
    bpy.types.unregister(VIEW3D_MT_3D_Cursor_Menu)
    bpy.types.unregister(pivot_cursor)
    bpy.types.unregister(revert_pivot)
    bpy.types.unregister(VIEW3D_MT_curs)
    bpy.types.unregister(VIEW3D_MT_editM_Edge)
    bpy.types.unregister(VIEW3D_MT_selectS)
    bpy.types.unregister(VIEW3D_MT_undoS)
    km = bpy.context.manager.active_keyconfig.keymaps['3D View']
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "VIEW3D_MT_3D_Cursor_Menu":
                km.remove_item(kmi)
                break

if __name__ == "__main__":
    register()