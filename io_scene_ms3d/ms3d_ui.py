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

# <pep8 compliant>

###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------


# ##### BEGIN COPYRIGHT BLOCK #####
#
# initial script copyright (c)2011,2012 Alexander Nussbaumer
#
# ##### END COPYRIGHT BLOCK #####


#import python stuff
from random import (
        randrange,
        )

# To support reload properly, try to access a package var,
# if it's there, reload everything
if ('bpy' in locals()):
    import imp
    if 'io_scene_ms3d.ms3d_strings' in locals():
        imp.reload(io_scene_ms3d.ms3d_strings)
    if 'io_scene_ms3d.ms3d_spec' in locals():
        imp.reload(io_scene_ms3d.ms3d_spec)
    if 'io_scene_ms3d.ms3d_utils' in locals():
        imp.reload(io_scene_ms3d.ms3d_utils)
    #if 'io_scene_ms3d.ms3d_import' in locals():
    #    imp.reload(io_scene_ms3d.ms3d_import)
    #if 'io_scene_ms3d.ms3d_export' in locals():
    #    imp.reload(io_scene_ms3d.ms3d_export)
else:
    from io_scene_ms3d.ms3d_strings import (
            ms3d_str,
            )
    from io_scene_ms3d.ms3d_spec import (
            MS3D_FLAG_TEXTURE_COMBINE_ALPHA,
            MS3D_FLAG_TEXTURE_HAS_ALPHA,
            MS3D_FLAG_TEXTURE_SPHERE_MAP,
            MS3D_MODE_TRANSPARENCY_SIMPLE,
            MS3D_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES,
            MS3D_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF,
            MAX_MATERIAL_SHININESS,
            MS3D_FLAG_NONE,
            MS3D_FLAG_SELECTED,
            MS3D_FLAG_HIDDEN,
            MS3D_FLAG_SELECTED2,
            MS3D_FLAG_DIRTY,
            MS3D_FLAG_ISKEY,
            MS3D_FLAG_NEWLYCREATED,
            MS3D_FLAG_MARKED,
            DEFAULT_VERTEX_BONE_ID,
            DEFAULT_TRIANGLE_SMOOTHING_GROUP,
            DEFAULT_TRIANGLE_GROUP,
            DEFAULT_MATERIAL_MODE,
            DEFAULT_GROUP_MATERIAL_INDEX,
            DEFAULT_MODEL_JOINT_SIZE,
            DEFAULT_MODEL_TRANSPARENCY_MODE,
            DEFAULT_MODEL_ANIMATION_FPS,
            MAX_MATERIAL_SHININESS,
            DEFAULT_FLAGS,
            )
    from io_scene_ms3d.ms3d_utils import (
            enable_edit_mode,
            )
    #from io_scene_ms3d.ms3d_import import ( Ms3dImporter, )
    #from io_scene_ms3d.ms3d_export import ( Ms3dExporter, )


#import blender stuff
from bmesh import (
        from_edit_mesh,
        )
from bpy.utils import (
        register_class,
        unregister_class,
        )
from bpy_extras.io_utils import (
        ExportHelper,
        ImportHelper,
        )
from bpy.props import (
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        StringProperty,
        PointerProperty,
        )
from bpy.types import (
        Operator,
        PropertyGroup,
        Panel,
        Armature,
        Bone,
        Mesh,
        Material,
        Action,
        Group,
        )
from bpy.app import (
        debug,
        )

_VERBOSE_DEFAULT = debug


###############################################################################
UI_FLAG_TEXTURE_COMBINE_ALPHA = 'COMBINE_ALPHA'
UI_FLAG_TEXTURE_HAS_ALPHA = 'HAS_ALPHA'
UI_FLAG_TEXTURE_SPHERE_MAP = 'SPHERE_MAP'

def ms3d_texture_mode_to_ui(ms3d_value):
    ui_value = set()
    if (ms3d_value & MS3D_FLAG_TEXTURE_COMBINE_ALPHA) == MS3D_FLAG_TEXTURE_COMBINE_ALPHA:
        ui_value.add(UI_FLAG_TEXTURE_COMBINE_ALPHA)
    if (ms3d_value & MS3D_FLAG_TEXTURE_HAS_ALPHA) == MS3D_FLAG_TEXTURE_HAS_ALPHA:
        ui_value.add(UI_FLAG_TEXTURE_HAS_ALPHA)
    if (ms3d_value & MS3D_FLAG_TEXTURE_SPHERE_MAP) == MS3D_FLAG_TEXTURE_SPHERE_MAP:
        ui_value.add(UI_FLAG_TEXTURE_SPHERE_MAP)
    return ui_value

def ui_texture_mode_to_ms3d(ui_value):
    ms3d_value = MS3D_FLAG_TEXTURE_NONE

    if UI_FLAG_TEXTURE_COMBINE_ALPHA in ui_value:
        ms3d_value |= MS3D_FLAG_TEXTURE_COMBINE_ALPHA
    if UI_FLAG_TEXTURE_HAS_ALPHA in ui_value:
        ms3d_value |= MS3D_FLAG_TEXTURE_HAS_ALPHA
    if UI_FLAG_TEXTURE_SPHERE_MAP in ui_value:
        ms3d_value |= MS3D_FLAG_TEXTURE_SPHERE_MAP
    return ms3d_value


UI_MODE_TRANSPARENCY_SIMPLE = 'SIMPLE'
UI_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF = 'DEPTH_BUFFERED_WITH_ALPHA_REF'
UI_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES = 'DEPTH_SORTED_TRIANGLES'

def ms3d_transparency_mode_to_ui(ms3d_value):
    if(ms3d_value == MS3D_MODE_TRANSPARENCY_SIMPLE):
        return UI_MODE_TRANSPARENCY_SIMPLE
    elif(ms3d_value == MS3D_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF):
        return UI_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF
    elif(ms3d_value == MS3D_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES):
        return UI_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES
    return None

def ui_transparency_mode_to_ms3d(ui_value):
    if(ui_value == UI_MODE_TRANSPARENCY_SIMPLE):
        return MS3D_MODE_TRANSPARENCY_SIMPLE
    elif(ui_value == UI_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF):
        return MS3D_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF
    elif(ui_value == UI_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES):
        return MS3D_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES
    return None


UI_FLAG_NONE = 'NONE'
UI_FLAG_SELECTED = 'SELECTED'
UI_FLAG_HIDDEN = 'HIDDEN'
UI_FLAG_SELECTED2 = 'SELECTED2'
UI_FLAG_DIRTY = 'DIRTY'
UI_FLAG_ISKEY = 'ISKEY'
UI_FLAG_NEWLYCREATED = 'NEWLYCREATED'
UI_FLAG_MARKED = 'MARKED'

def ms3d_flags_to_ui(ms3d_value):
    ui_value = set()
    if (ms3d_value & MS3D_FLAG_SELECTED) == MS3D_FLAG_SELECTED:
        ui_value.add(UI_FLAG_SELECTED)
    if (ms3d_value & MS3D_FLAG_HIDDEN) == MS3D_FLAG_HIDDEN:
        ui_value.add(UI_FLAG_HIDDEN)
    if (ms3d_value & MS3D_FLAG_SELECTED2) == MS3D_FLAG_SELECTED2:
        ui_value.add(UI_FLAG_SELECTED2)
    if (ms3d_value & MS3D_FLAG_DIRTY) == MS3D_FLAG_DIRTY:
        ui_value.add(UI_FLAG_DIRTY)
    if (ms3d_value & MS3D_FLAG_ISKEY) == MS3D_FLAG_ISKEY:
        ui_value.add(UI_FLAG_ISKEY)
    if (ms3d_value & MS3D_FLAG_NEWLYCREATED) == MS3D_FLAG_NEWLYCREATED:
        ui_value.add(UI_FLAG_NEWLYCREATED)
    if (ms3d_value & MS3D_FLAG_MARKED) == MS3D_FLAG_MARKED:
        ui_value.add(UI_FLAG_MARKED)
    return ui_value

def ui_flags_to_ms3d(ui_value):
    ms3d_value = MS3D_FLAG_NONE
    if UI_FLAG_SELECTED in ui_value:
        ms3d_value |= MS3D_FLAG_SELECTED
    if UI_FLAG_HIDDEN in ui_value:
        ms3d_value |= MS3D_FLAG_HIDDEN
    if UI_FLAG_SELECTED2 in ui_value:
        ms3d_value |= MS3D_FLAG_SELECTED2
    if UI_FLAG_DIRTY in ui_value:
        ms3d_value |= MS3D_FLAG_DIRTY
    if UI_FLAG_ISKEY in ui_value:
        ms3d_value |= MS3D_FLAG_ISKEY
    if UI_FLAG_NEWLYCREATED in ui_value:
        ms3d_value |= MS3D_FLAG_NEWLYCREATED
    if UI_FLAG_MARKED in ui_value:
        ms3d_value |= MS3D_FLAG_MARKED
    return ms3d_value

###############################################################################
LABEL_ICON_OPTIONS = 'LAMP'
LABEL_ICON_OBJECT = 'WORLD'
LABEL_ICON_PROCESSING = 'OBJECT_DATAMODE'
LABEL_ICON_ANIMATION = 'RENDER_ANIMATION'


###############################################################################
PROP_DEFAULT_VERBOSE = _VERBOSE_DEFAULT


###############################################################################
PROP_ITEM_COORDINATESYSTEM_1_BY_1 = '0'
PROP_ITEM_COORDINATESYSTEM_IMP = '1'
PROP_ITEM_COORDINATESYSTEM_EXP = '2'
PROP_DEFAULT_COORDINATESYSTEM_IMP = PROP_ITEM_COORDINATESYSTEM_IMP
PROP_DEFAULT_COORDINATESYSTEM_EXP = PROP_ITEM_COORDINATESYSTEM_EXP


###############################################################################
PROP_DEFAULT_SCALE = 1.0
PROP_MIN_SCALE = 0.001
PROP_MAX_SCALE = 1000.0
PROP_SMIN_SCALE = 0.01
PROP_SMAX_SCALE = 100.0


###############################################################################
PROP_DEFAULT_UNIT_MM = True


###############################################################################
PROP_DEFAULT_SELECTED = False


###############################################################################
PROP_ITEM_OBJECT_ANIMATION = 'ANIMATION'
PROP_ITEM_OBJECT_GROUP = 'GROUP'
PROP_ITEM_OBJECT_JOINT = 'JOINT'
PROP_ITEM_OBJECT_MATERIAL = 'MATERIAL'
PROP_ITEM_OBJECT_MESH = 'MESH'
PROP_ITEM_OBJECT_SMOOTHGROUPS = 'SMOOTHGROUPS'
###############################################################################
PROP_DEFAULT_OBJECTS_IMP = {
        #PROP_ITEM_OBJECT_MESH,
        PROP_ITEM_OBJECT_MATERIAL,
        PROP_ITEM_OBJECT_JOINT,
        PROP_ITEM_OBJECT_SMOOTHGROUPS,
        PROP_ITEM_OBJECT_GROUP,
        }


###############################################################################
PROP_DEFAULT_OBJECTS_EXP = {
        #PROP_ITEM_OBJECT_MESH,
        PROP_ITEM_OBJECT_MATERIAL,
        }


###############################################################################
PROP_DEFAULT_ANIMATION = False


###############################################################################
class Ms3dImportOperator(Operator, ImportHelper):
    """ Load a MilkShape3D MS3D File """
    bl_idname = 'io_scene_ms3d.import'
    bl_label = ms3d_str['BL_LABEL_IMPORTER']
    bl_description = ms3d_str['BL_DESCRIPTION_IMPORTER']
    bl_options = {'PRESET', }
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    @staticmethod
    def menu_func(cls, context):
        cls.layout.operator(
                Ms3dImportOperator.bl_idname,
                text=ms3d_str['TEXT_OPERATOR'],
                )

    filename_ext = ms3d_str['FILE_EXT']

    filter_glob = StringProperty(
            default=ms3d_str['FILE_FILTER'],
            options={'HIDDEN', 'SKIP_SAVE', }
            )

    filepath = StringProperty(
            subtype='FILE_PATH',
            options={'HIDDEN', 'SKIP_SAVE', }
            )

    prop_verbose = BoolProperty(
            name=ms3d_str['PROP_NAME_VERBOSE'],
            description=ms3d_str['PROP_DESC_VERBOSE'],
            default=PROP_DEFAULT_VERBOSE,
            )

    prop_coordinate_system = EnumProperty(
            name=ms3d_str['PROP_NAME_COORDINATESYSTEM'],
            description=ms3d_str['PROP_DESC_COORDINATESYSTEM'],
            items=( (PROP_ITEM_COORDINATESYSTEM_1_BY_1,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_1_BY_1_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_1_BY_1_2']),
                    (PROP_ITEM_COORDINATESYSTEM_IMP,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_IMP_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_IMP_2']),
                    (PROP_ITEM_COORDINATESYSTEM_EXP,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_EXP_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_EXP_2']),
                    ),
            default=PROP_DEFAULT_COORDINATESYSTEM_IMP,
            )

    prop_scale = FloatProperty(
            name=ms3d_str['PROP_NAME_SCALE'],
            description=ms3d_str['PROP_DESC_SCALE'],
            default=PROP_DEFAULT_SCALE,
            min=PROP_MIN_SCALE,
            max=PROP_MAX_SCALE,
            soft_min=PROP_SMIN_SCALE,
            soft_max=PROP_SMAX_SCALE,
            )

    prop_unit_mm = BoolProperty(
            name=ms3d_str['PROP_NAME_UNIT_MM'],
            description=ms3d_str['PROP_DESC_UNIT_MM'],
            default=PROP_DEFAULT_UNIT_MM,
            )

    prop_animation = BoolProperty(
            name=ms3d_str['PROP_NAME_ANIMATION'],
            description=ms3d_str['PROP_DESC_ANIMATION'],
            default=PROP_DEFAULT_ANIMATION,
            )

    @property
    def handle_animation(self):
        return (PROP_ITEM_OBJECT_ANIMATION in self.prop_objects)

    @property
    def handle_materials(self):
        return (PROP_ITEM_OBJECT_MATERIAL in self.prop_objects)

    @property
    def handle_joints(self):
        return (PROP_ITEM_OBJECT_JOINT in self.prop_objects)

    @property
    def handle_smoothing_groups(self):
        return (PROP_ITEM_OBJECT_SMOOTHGROUPS in self.prop_objects)

    @property
    def handle_groups(self):
        return (PROP_ITEM_OBJECT_GROUP in self.prop_objects)


    @property
    def is_coordinate_system_1by1(self):
        return (PROP_ITEM_COORDINATESYSTEM_1_BY_1 in self.prop_coordinate_system)

    @property
    def is_coordinate_system_import(self):
        return (PROP_ITEM_COORDINATESYSTEM_IMP in self.prop_coordinate_system)

    @property
    def is_coordinate_system_export(self):
        return (PROP_ITEM_COORDINATESYSTEM_EXP in self.prop_coordinate_system)


    # draw the option panel
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_OPTIONS'], icon=LABEL_ICON_OPTIONS)
        box.prop(self, 'prop_verbose', icon='SPEAKER')

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_OBJECT'], icon=LABEL_ICON_OBJECT)
        box.prop(self, 'prop_unit_mm', icon='SCENE_DATA', expand=True)
        box.prop(self, 'prop_coordinate_system', icon='WORLD_DATA', expand=True)
        box.prop(self, 'prop_scale', icon='MESH_DATA')

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_ANIMATION'], icon=LABEL_ICON_ANIMATION)
        box.prop(self, 'prop_animation')
        if (self.prop_animation):
            box.label(ms3d_str['REMARKS_2'], icon='ERROR')

    # entrypoint for MS3D -> blender
    def execute(self, blender_context):
        """ start executing """
        from io_scene_ms3d.ms3d_import import (Ms3dImporter, )
        return Ms3dImporter(self).read(blender_context)

    def invoke(self, blender_context, event):
        blender_context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL', }


class Ms3dExportOperator(Operator, ExportHelper):
    """Save a MilkShape3D MS3D File"""
    bl_idname = 'io_scene_ms3d.export'
    bl_label = ms3d_str['BL_LABEL_EXPORTER']
    bl_description = ms3d_str['BL_DESCRIPTION_EXPORTER']
    bl_options = {'PRESET', }
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    def menu_func(cls, context):
        cls.layout.operator(
                Ms3dExportOperator.bl_idname,
                text=ms3d_str['TEXT_OPERATOR']
                )

    filename_ext = ms3d_str['FILE_EXT']

    filter_glob = StringProperty(
            default=ms3d_str['FILE_FILTER'],
            options={'HIDDEN', 'SKIP_SAVE', }
            )

    filepath = StringProperty(
            subtype='FILE_PATH',
            options={'HIDDEN', 'SKIP_SAVE', }
            )

    prop_verbose = BoolProperty(
            name=ms3d_str['PROP_NAME_VERBOSE'],
            description=ms3d_str['PROP_DESC_VERBOSE'],
            default=PROP_DEFAULT_VERBOSE,
            )

    prop_coordinate_system = EnumProperty(
            name=ms3d_str['PROP_NAME_COORDINATESYSTEM'],
            description=ms3d_str['PROP_DESC_COORDINATESYSTEM'],
            items=( (PROP_ITEM_COORDINATESYSTEM_1_BY_1,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_1_BY_1_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_1_BY_1_2']),
                    (PROP_ITEM_COORDINATESYSTEM_IMP,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_IMP_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_IMP_2']),
                    (PROP_ITEM_COORDINATESYSTEM_EXP,
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_EXP_1'],
                            ms3d_str['PROP_ITEM_COORDINATESYSTEM_EXP_2']),
                    ),
            default=PROP_DEFAULT_COORDINATESYSTEM_EXP,
            )

    prop_scale = FloatProperty(
            name=ms3d_str['PROP_NAME_SCALE'],
            description=ms3d_str['PROP_DESC_SCALE'],
            default=1.0 / PROP_DEFAULT_SCALE,
            min=PROP_MIN_SCALE,
            max=PROP_MAX_SCALE,
            soft_min=PROP_SMIN_SCALE,
            soft_max=PROP_SMAX_SCALE,
            )

    prop_objects = EnumProperty(
            name=ms3d_str['PROP_NAME_OBJECTS_EXP'],
            description=ms3d_str['PROP_DESC_OBJECTS_EXP'],
            items=( #(PROP_ITEM_OBJECT_MESH,
                    #        ms3d_str['PROP_ITEM_OBJECT_MESH_1'],
                    #        ms3d_str['PROP_ITEM_OBJECT_MESH_2']),
                    (PROP_ITEM_OBJECT_MATERIAL,
                            ms3d_str['PROP_ITEM_OBJECT_MATERIAL_1'],
                            ms3d_str['PROP_ITEM_OBJECT_MATERIAL_2']),
                    (PROP_ITEM_OBJECT_JOINT,
                            ms3d_str['PROP_ITEM_OBJECT_JOINT_1'],
                            ms3d_str['PROP_ITEM_OBJECT_JOINT_2']),
                    #(PROP_ITEM_OBJECT_ANIMATION,
                    #        ms3d_str['PROP_ITEM_OBJECT_ANIMATION_1'],
                    #        ms3d_str['PROP_ITEM_OBJECT_ANIMATION_2']),
                    ),
            default=PROP_DEFAULT_OBJECTS_EXP,
            options={'ENUM_FLAG', 'ANIMATABLE', },
            )

    prop_selected = BoolProperty(
            name=ms3d_str['PROP_NAME_SELECTED'],
            description=ms3d_str['PROP_DESC_SELECTED'],
            default=PROP_DEFAULT_SELECTED,
            )

    prop_animation = BoolProperty(
            name=ms3d_str['PROP_NAME_ANIMATION'],
            description=ms3d_str['PROP_DESC_ANIMATION'],
            default=PROP_DEFAULT_ANIMATION,
            )

    @property
    def handle_animation(self):
        return (PROP_ITEM_OBJECT_ANIMATION in self.prop_objects)

    @property
    def handle_materials(self):
        return (PROP_ITEM_OBJECT_MATERIAL in self.prop_objects)

    @property
    def handle_joints(self):
        return (PROP_ITEM_OBJECT_JOINT in self.prop_objects)

    @property
    def handle_smoothing_groups(self):
        return (PROP_ITEM_OBJECT_SMOOTHGROUPS in self.prop_objects)

    @property
    def handle_groups(self):
        return (PROP_ITEM_OBJECT_GROUP in self.prop_objects)


    @property
    def is_coordinate_system_1by1(self):
        return (PROP_ITEM_COORDINATESYSTEM_1_BY_1 in self.prop_coordinate_system)

    @property
    def is_coordinate_system_import(self):
        return (PROP_ITEM_COORDINATESYSTEM_IMP in self.prop_coordinate_system)

    @property
    def is_coordinate_system_export(self):
        return (PROP_ITEM_COORDINATESYSTEM_EXP in self.prop_coordinate_system)


    # draw the option panel
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_OPTIONS'], icon=LABEL_ICON_OPTIONS)
        box.prop(self, 'prop_verbose', icon='SPEAKER')

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_OBJECT'], icon=LABEL_ICON_OBJECT)
        box.prop(self, 'prop_coordinate_system', icon='WORLD_DATA', expand=True)
        box.prop(self, 'prop_scale', icon='MESH_DATA')

        box = layout.box()
        box.label(ms3d_str['LABEL_NAME_PROCESSING'], icon=LABEL_ICON_PROCESSING)
        box.prop(self, 'prop_selected', icon='ROTACTIVE')
        box.prop(self, 'prop_objects', icon='MESH_DATA', expand=True)

        if (PROP_ITEM_OBJECT_JOINT in self.prop_objects):
            box.label(ms3d_str['REMARKS_2'], icon='ERROR')

            box = layout.box()
            box.label(ms3d_str['LABEL_NAME_ANIMATION'], icon=LABEL_ICON_ANIMATION)
            box.prop(self, 'prop_animation')

    # entrypoint for blender -> MS3D
    def execute(self, blender_context):
        """start executing"""
        from io_scene_ms3d.ms3d_export import (Ms3dExporter, )
        return Ms3dExporter(self).write(blender_context)

    #
    def invoke(self, blender_context, event):
        blender_context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL", }


###############################################################################
##
###############################################################################

MS3D_SMOOTHING_GROUP_APPLY = 'io_scene_ms3d.apply_smoothing_group'
MS3D_GROUP_APPLY = 'io_scene_ms3d.apply_group'

###############################################################################

###############################################################################
class Ms3dSetSmoothingGroupOperator(Operator):
    bl_idname = MS3D_SMOOTHING_GROUP_APPLY
    bl_label = ms3d_str['BL_LABEL_SMOOTHING_GROUP_OPERATOR']
    bl_options = {'INTERNAL', }

    smoothing_group_index = IntProperty(
            name=ms3d_str['PROP_SMOOTHING_GROUP_INDEX'],
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                and context.mode == 'EDIT_MESH'
                and context.tool_settings.mesh_select_mode[2]
                )

    def execute(self, context):
        custom_data = context.object.data.ms3d
        blender_mesh = context.object.data
        bm = from_edit_mesh(blender_mesh)
        layer_smoothing_group = bm.faces.layers.int.get(ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
        if custom_data.apply_mode in {'SELECT', 'DESELECT', }:
            if layer_smoothing_group is not None:
                is_select = (custom_data.apply_mode == 'SELECT')
                for bmf in bm.faces:
                    if (bmf[layer_smoothing_group] == self.smoothing_group_index):
                        bmf.select_set(is_select)
        elif custom_data.apply_mode == 'ASSIGN':
            if layer_smoothing_group is None:
                layer_smoothing_group = bm.faces.layers.int.new(ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
                blender_mesh_object = context.object
                blender_modifier = blender_mesh_object.modifiers.get(ms3d_str['OBJECT_MODIFIER_SMOOTHING_GROUP'])
                if blender_modifier is None:
                    blender_modifier = blender_mesh_object.modifiers.new(ms3d_str['OBJECT_MODIFIER_SMOOTHING_GROUP'], type='EDGE_SPLIT')
                    blender_modifier.show_expanded = False
                    blender_modifier.use_edge_angle = False
                    blender_modifier.use_edge_sharp = True
            blender_face_list = []
            for bmf in bm.faces:
                if bmf.select:
                    bmf[layer_smoothing_group] = self.smoothing_group_index
                    blender_face_list.append(bmf)
            edge_dict = {}
            for bmf in blender_face_list:
                bmf.smooth = True
                for bme in bmf.edges:
                    if edge_dict.get(bme) is None:
                        edge_dict[bme] = 0
                    else:
                        edge_dict[bme] += 1
                    is_border = (edge_dict[bme] == 0)
                    if is_border:
                        surround_face_smoothing_group_index = self.smoothing_group_index
                        for bmf in bme.link_faces:
                            if bmf[layer_smoothing_group] != surround_face_smoothing_group_index:
                                surround_face_smoothing_group_index = bmf[layer_smoothing_group]
                                break;
                        if surround_face_smoothing_group_index == self.smoothing_group_index:
                            is_border = False
                    bme.seam = is_border
                    bme.smooth = not is_border
        bm.free()
        enable_edit_mode(False)
        enable_edit_mode(True)
        return {'FINISHED', }

class Ms3dGroupCollectionOperator(Operator):
    bl_idname = MS3D_GROUP_APPLY
    bl_label = ms3d_str['BL_LABEL_GROUP_OPERATOR']
    bl_options = {'INTERNAL', }

    mode = EnumProperty(
            items=( ('', "", ""),
                    ('ADD_GROUP', ms3d_str['ENUM_ADD_GROUP_1'], ms3d_str['ENUM_ADD_GROUP_2']),
                    ('REMOVE_GROUP', ms3d_str['ENUM_REMOVE_GROUP_1'], ms3d_str['ENUM_REMOVE_GROUP_2']),
                    ('ASSIGN', ms3d_str['ENUM_ASSIGN_1'], ms3d_str['ENUM_ASSIGN_2_GROUP']),
                    ('REMOVE', ms3d_str['ENUM_REMOVE_1'], ms3d_str['ENUM_REMOVE_2_GROUP']),
                    ('SELECT', ms3d_str['ENUM_SELECT_1'], ms3d_str['ENUM_SELECT_2_GROUP']),
                    ('DESELECT', ms3d_str['ENUM_DESELECT_1'], ms3d_str['ENUM_DESELECT_2_GROUP']),
                    ),
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                #and context.object.data.ms3d.selected_group_index != -1
                )

    def execute(self, context):
        custom_data = context.object.data.ms3d
        blender_mesh = context.object.data
        bm = from_edit_mesh(blender_mesh)

        if self.mode == 'ADD_GROUP':
            item = custom_data.create_group()
            layer_group = bm.faces.layers.int.get(ms3d_str['OBJECT_LAYER_GROUP'])
            if layer_group is None:
                bm.faces.layers.int.new(ms3d_str['OBJECT_LAYER_GROUP'])

        elif self.mode == 'REMOVE_GROUP':
            custom_data.remove_group()

        elif (custom_data.selected_group_index >= 0) and (custom_data.selected_group_index < len(custom_data.groups)):
            if self.mode in {'SELECT', 'DESELECT', }:
                layer_group = bm.faces.layers.int.get(ms3d_str['OBJECT_LAYER_GROUP'])
                if layer_group is not None:
                    is_select = (self.mode == 'SELECT')
                    id = custom_data.groups[custom_data.selected_group_index].id
                    for bmf in bm.faces:
                        if bmf[layer_group] == id:
                            bmf.select_set(is_select)

            elif self.mode in {'ASSIGN', 'REMOVE', }:
                layer_group = bm.faces.layers.int.get(ms3d_str['OBJECT_LAYER_GROUP'])
                if layer_group is None:
                    layer_group = bm.faces.layers.int.new(ms3d_str['OBJECT_LAYER_GROUP'])

                is_assign = (self.mode == 'ASSIGN')
                id = custom_data.groups[custom_data.selected_group_index].id
                for bmf in bm.faces:
                    if bmf.select:
                        if is_assign:
                            bmf[layer_group] = id
                        else:
                            bmf[layer_group] = -1
        if bm is not None:
            bm.free()
        enable_edit_mode(False)
        enable_edit_mode(True)
        return {'FINISHED', }

###############################################################################
# imported
class Ms3dGroupPropertyGroup(PropertyGroup):
    name = StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_GROUP_NAME'],
            default="",
            #options={'HIDDEN', },
            )

    flags = EnumProperty(
            name=ms3d_str['PROP_NAME_FLAGS'],
            description=ms3d_str['PROP_DESC_FLAGS_GROUP'],
            items=(#(UI_FLAG_NONE, ms3d_str['ENUM_FLAG_NONE_1'], ms3d_str['ENUM_FLAG_NONE_2'], MS3D_FLAG_NONE),
                    (UI_FLAG_SELECTED, ms3d_str['ENUM_FLAG_SELECTED_1'], ms3d_str['ENUM_FLAG_SELECTED_2'], MS3D_FLAG_SELECTED),
                    (UI_FLAG_HIDDEN, ms3d_str['ENUM_FLAG_HIDDEN_1'], ms3d_str['ENUM_FLAG_HIDDEN_2'], MS3D_FLAG_HIDDEN),
                    (UI_FLAG_SELECTED2, ms3d_str['ENUM_FLAG_SELECTED2_1'], ms3d_str['ENUM_FLAG_SELECTED2_2'], MS3D_FLAG_SELECTED2),
                    (UI_FLAG_DIRTY, ms3d_str['ENUM_FLAG_DIRTY_1'], ms3d_str['ENUM_FLAG_DIRTY_2'], MS3D_FLAG_DIRTY),
                    (UI_FLAG_ISKEY, ms3d_str['ENUM_FLAG_ISKEY_1'], ms3d_str['ENUM_FLAG_ISKEY_2'], MS3D_FLAG_ISKEY),
                    (UI_FLAG_NEWLYCREATED, ms3d_str['ENUM_FLAG_NEWLYCREATED_1'], ms3d_str['ENUM_FLAG_NEWLYCREATED_2'], MS3D_FLAG_NEWLYCREATED),
                    (UI_FLAG_MARKED, ms3d_str['ENUM_FLAG_MARKED_1'], ms3d_str['ENUM_FLAG_MARKED_2'], MS3D_FLAG_MARKED),
                    ),
            default=ms3d_flags_to_ui(DEFAULT_FLAGS),
            options={'ENUM_FLAG', 'ANIMATABLE', },
            )

    comment = StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_GROUP'],
            default="",
            #options={'HIDDEN', },
            )

    template_list_controls = StringProperty(
            default="",
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    id = IntProperty(options={'HIDDEN', },)


class Ms3dModelPropertyGroup(PropertyGroup):
    name = StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_MODEL'],
            default="",
            #options={'HIDDEN', },
            )

    joint_size = FloatProperty(
            name=ms3d_str['PROP_NAME_JOINT_SIZE'],
            description=ms3d_str['PROP_DESC_JOINT_SIZE'],
            min=0, max=1, precision=3, step=0.1,
            default=DEFAULT_MODEL_JOINT_SIZE,
            subtype='FACTOR',
            #options={'HIDDEN', },
            )

    transparency_mode = EnumProperty(
            name=ms3d_str['PROP_NAME_TRANSPARENCY_MODE'],
            description=ms3d_str['PROP_DESC_TRANSPARENCY_MODE'],
            items=( (UI_MODE_TRANSPARENCY_SIMPLE,
                            ms3d_str['PROP_MODE_TRANSPARENCY_SIMPLE_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_SIMPLE_2'],
                            MS3D_MODE_TRANSPARENCY_SIMPLE),
                    (UI_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES,
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES_2'],
                            MS3D_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES),
                    (UI_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF,
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF_2'],
                            MS3D_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF),
                    ),
            default=ms3d_transparency_mode_to_ui(DEFAULT_MODEL_TRANSPARENCY_MODE),
            #options={'HIDDEN', },
            )

    alpha_ref = FloatProperty(
            name=ms3d_str['PROP_NAME_ALPHA_REF'],
            description=ms3d_str['PROP_DESC_ALPHA_REF'],
            min=0, max=1, precision=3, step=0.1,
            default=0.5,
            subtype='FACTOR',
            #options={'HIDDEN', },
            )

    comment = StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_MODEL'],
            default="",
            #options={'HIDDEN', },
            )

    ##########################
    # ms3d group handling
    #
    apply_mode = EnumProperty(
            items=( ('ASSIGN', ms3d_str['ENUM_ASSIGN_1'], ms3d_str['ENUM_ASSIGN_2_SMOOTHING_GROUP']),
                    ('SELECT', ms3d_str['ENUM_SELECT_1'], ms3d_str['ENUM_SELECT_2_SMOOTHING_GROUP']),
                    ('DESELECT', ms3d_str['ENUM_DESELECT_1'], ms3d_str['ENUM_DESELECT_2_SMOOTHING_GROUP']),
                    ),
            default='SELECT',
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    selected_group_index = IntProperty(
            default=-1,
            min=-1,
            options={'HIDDEN', 'SKIP_SAVE', },
            )
    #
    # ms3d group handling
    ##########################

    groups = CollectionProperty(
            type=Ms3dGroupPropertyGroup,
            #options={'HIDDEN', },
            )


    def generate_unique_id(self):
        return randrange(1, 0x7FFFFFFF) # pseudo unique id

    def create_group(self):
        item = self.groups.add()
        item.id = self.generate_unique_id()
        length = len(self.groups)
        self.selected_group_index = length - 1

        item.name = ms3d_str['STRING_FORMAT_GROUP'].format(length)
        return item

    def remove_group(self):
        index = self.selected_group_index
        length = len(self.groups)
        if (index >= 0) and (index < length):
            if index > 0 or length == 1:
                self.selected_group_index = index - 1
            self.groups.remove(index)

class Ms3dArmaturePropertyGroup(PropertyGroup):
    name = StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_ARMATURE'],
            default="",
            #options={'HIDDEN', },
            )


class Ms3dJointPropertyGroup(PropertyGroup):
    name = StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_JOINT'],
            default="",
            #options={'HIDDEN', },
            )

    flags = EnumProperty(
            name=ms3d_str['PROP_NAME_FLAGS'],
            description=ms3d_str['PROP_DESC_FLAGS_JOINT'],
            items=(#(UI_FLAG_NONE, ms3d_str['ENUM_FLAG_NONE_1'], ms3d_str['ENUM_FLAG_NONE_2'], MS3D_FLAG_NONE),
                    (UI_FLAG_SELECTED, ms3d_str['ENUM_FLAG_SELECTED_1'], ms3d_str['ENUM_FLAG_SELECTED_2'], MS3D_FLAG_SELECTED),
                    (UI_FLAG_HIDDEN, ms3d_str['ENUM_FLAG_HIDDEN_1'], ms3d_str['ENUM_FLAG_HIDDEN_2'], MS3D_FLAG_HIDDEN),
                    (UI_FLAG_SELECTED2, ms3d_str['ENUM_FLAG_SELECTED2_1'], ms3d_str['ENUM_FLAG_SELECTED2_2'], MS3D_FLAG_SELECTED2),
                    (UI_FLAG_DIRTY, ms3d_str['ENUM_FLAG_DIRTY_1'], ms3d_str['ENUM_FLAG_DIRTY_2'], MS3D_FLAG_DIRTY),
                    (UI_FLAG_ISKEY, ms3d_str['ENUM_FLAG_ISKEY_1'], ms3d_str['ENUM_FLAG_ISKEY_2'], MS3D_FLAG_ISKEY),
                    (UI_FLAG_NEWLYCREATED, ms3d_str['ENUM_FLAG_NEWLYCREATED_1'], ms3d_str['ENUM_FLAG_NEWLYCREATED_2'], MS3D_FLAG_NEWLYCREATED),
                    (UI_FLAG_MARKED, ms3d_str['ENUM_FLAG_MARKED_1'], ms3d_str['ENUM_FLAG_MARKED_2'], MS3D_FLAG_MARKED),
                    ),
            default=ms3d_flags_to_ui(DEFAULT_FLAGS),
            options={'ENUM_FLAG', 'ANIMATABLE', },
            )

    color = FloatVectorProperty(
            name=ms3d_str['PROP_NAME_COLOR'],
            description=ms3d_str['PROP_DESC_COLOR_JOINT'],
            subtype='COLOR', size=3, min=0, max=1, precision=3, step=0.1,
            default=(0.8, 0.8, 0.8),
            #options={'HIDDEN', },
            )

    comment = StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_JOINT'],
            default="",
            #options={'HIDDEN', },
            )


# imported
class Ms3dMaterialPropertyGroupHelper:
    @staticmethod
    def on_update_ambient(cls, context):
        pass

    @staticmethod
    def on_update_diffuse(cls, context):
        cls.id_data.diffuse_color = cls.diffuse[0:3]
        cls.id_data.diffuse_intensity = cls.diffuse[3]
        pass

    @staticmethod
    def on_update_specular(cls, context):
        cls.id_data.specular_color = cls.specular[0:3]
        cls.id_data.specular_intensity = cls.specular[3]
        pass

    @staticmethod
    def on_update_emissive(cls, context):
        cls.id_data.emit = (cls.emissive[0] + cls.emissive[1] + cls.emissive[2]) / 3.0
        pass

    @staticmethod
    def on_update_shininess(cls, context):
        cls.id_data.specular_hardness = cls.shininess * 4.0
        pass

    @staticmethod
    def on_update_transparency(cls, context):
        cls.id_data.alpha = cls.transparency
        pass


class Ms3dMaterialPropertyGroup(PropertyGroup):
    name = StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_MATERIAL'],
            default="",
            #options={'HIDDEN', },
            )

    ambient = FloatVectorProperty(
            name=ms3d_str['PROP_NAME_AMBIENT'],
            description=ms3d_str['PROP_DESC_AMBIENT'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=(0.2, 0.2, 0.2, 1.0), # OpenGL default for ambient
            update=Ms3dMaterialPropertyGroupHelper.on_update_ambient,
            #options={'HIDDEN', },
            )

    diffuse = FloatVectorProperty(
            name=ms3d_str['PROP_NAME_DIFFUSE'],
            description=ms3d_str['PROP_DESC_DIFFUSE'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=(0.8, 0.8, 0.8, 1.0), # OpenGL default for diffuse
            update=Ms3dMaterialPropertyGroupHelper.on_update_diffuse,
            #options={'HIDDEN', },
            )

    specular = FloatVectorProperty(
            name=ms3d_str['PROP_NAME_SPECULAR'],
            description=ms3d_str['PROP_DESC_SPECULAR'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=(0.0, 0.0, 0.0, 1.0), # OpenGL default for specular
            update=Ms3dMaterialPropertyGroupHelper.on_update_specular,
            #options={'HIDDEN', },
            )

    emissive = FloatVectorProperty(
            name=ms3d_str['PROP_NAME_EMISSIVE'],
            description=ms3d_str['PROP_DESC_EMISSIVE'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=(0.0, 0.0, 0.0, 1.0), # OpenGL default for emissive
            update=Ms3dMaterialPropertyGroupHelper.on_update_emissive,
            #options={'HIDDEN', },
            )

    shininess = FloatProperty(
            name=ms3d_str['PROP_NAME_SHININESS'],
            description=ms3d_str['PROP_DESC_SHININESS'],
            min=0, max=MAX_MATERIAL_SHININESS, precision=3, step=0.1,
            default=0,
            subtype='FACTOR',
            update=Ms3dMaterialPropertyGroupHelper.on_update_shininess,
            #options={'HIDDEN', },
            )

    transparency = FloatProperty(
            name=ms3d_str['PROP_NAME_TRANSPARENCY'],
            description=ms3d_str['PROP_DESC_TRANSPARENCY'],
            min=0, max=1, precision=3, step=0.1,
            default=0,
            subtype='FACTOR',
            update=Ms3dMaterialPropertyGroupHelper.on_update_transparency,
            #options={'HIDDEN', },
            )

    mode = EnumProperty(
            name=ms3d_str['PROP_NAME_MODE'],
            description=ms3d_str['PROP_DESC_MODE_TEXTURE'],
            items=( (UI_FLAG_TEXTURE_COMBINE_ALPHA,
                            ms3d_str['PROP_FLAG_TEXTURE_COMBINE_ALPHA_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_COMBINE_ALPHA_2'],
                            MS3D_FLAG_TEXTURE_COMBINE_ALPHA),
                    (UI_FLAG_TEXTURE_HAS_ALPHA,
                            ms3d_str['PROP_FLAG_TEXTURE_HAS_ALPHA_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_HAS_ALPHA_2'],
                            MS3D_FLAG_TEXTURE_HAS_ALPHA),
                    (UI_FLAG_TEXTURE_SPHERE_MAP,
                            ms3d_str['PROP_FLAG_TEXTURE_SPHERE_MAP_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_SPHERE_MAP_2'],
                            MS3D_FLAG_TEXTURE_SPHERE_MAP),
                    ),
            default=ms3d_texture_mode_to_ui(DEFAULT_MATERIAL_MODE),
            options={'ANIMATABLE', 'ENUM_FLAG', },
            )

    texture = StringProperty(
            name=ms3d_str['PROP_NAME_TEXTURE'],
            description=ms3d_str['PROP_DESC_TEXTURE'],
            default="",
            subtype = 'FILE_PATH'
            #options={'HIDDEN', },
            )

    alphamap = StringProperty(
            name=ms3d_str['PROP_NAME_ALPHAMAP'],
            description=ms3d_str['PROP_DESC_ALPHAMAP'],
            default="",
            subtype = 'FILE_PATH'
            #options={'HIDDEN', },
            )

    comment = StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_MATERIAL'],
            default="",
            #options={'HIDDEN', },
            )


###############################################################################
class Ms3dMeshObjectPanel(Panel):
    bl_label = ms3d_str['LABEL_PANEL_MODEL']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                )

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, context):
        layout = self.layout
        custom_data = context.object.data.ms3d

        col = layout.column()
        col.prop(custom_data, 'name')
        col.prop(custom_data, 'joint_size')
        col.prop(custom_data, 'transparency_mode')
        col.prop(custom_data, 'alpha_ref', )
        col.prop(custom_data, 'comment')


class Ms3dMaterialPanel(Panel):
    bl_label = ms3d_str['LABEL_PANEL_MATERIALS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                and context.material
                and context.material.ms3d is not None
                )

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, context):
        layout = self.layout
        custom_data = context.material.ms3d

        col = layout.column()
        col.prop(custom_data, 'name')
        col.separator()
        row = col.row()
        row.prop(custom_data, 'ambient')
        row.prop(custom_data, 'diffuse')
        row = col.row()
        row.prop(custom_data, 'specular')
        row.prop(custom_data, 'emissive')
        col.separator()
        row = col.row()
        row.prop(custom_data, 'shininess')
        row.prop(custom_data, 'transparency')
        col.separator()
        col.prop(custom_data, 'texture')
        col.prop(custom_data, 'alphamap')
        col.separator()
        col.prop(custom_data, 'mode')
        col.separator()
        col.prop(custom_data, 'comment')


class Ms3dBonePanel(Panel):
    bl_label = ms3d_str['LABEL_PANEL_JOINTS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return (context
                and context.object.type in {'ARMATURE', }
                and context.active_bone
                and isinstance(context.active_bone, Bone)
                and context.active_bone.ms3d is not None
                )

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, context):
        import bpy
        layout = self.layout
        custom_data = context.active_bone.ms3d

        col = layout.column()
        col.prop(custom_data, 'name')
        col.prop(custom_data, 'flags')
        col.prop(custom_data, 'color')
        col.prop(custom_data, 'comment')


class Ms3dGroupDataPanel(Panel):
    bl_label = ms3d_str['LABEL_PANEL_GROUPS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                )

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, context):
        layout = self.layout
        custom_data = context.object.data.ms3d

        col = layout.column()

        row = col.row()
        row.template_list(
                custom_data, 'groups',
                custom_data, 'selected_group_index',
                prop_list='template_list_controls',
                rows=2,
                type='DEFAULT',
                )

        rowcol = row.column()
        rowcolrow =rowcol.row()
        rowcolrowcol = rowcolrow.column(align=True)
        rowcolrowcol.operator(MS3D_GROUP_APPLY, text="", icon='ZOOMIN').mode = 'ADD_GROUP'
        rowcolrowcol.operator(MS3D_GROUP_APPLY, text="", icon='ZOOMOUT').mode = 'REMOVE_GROUP'

        index = custom_data.selected_group_index
        collection = custom_data.groups
        if (index >= 0 and index < len(collection)):
            col.prop(collection[index], 'name')

            if (context.mode == 'EDIT_MESH') and (context.tool_settings.mesh_select_mode[2]):
                row = col.row()
                rowrow = row.row(align=True)
                rowrow.operator(MS3D_GROUP_APPLY, text=ms3d_str['ENUM_ASSIGN_1']).mode = 'ASSIGN'
                rowrow.operator(MS3D_GROUP_APPLY, text=ms3d_str['ENUM_REMOVE_1']).mode = 'REMOVE'
                rowrow = row.row(align=True)
                rowrow.operator(MS3D_GROUP_APPLY, text=ms3d_str['ENUM_SELECT_1']).mode = 'SELECT'
                rowrow.operator(MS3D_GROUP_APPLY, text=ms3d_str['ENUM_DESELECT_1']).mode = 'DESELECT'

            col.prop(collection[index], 'comment')


class Ms3dSmoothingGroupDataPanel(Panel):
    bl_label = ms3d_str['BL_LABEL_PANEL_SMOOTHING_GROUP']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return (context
                and context.object
                and context.object.type in {'MESH', }
                and context.object.data
                and context.object.data.ms3d is not None
                )

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, context):
        custom_data = context.object.data.ms3d
        layout = self.layout

        col = layout.column()
        #box = col.box()
        col.enabled = (context.mode == 'EDIT_MESH') and (context.tool_settings.mesh_select_mode[2])
        row = col.row()
        row.prop(custom_data, 'apply_mode', expand=True)

        col = col.column(align=True)
        row = col.row(align=True)
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="1").smoothing_group_index = 1
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="2").smoothing_group_index = 2
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="3").smoothing_group_index = 3
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="4").smoothing_group_index = 4
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="5").smoothing_group_index = 5
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="6").smoothing_group_index = 6
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="7").smoothing_group_index = 7
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="8").smoothing_group_index = 8
        row = col.row(align=True)
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="9").smoothing_group_index = 9
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="10").smoothing_group_index = 10
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="11").smoothing_group_index = 11
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="12").smoothing_group_index = 12
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="13").smoothing_group_index = 13
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="14").smoothing_group_index = 14
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="15").smoothing_group_index = 15
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="16").smoothing_group_index = 16
        row = col.row(align=True)
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="17").smoothing_group_index = 17
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="18").smoothing_group_index = 18
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="19").smoothing_group_index = 19
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="20").smoothing_group_index = 20
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="21").smoothing_group_index = 21
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="22").smoothing_group_index = 22
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="23").smoothing_group_index = 23
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="24").smoothing_group_index = 24
        row = col.row(align=True)
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="25").smoothing_group_index = 25
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="26").smoothing_group_index = 26
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="27").smoothing_group_index = 27
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="28").smoothing_group_index = 28
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="29").smoothing_group_index = 29
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="30").smoothing_group_index = 30
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="31").smoothing_group_index = 31
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text="32").smoothing_group_index = 32
        row = col.row()
        row.operator(MS3D_SMOOTHING_GROUP_APPLY, text=ms3d_str['LABEL_PANEL_BUTTON_NONE']).smoothing_group_index = 0


###############################################################################
def register_property_groups():
    register_class(Ms3dGroupPropertyGroup)
    register_class(Ms3dModelPropertyGroup)
    register_class(Ms3dArmaturePropertyGroup)
    register_class(Ms3dJointPropertyGroup)
    register_class(Ms3dMaterialPropertyGroup)
    inject_properties()
    register_class(Ms3dSetSmoothingGroupOperator)
    register_class(Ms3dGroupCollectionOperator)

def unregister_property_groups():
    unregister_class(Ms3dGroupCollectionOperator)
    unregister_class(Ms3dSetSmoothingGroupOperator)
    delete_properties()
    unregister_class(Ms3dMaterialPropertyGroup)
    unregister_class(Ms3dJointPropertyGroup)
    unregister_class(Ms3dArmaturePropertyGroup)
    unregister_class(Ms3dModelPropertyGroup)
    unregister_class(Ms3dGroupPropertyGroup)

def inject_properties():
    Mesh.ms3d = PointerProperty(type=Ms3dModelPropertyGroup)
    Armature.ms3d = PointerProperty(type=Ms3dArmaturePropertyGroup)
    Bone.ms3d = PointerProperty(type=Ms3dJointPropertyGroup)
    Material.ms3d = PointerProperty(type=Ms3dMaterialPropertyGroup)
    Action.ms3d = PointerProperty(type=Ms3dArmaturePropertyGroup)
    Group.ms3d = PointerProperty(type=Ms3dGroupPropertyGroup)

def delete_properties():
    del Mesh.ms3d
    del Armature.ms3d
    del Bone.ms3d
    del Material.ms3d
    del Action.ms3d
    del Group.ms3d

###############################################################################
register_property_groups()


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
