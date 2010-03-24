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
    "name": "Index Visualiser",
    "author": "Bartius Crouch",
    "version": "2.2 2010/03/16",
    "blender": "2.5.2",
    "category": "3D View",
    "location": "View3D > properties panel > display tab",
    "url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Index_Visualiser",
    "doc": """\
Display the indices of vertices, edges and faces in the 3d-view.

How to use:
- Select a mesh and go into editmode
- Display the properties panel (N-key)
- Go to the Display tab (4th tab), it helps to fold the tabs above it
- Press the 'Visualise indices button'

"""}


import bgl, blf, bpy, Mathutils

# calculate locations and store them as ID property in the mesh
def calc_callback(self, context):
    # polling
    if context.mode != 'EDIT_MESH':
        return
    
    # get screen information
    mid_x = context.region.width/2.0
    mid_y = context.region.height/2.0
    width = context.region.width
    height = context.region.height
    
    # get matrices
    view_mat = context.space_data.region_3d.perspective_matrix
    ob_mat = context.active_object.matrix
    total_mat = view_mat*ob_mat
    
    # calculate location info
    texts = []
    locs = []
    me = context.active_object.data
    # uncomment 2 lines below, to enable live updating of the selection
    #bpy.ops.object.editmode_toggle()
    #bpy.ops.object.editmode_toggle()
    if bpy.context.scene.display_vert_index:
        for v in me.verts:
            if v.selected or not bpy.context.scene.display_sel_only:
                locs.append([1.0, 1.0, 1.0, v.index, Mathutils.Vector(v.co[:][0], v.co[:][1], v.co[:][2], 1.0)])
    if bpy.context.scene.display_edge_index:
        for ed in me.edges:
            if ed.selected or not bpy.context.scene.display_sel_only:
                v1, v2 = ed.verts
                v1 = Mathutils.Vector(me.verts[v1].co[:])
                v2 = Mathutils.Vector(me.verts[v2].co[:])
                loc = v1 + ((v2-v1)/2.0)
                locs.append([1.0, 1.0, 0.0, ed.index, Mathutils.Vector(loc[0],loc[1],loc[2],1.0)])
    if bpy.context.scene.display_face_index:
        for f in me.faces:
            if f.selected or not bpy.context.scene.display_sel_only:
                locs.append([1.0, 0.0, 0.5, f.index, Mathutils.Vector(f.center[0], f.center[1], f.center[2], 1.0)])
                
    for loc in locs:
        vec = total_mat*loc[4] # order is important
        vec = Mathutils.Vector(vec[0]/vec[3],vec[1]/vec[3],vec[2]/vec[3]) # dehomogenise
        x = int(mid_x + vec[0]*width/2.0)
        y = int(mid_y + vec[1]*height/2.0)
        texts+=[loc[0], loc[1], loc[2], loc[3], x, y, 0]

    # store as ID property in mesh
    context.active_object.data['IndexVisualiser'] = texts

# draw in 3d-view
def draw_callback(self, context):
    # polling
    if context.mode != 'EDIT_MESH':
        return
    # retrieving ID property data
    try:
        texts = context.active_object.data['IndexVisualiser']
    except:
        return
    if not texts:
        return
    
    # draw
    blf.size(13, 72)
    for i in range(0,len(texts),7):
        bgl.glColor3f(texts[i], texts[i+1], texts[i+2])
        blf.position(texts[i+4], texts[i+5], texts[i+6])
        blf.draw(str(int(texts[i+3])))

# operator
class IndexVisualiser(bpy.types.Operator):
    bl_idname = "view3d.index_visualiser"
    bl_label = "Index Visualiser"
    bl_description = "Toggle the visualisation of indices"
    
    def poll(self, context):
        return context.mode=='EDIT_MESH'
    
    def modal(self, context, event):
        context.area.tag_redraw()

        # removal of callbacks when operator is called again
        if context.scene.display_indices == -1:
            context.region.callback_remove(self.handle1)
            context.region.callback_remove(self.handle2)
            context.scene.display_indices = 0
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.scene.display_indices == 0:
                # operator is called for the first time, start everything
                context.scene.display_indices = 1
                context.manager.add_modal_handler(self)
                self.handle1 = context.region.callback_add(calc_callback, (self, context), 'POST_VIEW')
                self.handle2 = context.region.callback_add(draw_callback, (self, context), 'POST_PIXEL')
                return {'RUNNING_MODAL'}
            else:
                # operator is called again, stop displaying
                context.scene.display_indices = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, can't run operator")
            return {'CANCELLED'}

# defining the panel
def menu_func(self, context):
    col = self.layout.column(align=True)
    col.operator(IndexVisualiser.bl_idname, text="Visualise indices")
    row = col.row(align=True)
    row.active = (context.mode=='EDIT_MESH' and context.scene.display_indices==1)
    row.prop(context.scene, 'display_vert_index', toggle=True)
    row.prop(context.scene, 'display_edge_index', toggle=True)
    row.prop(context.scene, 'display_face_index', toggle=True)
    row = col.row(align=True)
    row.active = (context.mode=='EDIT_MESH' and context.scene.display_indices==1)
    row.prop(context.scene, 'display_sel_only')
    self.layout.separator()

def register():
    bpy.types.Scene.IntProperty(attr="display_indices", default=0)
    bpy.context.scene.display_indices = 0
    bpy.types.Scene.BoolProperty(attr="display_sel_only", name="Selected only", description="Only display indices of selected vertices/edges/faces", default=True)
    bpy.types.Scene.BoolProperty(attr="display_vert_index", name="Vertices", description="Display vertex indices", default=True)
    bpy.types.Scene.BoolProperty(attr="display_edge_index", name="Edges", description="Display edge indices")
    bpy.types.Scene.BoolProperty(attr="display_face_index", name="Faces", description="Display face indices")
    bpy.types.register(IndexVisualiser)
    bpy.types.VIEW3D_PT_3dview_display.prepend(menu_func)

def unregister():
    bpy.types.unregister(IndexVisualiser)
    bpy.types.VIEW3D_PT_3dview_display.remove(menu_func)

if __name__ == "__main__":
    register()