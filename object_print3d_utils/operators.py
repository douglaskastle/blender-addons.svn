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

# <pep8-80 compliant>

# All Operator

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )

from . import mesh_helpers
from . import report


def clean_float(text):
    # strip trailing zeros: 0.000 -> 0.0
    index = text.rfind(".")
    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail
    return text

# ---------
# Mesh Info

class Print3DInfoVolume(Operator):
    """Report the volume of the active mesh"""
    bl_idname = "mesh.print3d_info_volume"
    bl_label = "Print3D Info Volume"

    def execute(self, context):
        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length
        obj = context.active_object

        bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
        volume = mesh_helpers.bmesh_calc_volume(bm)
        bm.free()

        info = []
        info.append(("Volume: %s³" % clean_float("%.4f" % volume),
                    None))
        info.append(("%s cm³" % clean_float("%.4f" % ((volume * (scale * scale * scale)) / (0.01 * 0.01 * 0.01) )),
                    None))

        report.update(*info)
        return {'FINISHED'}


class Print3DInfoArea(Operator):
    """Report the surface area of the active mesh"""
    bl_idname = "mesh.print3d_info_area"
    bl_label = "Print3D Info Area"

    def execute(self, context):
        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length
        obj = context.active_object

        bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
        area = mesh_helpers.bmesh_calc_area(bm)
        bm.free()

        info = []
        info.append(("Area: %s²" % clean_float("%.4f" % area),
                    None))
        info.append(("%s cm²" % clean_float("%.4f" % ((area * (scale * scale)) / (0.01 * 0.01))),
                    None))
        report.update(*info)
        return {'FINISHED'}


# ---------------
# Geometry Checks

def execute_check(self, context):
    obj = context.active_object

    info = []
    self.main_check(obj, info)
    report.update(*info)

    return {'FINISHED'}


class Print3DCheckSolid(Operator):
    """Check for geometry is solid (has valid inside/outside) and correct normals"""
    bl_idname = "mesh.print3d_check_solid"
    bl_label = "Print3D Check Solid"

    @staticmethod
    def main_check(obj, info):
        import array

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)

        edges_non_manifold = array.array('i', (i for i, ele in enumerate(bm.edges)
                if not ele.is_manifold))
        edges_non_contig = array.array('i', (i for i, ele in enumerate(bm.edges)
                if ele.is_manifold and (not ele.is_contiguous)))

        info.append(("Non Manifold Edge: %d" % len(edges_non_manifold),
                    (bmesh.types.BMEdge, edges_non_manifold)))

        info.append(("Bad Contig. Edges: %d" % len(edges_non_contig),
                    (bmesh.types.BMEdge, edges_non_contig)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)



class Print3DCheckIntersections(Operator):
    """Check geometry for self intersections"""
    bl_idname = "mesh.print3d_check_intersect"
    bl_label = "Print3D Check Intersections"

    @staticmethod
    def main_check(obj, info):
        faces_intersect = mesh_helpers.bmesh_check_self_intersect_object(obj)
        info.append(("Intersect Face: %d" % len(faces_intersect),
                    (bmesh.types.BMFace, faces_intersect)))

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckDegenerate(Operator):
    """Check for degenerate geometry that may not print properly """ \
    """(zero area faces, zero length edges)"""
    bl_idname = "mesh.print3d_check_degenerate"
    bl_label = "Print3D Check Degenerate"

    @staticmethod
    def main_check(obj, info):
        import array
        scene = bpy.context.scene
        print_3d = scene.print_3d
        threshold = print_3d.threshold_zero

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)

        faces_zero = array.array('i', (i for i, ele in enumerate(bm.faces) if ele.calc_area() <= threshold))
        edges_zero = array.array('i', (i for i, ele in enumerate(bm.edges) if ele.calc_length() <= threshold))

        info.append(("Zero Faces: %d" % len(faces_zero),
                    (bmesh.types.BMFace, faces_zero)))

        info.append(("Zero Edges: %d" % len(edges_zero),
                    (bmesh.types.BMEdge, edges_zero)))

        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckThick(Operator):
    """Check geometry is above the minimum thickness preference """ \
    """(relies on correct normals)"""
    bl_idname = "mesh.print3d_check_thick"
    bl_label = "Print3D Check Thickness"

    @staticmethod
    def main_check(obj, info):
        scene = bpy.context.scene
        print_3d = scene.print_3d

        faces_error = mesh_helpers.bmesh_check_thick_object(obj, print_3d.thickness_min)

        info.append(("Thin Faces: %d" % len(faces_error),
                    (bmesh.types.BMFace, faces_error)))


    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckSharp(Operator):
    """Check edges are below the sharpness preference"""
    bl_idname = "mesh.print3d_check_sharp"
    bl_label = "Print3D Check Sharp"

    @staticmethod
    def main_check(obj, info):
        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_sharp = print_3d.angle_sharp

        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=True, triangulate=False)
        bm.normal_update()

        edges_sharp = [ele.index for ele in bm.edges
                       if ele.is_manifold and ele.calc_face_angle() > angle_sharp]

        info.append(("Sharp Edge: %d" % len(edges_sharp),
                    (bmesh.types.BMEdge, edges_sharp)))
        bm.free()

    def execute(self, context):
        return execute_check(self, context)


class Print3DCheckAll(Operator):
    """Run all checks"""
    bl_idname = "mesh.print3d_check_all"
    bl_label = "Print3D Check All"

    check_cls = (
        Print3DCheckSolid,
        Print3DCheckIntersections,
        Print3DCheckDegenerate,
        Print3DCheckThick,
        Print3DCheckSharp,
        )

    def execute(self, context):
        obj = context.active_object

        info = []
        for cls in self.check_cls:
            cls.main_check(obj, info)

        report.update(*info)

        return {'FINISHED'}


class Print3DCleanIsolated(Operator):
    """Cleanup isolated vertices and edges"""
    bl_idname = "mesh.print3d_clean_isolated"
    bl_label = "Print3D Clean Isolated "
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        bm = mesh_helpers.bmesh_from_object(obj)

        info = []
        change = False

        def face_is_isolated(ele):
            for loop in ele.loops:
                loop_next = loop.link_loop_radial_next
                if loop is not loop_next:
                    return False
            return True

        def edge_is_isolated(ele):
            return ele.is_wire

        def vert_is_isolated(ele):
            return (not bool(ele.link_edges))

        # --- face
        elems_remove = [ele for ele in bm.faces if face_is_isolated(ele)]
        remove = bm.faces.remove
        for ele in elems_remove:
            remove(ele)
        change |= bool(elems_remove)
        info.append(("Faces Removed: %d" % len(elems_remove),
                    None))
        del elems_remove
        # --- edge
        elems_remove = [ele for ele in bm.edges if edge_is_isolated(ele)]
        remove = bm.edges.remove
        for ele in elems_remove:
            remove(ele)
        change |= bool(elems_remove)
        info.append(("Edge Removed: %d" % len(elems_remove),
                    None))
        del elems_remove
        # --- vert
        elems_remove = [ele for ele in bm.verts if vert_is_isolated(ele)]
        remove = bm.verts.remove
        for ele in elems_remove:
            remove(ele)
        change |= bool(elems_remove)
        info.append(("Verts Removed: %d" % len(elems_remove),
                    None))
        del elems_remove
        # ---

        report.update(*info)

        if change:
            mesh_helpers.bmesh_to_object(obj, bm)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


class Print3DCleanDistorted(Operator):
    """Tessellate distorted faces"""
    bl_idname = "mesh.print3d_clean_distorted"
    bl_label = "Print3D Clean Distorted"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        print_3d = scene.print_3d
        angle_distort = print_3d.angle_distort

        def face_is_distorted(ele):
            no = ele.normal
            for loop in ele.loops:
                if no.angle(loop.calc_normal(), 1000.0) > angle_distort:
                    return True
            return False

        obj = context.active_object
        bm = mesh_helpers.bmesh_from_object(obj)
        bm.normal_update()
        elems_triangulate = [ele for ele in bm.faces if face_is_distorted(ele)]

        # edit
        if elems_triangulate:
            bmesh.ops.triangulate(bm, faces=elems_triangulate)
            mesh_helpers.bmesh_to_object(obj, bm)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


class Print3DCleanThin(Operator):
    """Ensure minimum thickness"""
    bl_idname = "mesh.print3d_clean_thin"
    bl_label = "Print3D Clean Thin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        TODO

        return {'FINISHED'}


# -------------
# Select Report
# ... helper function for info UI

class Print3DSelectReport(Operator):
    """Select the data assosiated with this report"""
    bl_idname = "mesh.print3d_select_report"
    bl_label = "Print3D Select Report"
    bl_options = {'INTERNAL'}

    index = IntProperty()

    _type_to_mode = {
        bmesh.types.BMVert: 'VERT',
        bmesh.types.BMEdge: 'EDGE',
        bmesh.types.BMFace: 'FACE',
        }

    _type_to_attr = {
        bmesh.types.BMVert: "verts",
        bmesh.types.BMEdge: "edges",
        bmesh.types.BMFace: "faces",
        }


    def execute(self, context):
        obj = context.edit_object
        info = report.info()
        text, data = info[self.index]
        bm_type, bm_array = data

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type=self._type_to_mode[bm_type])

        bm = bmesh.from_edit_mesh(obj.data)
        elems = getattr(bm, Print3DSelectReport._type_to_attr[bm_type])[:]

        try:
            for i in bm_array:
                elems[i].select_set(True)
        except:
            # possible arrays are out of sync
            self.report({'WARNING'}, "Report is out of date, re-run check")

        # Perhaps this is annoying? but also handy!
        bpy.ops.view3d.view_selected(use_all_regions=False)

        return {'FINISHED'}


# ------
# Export

class Print3DExport(Operator):
    """Export active object using print3d settings"""
    bl_idname = "mesh.print3d_export"
    bl_label = "Print3D Export"

    def execute(self, context):
        scene = bpy.context.scene
        print_3d = scene.print_3d
        from . import export

        info = []
        ret = export.write_mesh(context, info, self.report)
        report.update(*info)

        if ret:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
