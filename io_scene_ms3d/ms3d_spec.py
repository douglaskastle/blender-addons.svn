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


from struct import (
        pack,
        unpack,
        )
from sys import (
        exc_info,
        )
from os import (
        fstat,
        )

###############################################################################
#
# MilkShape 3D 1.8.5 File Format Specification
#
# all specifications were taken from SDK 1.8.5
#
# some additional specifications were taken from
# MilkShape 3D Viewer v2.0 (Nov 06 2007) - msMesh.h
#


###############################################################################
#
# sizes
#

class Ms3dSpec:
    ###########################################################################
    #
    # max values
    #
    MAX_VERTICES = 65534 # 0..65533; note: (65534???, 65535???)
    MAX_TRIANGLES = 65534 # 0..65533; note: (65534???, 65535???)
    MAX_GROUPS = 255 # 1..255; note: (0 default group)
    MAX_MATERIALS = 128 # 0..127; note: (-1 no material)
    MAX_JOINTS = 128 # 0..127; note: (-1 no joint)
    MAX_SMOOTH_GROUP = 32 # 0..32; note: (0 no smoothing group)
    MAX_TEXTURE_FILENAME_SIZE = 128

    ###########################################################################
    #
    # flags
    #
    FLAG_NONE = 0
    FLAG_SELECTED = 1
    FLAG_HIDDEN = 2
    FLAG_SELECTED2 = 4
    FLAG_DIRTY = 8
    FLAG_ISKEY = 16 # additional spec from [2]
    FLAG_NEWLYCREATED = 32 # additional spec from [2]
    FLAG_MARKED = 64 # additional spec from [2]

    FLAG_TEXTURE_NONE = 0x00
    FLAG_TEXTURE_COMBINE_ALPHA = 0x20
    FLAG_TEXTURE_HAS_ALPHA = 0x40
    FLAG_TEXTURE_SPHERE_MAP = 0x80

    MODE_TRANSPARENCY_SIMPLE = 0
    MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF = 1
    MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES = 2


    ###########################################################################
    #
    # values
    #
    HEADER = "MS3D000000"


    ###########################################################################
    #
    # min, max, default values
    #
    NONE_VERTEX_BONE_ID = -1
    NONE_GROUP_MATERIAL_INDEX = -1

    DEFAULT_HEADER = HEADER
    DEFAULT_HEADER_VERSION = 4
    DEFAULT_VERTEX_BONE_ID = NONE_VERTEX_BONE_ID
    DEFAULT_TRIANGLE_SMOOTHING_GROUP = 0
    DEFAULT_TRIANGLE_GROUP = 0
    DEFAULT_MATERIAL_MODE = FLAG_TEXTURE_NONE
    DEFAULT_GROUP_MATERIAL_INDEX = NONE_GROUP_MATERIAL_INDEX
    DEFAULT_MODEL_JOINT_SIZE = 1.0
    DEFAULT_MODEL_TRANSPARENCY_MODE = MODE_TRANSPARENCY_SIMPLE
    DEFAULT_MODEL_ANIMATION_FPS = 25.0
    DEFAULT_MODEL_SUB_VERSION_COMMENTS = 1
    DEFAULT_MODEL_SUB_VERSION_VERTEX_EXTRA = 2
    DEFAULT_MODEL_SUB_VERSION_JOINT_EXTRA = 1
    DEFAULT_MODEL_SUB_VERSION_MODEL_EXTRA = 1
    DEFAULT_FLAGS = FLAG_NONE
    MAX_MATERIAL_SHININESS = 128


###############################################################################
#
# helper class for basic raw io
#
class EOF(BaseException):
    pass

class Ms3dIo:
    # sizes for IO
    SIZE_BYTE = 1
    SIZE_SBYTE = 1
    SIZE_WORD = 2
    SIZE_DWORD = 4
    SIZE_FLOAT = 4
    LENGTH_ID = 10
    LENGTH_NAME = 32
    LENGTH_FILENAME = 128

    @staticmethod
    def raise_on_eof(file):
        """ pseudo end of file detection """
        fd = file.fileno()
        stat = fstat(fd)
        if file.tell() >= stat.st_size:
            raise EOF()

    @staticmethod
    def read_byte(file):
        """ read a single byte from file """
        value = unpack('<B', file.read(Ms3dIo.SIZE_BYTE))[0]
        return value

    @staticmethod
    def write_byte(file, value):
        """ write a single byte to file """
        file.write(pack('<B', value))

    @staticmethod
    def read_sbyte(file):
        """ read a single signed byte from file """
        value = unpack('<b', file.read(Ms3dIo.SIZE_SBYTE))[0]
        return value

    @staticmethod
    def write_sbyte(file, value):
        """ write a single signed byte to file """
        file.write(pack('<b', value))

    @staticmethod
    def read_word(file):
        """ read a word from file """
        value = unpack('<H', file.read(Ms3dIo.SIZE_WORD))[0]
        return value

    @staticmethod
    def write_word(file, value):
        """ write a word to file """
        file.write(pack('<H', value))

    @staticmethod
    def read_dword(file):
        """ read a double word from file """
        value = unpack('<I', file.read(Ms3dIo.SIZE_DWORD))[0]
        return value

    @staticmethod
    def write_dword(file, value):
        """ write a double word to file """
        file.write(pack('<I', value))

    @staticmethod
    def read_float(file):
        """ read a float from file """
        value = unpack('<f', file.read(Ms3dIo.SIZE_FLOAT))[0]
        return value

    @staticmethod
    def write_float(file, value):
        """ write a float to file """
        file.write(pack('<f', value))

    @staticmethod
    def read_array(file, itemReader, count):
        """ read an array[count] of objects from file, by using a itemReader """
        value = []
        for i in range(count):
            itemValue = itemReader(file)
            value.append(itemValue)
        return tuple(value)

    @staticmethod
    def write_array(file, itemWriter, count, value):
        """ write an array[count] of objects to file, by using a itemWriter """
        for i in range(count):
            itemValue = value[i]
            itemWriter(file, itemValue)

    @staticmethod
    def read_array2(file, itemReader, count, count2):
        """ read an array[count][count2] of objects from file,
            by using a itemReader """
        value = []
        for i in range(count):
            itemValue = Ms3dIo.read_array(file, itemReader, count2)
            value.append(tuple(itemValue))
        return value

    @staticmethod
    def write_array2(file, itemWriter, count, count2, value):
        """ write an array[count][count2] of objects to file,
            by using a itemWriter """
        for i in range(count):
            itemValue = value[i]
            Ms3dIo.write_array(file, itemWriter, count2, itemValue)

    @staticmethod
    def read_string(file, length):
        """ read a string of a specific length from file """
        value = []
        skip = False
        for i in range(length):
            raw = unpack('<b', file.read(Ms3dIo.SIZE_SBYTE))[0]
            if (raw >= 32) & (raw <= 255):
                pass
            else:
                if (raw == 0):
                    raw = 0
                    skip = True
                else:
                    raw = 32

            c = chr(raw)

            if (not skip):
                value.append(c)

        finalValue = "".join(value)
        return finalValue

    @staticmethod
    def write_string(file, length, value):
        """ write a string of a specific length to file """
        l = len(value)
        for i in range(length):
            if(i < l):
                c = value[i]

                if (isinstance(c, str)):
                    c = c[0]
                    raw = ord(c)
                elif (isinstance(c, int)):
                    raw = c
                else:
                    pass
            else:
                raw = 0

            file.write(pack('<b', raw % 255))


###############################################################################
#
# multi complex types
#

###############################################################################
class Ms3dHeader:
    """ Ms3dHeader """
    __slots__ = (
            'id',
            'version',
            )

    def __init__(
            self,
            default_id=Ms3dSpec.DEFAULT_HEADER,
            default_version=Ms3dSpec.DEFAULT_HEADER_VERSION
            ):
        self.id = default_id
        self.version = default_version

    def __repr__(self):
        return "\n<id='{0}', version={1}>".format(
            self.id,
            self.version
            )

    def __hash__(self):
        return hash(self.id) ^ hash(self.version)

    def __eq__(self, other):
        return ((self is not None) and (other is not None)
                and (self.id == other.id)
                and (self.version == other.version))

    def read(self, file):
        self.id = Ms3dIo.read_string(file, Ms3dIo.LENGTH_ID)
        self.version = Ms3dIo.read_dword(file)
        return self

    def write(self, file):
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_ID, self.id)
        Ms3dIo.write_dword(file, self.version)


###############################################################################
class Ms3dVertex:
    """ Ms3dVertex """
    """
    __slots__ was taking out,
    to be able to inject additional attributes during runtime
    __slots__ = (
            'flags',
            'bone_id',
            'reference_count',
            '_vertex',
            '_vertex_ex_object', # Ms3dVertexEx
            )
    """

    def __init__(
            self,
            default_flags=Ms3dSpec.DEFAULT_FLAGS,
            default_vertex=(0.0, 0.0, 0.0),
            default_bone_id=Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
            default_reference_count=0,
            default_vertex_ex_object=None, # Ms3dVertexEx
            ):
        self.flags = default_flags
        self._vertex = default_vertex
        self.bone_id = default_bone_id
        self.reference_count = default_reference_count

        if default_vertex_ex_object is None:
            default_vertex_ex_object = Ms3dVertexEx2()
            # Ms3dSpec.DEFAULT_MODEL_SUB_VERSION_VERTEX_EXTRA = 2
        self._vertex_ex_object = default_vertex_ex_object
        # Ms3dVertexEx

    def __repr__(self):
        return "\n<flags={0}, vertex={1}, bone_id={2},"\
                " reference_count={3}>".format(
                self.flags,
                self._vertex,
                self.bone_id,
                self.reference_count
                )

    def __hash__(self):
        return (hash(self.vertex)
                #^ hash(self.flags)
                #^ hash(self.bone_id)
                #^ hash(self.reference_count)
                )

    def __eq__(self, other):
        return ((self.vertex == other.vertex)
                #and (self.flags == other.flags)
                #and (self.bone_id == other.bone_id)
                #and (self.reference_count == other.reference_count)
                )


    @property
    def vertex(self):
        return self._vertex

    @property
    def vertex_ex_object(self):
        return self._vertex_ex_object


    def read(self, file):
        self.flags = Ms3dIo.read_byte(file)
        self._vertex = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        self.bone_id = Ms3dIo.read_sbyte(file)
        self.reference_count = Ms3dIo.read_byte(file)
        return self

    def write(self, file):
        Ms3dIo.write_byte(file, self.flags)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.vertex)
        Ms3dIo.write_sbyte(file, self.bone_id)
        Ms3dIo.write_byte(file, self.reference_count)


###############################################################################
class Ms3dTriangle:
    """ Ms3dTriangle """
    """
    __slots__ was taking out,
    to be able to inject additional attributes during runtime
    __slots__ = (
            'flags',
            'smoothing_group',
            'group_index',
            '_vertex_indices',
            '_vertex_normals',
            '_s',
            '_t',
            )
    """

    def __init__(
            self,
            default_flags=Ms3dSpec.DEFAULT_FLAGS,
            default_vertex_indices=(0, 0, 0),
            default_vertex_normals=(
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 0.0)),
            default_s=(0.0, 0.0, 0.0),
            default_t=(0.0, 0.0, 0.0),
            default_smoothing_group=Ms3dSpec.DEFAULT_TRIANGLE_SMOOTHING_GROUP,
            default_group_index=Ms3dSpec.DEFAULT_TRIANGLE_GROUP
            ):
        self.flags = default_flags
        self._vertex_indices = default_vertex_indices
        self._vertex_normals = default_vertex_normals
        self._s = default_s
        self._t = default_t
        self.smoothing_group = default_smoothing_group
        self.group_index = default_group_index

    def __repr__(self):
        return "\n<flags={0}, vertex_indices={1}, vertex_normals={2}, s={3},"\
                " t={4}, smoothing_group={5}, group_index={6}>".format(
                self.flags,
                self.vertex_indices,
                self.vertex_normals,
                self.s,
                self.t,
                self.smoothing_group,
                self.group_index
                )


    @property
    def vertex_indices(self):
        return self._vertex_indices

    @property
    def vertex_normals(self):
        return self._vertex_normals

    @property
    def s(self):
        return self._s

    @property
    def t(self):
        return self._t


    def read(self, file):
        self.flags = Ms3dIo.read_word(file)
        self._vertex_indices = Ms3dIo.read_array(file, Ms3dIo.read_word, 3)
        self._vertex_normals = Ms3dIo.read_array2(file, Ms3dIo.read_float, 3, 3)
        self._s = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        self._t = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        self.smoothing_group = Ms3dIo.read_byte(file)
        self.group_index = Ms3dIo.read_byte(file)
        return self

    def write(self, file):
        Ms3dIo.write_word(file, self.flags)
        Ms3dIo.write_array(file, Ms3dIo.write_word, 3, self.vertex_indices)
        Ms3dIo.write_array2(file, Ms3dIo.write_float, 3, 3, self.vertex_normals)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.s)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.t)
        Ms3dIo.write_byte(file, self.smoothing_group)
        Ms3dIo.write_byte(file, self.group_index)


###############################################################################
class Ms3dGroup:
    """ Ms3dGroup """
    """
    __slots__ was taking out,
    to be able to inject additional attributes during runtime
    __slots__ = (
            'flags',
            'name',
            'material_index',
            '_triangle_indices',
            '_comment_object', # Ms3dComment
            )
    """

    def __init__(
            self,
            default_flags=Ms3dSpec.DEFAULT_FLAGS,
            default_name="",
            default_triangle_indices=None,
            default_material_index=Ms3dSpec.DEFAULT_GROUP_MATERIAL_INDEX,
            default_comment_object=None, # Ms3dComment
            ):
        if (default_name is None):
            default_name = ""

        if (default_triangle_indices is None):
            default_triangle_indices = []

        self.flags = default_flags
        self.name = default_name
        self._triangle_indices = default_triangle_indices
        self.material_index = default_material_index

        if default_comment_object is None:
            default_comment_object = Ms3dCommentEx()
        self._comment_object = default_comment_object # Ms3dComment

    def __repr__(self):
        return "\n<flags={0}, name='{1}', number_triangles={2},"\
                " triangle_indices={3}, material_index={4}>".format(
                self.flags,
                self.name,
                self.number_triangles,
                self.triangle_indices,
                self.material_index
                )


    @property
    def number_triangles(self):
        if self.triangle_indices is None:
            return 0
        return len(self.triangle_indices)

    @property
    def triangle_indices(self):
        return self._triangle_indices

    @property
    def comment_object(self):
        return self._comment_object


    def read(self, file):
        self.flags = Ms3dIo.read_byte(file)
        self.name = Ms3dIo.read_string(file, Ms3dIo.LENGTH_NAME)
        _number_triangles = Ms3dIo.read_word(file)
        self._triangle_indices = Ms3dIo.read_array(
                file, Ms3dIo.read_word, _number_triangles)
        self.material_index = Ms3dIo.read_sbyte(file)
        return self

    def write(self, file):
        Ms3dIo.write_byte(file, self.flags)
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_NAME, self.name)
        Ms3dIo.write_word(file, self.number_triangles)
        Ms3dIo.write_array(
                file, Ms3dIo.write_word, self.number_triangles,
                self.triangle_indices)
        Ms3dIo.write_sbyte(file, self.material_index)


###############################################################################
class Ms3dMaterial:
    """ Ms3dMaterial """
    __slots__ = (
            'name',
            'shininess',
            'transparency',
            'mode',
            'texture',
            'alphamap',
            '_ambient',
            '_diffuse',
            '_specular',
            '_emissive',
            '_comment_object', # Ms3dComment
            )

    def __init__(
            self,
            default_name="",
            default_ambient=(0.0, 0.0, 0.0, 0.0),
            default_diffuse=(0.0, 0.0, 0.0, 0.0),
            default_specular=(0.0, 0.0, 0.0, 0.0),
            default_emissive=(0.0, 0.0, 0.0, 0.0),
            default_shininess=0.0,
            default_transparency=0.0,
            default_mode=Ms3dSpec.DEFAULT_MATERIAL_MODE,
            default_texture="",
            default_alphamap="",
            default_comment_object=None, # Ms3dComment
            ):
        if (default_name is None):
            default_name = ""

        if (default_texture is None):
            default_texture = ""

        if (default_alphamap is None):
            default_alphamap = ""

        self.name = default_name
        self._ambient = default_ambient
        self._diffuse = default_diffuse
        self._specular = default_specular
        self._emissive = default_emissive
        self.shininess = default_shininess
        self.transparency = default_transparency
        self.mode = default_mode
        self.texture = default_texture
        self.alphamap = default_alphamap

        if default_comment_object is None:
            default_comment_object = Ms3dCommentEx()
        self._comment_object = default_comment_object # Ms3dComment

    def __repr__(self):
        return "\n<name='{0}', ambient={1}, diffuse={2}, specular={3},"\
                " emissive={4}, shininess={5}, transparency={6}, mode={7},"\
                " texture='{8}', alphamap='{9}'>".format(
                self.name,
                self.ambient,
                self.diffuse,
                self.specular,
                self.emissive,
                self.shininess,
                self.transparency,
                self.mode,
                self.texture,
                self.alphamap
                )

    def __hash__(self):
        return (hash(self.name)

                ^ hash(self.ambient)
                ^ hash(self.diffuse)
                ^ hash(self.specular)
                ^ hash(self.emissive)

                ^ hash(self.shininess)
                ^ hash(self.transparency)
                ^ hash(self.mode)

                ^ hash(self.texture)
                ^ hash(self.alphamap)
                )

    def __eq__(self, other):
        return ((self.name == other.name)

                and (self.ambient == other.ambient)
                and (self.diffuse == other.diffuse)
                and (self.specular == other.specular)
                and (self.emissive == other.emissive)

                and (self.shininess == other.shininess)
                and (self.transparency == other.transparency)
                and (self.mode == other.mode)

                #and (self.texture == other.texture)
                #and (self.alphamap == other.alphamap)
                )


    @property
    def ambient(self):
        return self._ambient

    @property
    def diffuse(self):
        return self._diffuse

    @property
    def specular(self):
        return self._specular

    @property
    def emissive(self):
        return self._emissive

    @property
    def comment_object(self):
        return self._comment_object


    def read(self, file):
        self.name = Ms3dIo.read_string(file, Ms3dIo.LENGTH_NAME)
        self._ambient = Ms3dIo.read_array(file, Ms3dIo.read_float, 4)
        self._diffuse = Ms3dIo.read_array(file, Ms3dIo.read_float, 4)
        self._specular = Ms3dIo.read_array(file, Ms3dIo.read_float, 4)
        self._emissive = Ms3dIo.read_array(file, Ms3dIo.read_float, 4)
        self.shininess = Ms3dIo.read_float(file)
        self.transparency = Ms3dIo.read_float(file)
        self.mode = Ms3dIo.read_sbyte(file)
        self.texture = Ms3dIo.read_string(file, Ms3dIo.LENGTH_FILENAME)
        self.alphamap = Ms3dIo.read_string(file, Ms3dIo.LENGTH_FILENAME)
        return self

    def write(self, file):
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_NAME, self.name)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 4, self.ambient)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 4, self.diffuse)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 4, self.specular)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 4, self.emissive)
        Ms3dIo.write_float(file, self.shininess)
        Ms3dIo.write_float(file, self.transparency)
        Ms3dIo.write_sbyte(file, self.mode)
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_FILENAME, self.texture)
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_FILENAME, self.alphamap)


###############################################################################
class Ms3dRotationKeyframe:
    """ Ms3dRotationKeyframe """
    __slots__ = (
            'time',
            '_rotation',
            )

    def __init__(
            self,
            default_time=0.0,
            default_rotation=(0.0, 0.0, 0.0)
            ):
        self.time = default_time
        self._rotation = default_rotation

    def __repr__(self):
        return "\n<time={0}, rotation={1}>".format(
                self.time,
                self.rotation,
                )


    @property
    def rotation(self):
        return self._rotation


    def read(self, file):
        self.time = Ms3dIo.read_float(file)
        self._rotation = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        return self

    def write(self, file):
        Ms3dIo.write_float(file, self.time)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.rotation)


###############################################################################
class Ms3dTranslationKeyframe:
    """ Ms3dTranslationKeyframe """
    __slots__ = (
            'time',
            '_position',
            )

    def __init__(
            self,
            default_time=0.0,
            default_position=(0.0, 0.0, 0.0)
            ):
        self.time = default_time
        self._position = default_position

    def __repr__(self):
        return "\n<time={0}, position={1}>".format(
                self.time,
                self.position,
                )


    @property
    def position(self):
        return self._position


    def read(self, file):
        self.time = Ms3dIo.read_float(file)
        self._position = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        return self

    def write(self, file):
        Ms3dIo.write_float(file, self.time)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.position)


###############################################################################
class Ms3dJoint:
    """ Ms3dJoint """
    """
    __slots__ was taking out,
    to be able to inject additional attributes during runtime
    __slots__ = (
            'flags',
            'name',
            'parent_name',
            '_rotation',
            '_position',
            '_rotation_keyframes',
            '_translation_keyframes',
            '_joint_ex_object', # Ms3dJointEx
            '_comment_object', # Ms3dComment
            )
    """

    def __init__(
            self,
            default_flags=Ms3dSpec.DEFAULT_FLAGS,
            default_name="",
            default_parent_name="",
            default_rotation=(0.0, 0.0, 0.0),
            default_position=(0.0, 0.0, 0.0),
            default_rotation_keyframes=None,
            default_translation_keyframes=None,
            default_joint_ex_object=None, # Ms3dJointEx
            default_comment_object=None, # Ms3dComment
            ):
        if (default_name is None):
            default_name = ""

        if (default_parent_name is None):
            default_parent_name = ""

        if (default_rotation_keyframes is None):
            default_rotation_keyframes = [] #Ms3dRotationKeyframe()

        if (default_translation_keyframes is None):
            default_translation_keyframes = [] #Ms3dTranslationKeyframe()

        self.flags = default_flags
        self.name = default_name
        self.parent_name = default_parent_name
        self._rotation = default_rotation
        self._position = default_position
        self._rotation_keyframes = default_rotation_keyframes
        self._translation_keyframes = default_translation_keyframes

        if default_comment_object is None:
            default_comment_object = Ms3dCommentEx()
        self._comment_object = default_comment_object # Ms3dComment

        if default_joint_ex_object is None:
            default_joint_ex_object = Ms3dJointEx()
        self._joint_ex_object = default_joint_ex_object # Ms3dJointEx

    def __repr__(self):
        return "\n<flags={0}, name='{1}', parent_name='{2}', rotation={3},"\
                " position={4}, number_rotation_keyframes={5},"\
                " number_translation_keyframes={6},"\
                " rotation_key_frames={7}, translation_key_frames={8}>".format(
                self.flags,
                self.name,
                self.parent_name,
                self.rotation,
                self.position,
                self.number_rotation_keyframes,
                self.number_translation_keyframes,
                self.rotation_key_frames,
                self.translation_key_frames
                )


    @property
    def rotation(self):
        return self._rotation

    @property
    def position(self):
        return self._position

    @property
    def number_rotation_keyframes(self):
        if self.rotation_key_frames is None:
            return 0
        return len(self.rotation_key_frames)

    @property
    def number_translation_keyframes(self):
        if self.translation_key_frames is None:
            return 0
        return len(self.translation_key_frames)

    @property
    def rotation_key_frames(self):
        return self._rotation_keyframes

    @property
    def translation_key_frames(self):
        return self._translation_keyframes


    @property
    def joint_ex_object(self):
        return self._joint_ex_object


    @property
    def comment_object(self):
        return self._comment_object


    def read(self, file):
        self.flags = Ms3dIo.read_byte(file)
        self.name = Ms3dIo.read_string(file, Ms3dIo.LENGTH_NAME)
        self.parent_name = Ms3dIo.read_string(file, Ms3dIo.LENGTH_NAME)
        self._rotation = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        self._position = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        _number_rotation_keyframes = Ms3dIo.read_word(file)
        _number_translation_keyframes = Ms3dIo.read_word(file)
        self._rotation_keyframes = []
        for i in range(_number_rotation_keyframes):
            self.rotation_key_frames.append(Ms3dRotationKeyframe().read(file))
        self._translation_keyframes = []
        for i in range(_number_translation_keyframes):
            self.translation_key_frames.append(
                    Ms3dTranslationKeyframe().read(file))
        return self

    def write(self, file):
        Ms3dIo.write_byte(file, self.flags)
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_NAME, self.name)
        Ms3dIo.write_string(file, Ms3dIo.LENGTH_NAME, self.parent_name)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.rotation)
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.position)
        Ms3dIo.write_word(file, self.number_rotation_keyframes)
        Ms3dIo.write_word(file, self.number_translation_keyframes)
        for i in range(self.number_rotation_keyframes):
            self.rotation_key_frames[i].write(file)
        for i in range(self.number_translation_keyframes):
            self.translation_key_frames[i].write(file)


###############################################################################
class Ms3dCommentEx:
    """ Ms3dCommentEx """
    __slots__ = (
            'index',
            'comment',
            )

    def __init__(
            self,
            default_index=0,
            default_comment=""
            ):
        if (default_comment is None):
            default_comment = ""

        self.index = default_index
        self.comment = default_comment

    def __repr__(self):
        return "\n<index={0}, comment_length={1}, comment={2}>".format(
                self.index,
                self.comment_length,
                self.comment
                )


    @property
    def comment_length(self):
        if self.comment is None:
            return 0
        return len(self.comment)


    def read(self, file):
        self.index = Ms3dIo.read_dword(file)
        _comment_length = Ms3dIo.read_dword(file)
        self.comment = Ms3dIo.read_string(file, _comment_length)
        return self

    def write(self, file):
        Ms3dIo.write_dword(file, self.index)
        Ms3dIo.write_dword(file, self.comment_length)
        Ms3dIo.write_string(file, self.comment_length, self.comment)


###############################################################################
class Ms3dComment:
    """ Ms3dComment """
    __slots__ = (
            'comment',
            )

    def __init__(
            self,
            default_comment=""
            ):
        if (default_comment is None):
            default_comment = ""

        self.comment = default_comment

    def __repr__(self):
        return "\n<comment_length={0}, comment={1}>".format(
                self.comment_length,
                self.comment
                )


    @property
    def comment_length(self):
        if self.comment is None:
            return 0
        return len(self.comment)


    def read(self, file):
        _comment_length = Ms3dIo.read_dword(file)
        self.comment = Ms3dIo.read_string(file, _comment_length)
        return self

    def write(self, file):
        Ms3dIo.write_dword(file, self.comment_length)
        Ms3dIo.write_string(file, self.comment_length, self.comment)


###############################################################################
class Ms3dVertexEx1:
    """ Ms3dVertexEx1 """
    __slots__ = (
            '_bone_ids',
            '_weights',
            )

    def __init__(
            self,
            default_bone_ids=(
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID),
            default_weights=(0, 0, 0)
            ):
        self._bone_ids = default_bone_ids
        self._weights = default_weights

    def __repr__(self):
        return "\n<bone_ids={0}, weights={1}>".format(
                self.bone_ids,
                self.weights
                )


    @property
    def bone_ids(self):
        return self._bone_ids

    @property
    def weights(self):
        return self._weights


    @property
    def weight_bone_id(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights
        return 100

    @property
    def weight_bone_id0(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[0]
        return 0

    @property
    def weight_bone_id1(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[1]
        return 0

    @property
    def weight_bone_id2(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return 100 - (self._weights[0] + self._weights[1] \
                    + self._weights[2])
        return 0


    def read(self, file):
        self._bone_ids = Ms3dIo.read_array(file, Ms3dIo.read_sbyte, 3)
        self._weights = Ms3dIo.read_array(file, Ms3dIo.read_byte, 3)
        return self

    def write(self, file):
        Ms3dIo.write_array(file, Ms3dIo.write_sbyte, 3, self.bone_ids)
        Ms3dIo.write_array(file, Ms3dIo.write_byte, 3, self.weights)


###############################################################################
class Ms3dVertexEx2:
    """ Ms3dVertexEx2 """
    __slots__ = (
            'extra',
            '_bone_ids',
            '_weights',
            )

    def __init__(
            self,
            default_bone_ids=(
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID),
            default_weights=(0, 0, 0),
            default_extra=0
            ):
        self._bone_ids = default_bone_ids
        self._weights = default_weights
        self.extra = default_extra

    def __repr__(self):
        return "\n<bone_ids={0}, weights={1}, extra={2}>".format(
                self.bone_ids,
                self.weights,
                self.extra
                )


    @property
    def bone_ids(self):
        return self._bone_ids

    @property
    def weights(self):
        return self._weights


    @property
    def weight_bone_id(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights
        return 100

    @property
    def weight_bone_id0(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[0]
        return 0

    @property
    def weight_bone_id1(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[1]
        return 0

    @property
    def weight_bone_id2(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return 100 - (self._weights[0] + self._weights[1] \
                    + self._weights[2])
        return 0


    def read(self, file):
        self._bone_ids = Ms3dIo.read_array(file, Ms3dIo.read_sbyte, 3)
        self._weights = Ms3dIo.read_array(file, Ms3dIo.read_byte, 3)
        self.extra = Ms3dIo.read_dword(file)
        return self

    def write(self, file):
        Ms3dIo.write_array(file, Ms3dIo.write_sbyte, 3, self.bone_ids)
        Ms3dIo.write_array(file, Ms3dIo.write_byte, 3, self.weights)
        Ms3dIo.write_dword(file, self.extra)


###############################################################################
class Ms3dVertexEx3:
    """ Ms3dVertexEx3 """
    #char bone_ids[3]; // index of joint or -1, if -1, then that weight is
    #    ignored, since subVersion 1
    #byte weights[3]; // vertex weight ranging from 0 - 100, last weight is
    #    computed by 1.0 - sum(all weights), since subVersion 1
    #// weight[0] is the weight for bone_id in Ms3dVertex
    #// weight[1] is the weight for bone_ids[0]
    #// weight[2] is the weight for bone_ids[1]
    #// 1.0f - weight[0] - weight[1] - weight[2] is the weight for bone_ids[2]
    #unsigned int extra; // vertex extra, which can be used as color or
    #    anything else, since subVersion 2
    __slots__ = (
            'extra',
            '_bone_ids',
            '_weights',
            )

    def __init__(
            self,
            default_bone_ids=(
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID,
                    Ms3dSpec.DEFAULT_VERTEX_BONE_ID),
            default_weights=(0, 0, 0),
            default_extra=0
            ):
        self._bone_ids = default_bone_ids
        self._weights = default_weights
        self.extra = default_extra

    def __repr__(self):
        return "\n<bone_ids={0}, weights={1}, extra={2}>".format(
                self.bone_ids,
                self.weights,
                self.extra
                )


    @property
    def bone_ids(self):
        return self._bone_ids

    @property
    def weights(self):
        return self._weights


    @property
    def weight_bone_id(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights
        return 100

    @property
    def weight_bone_id0(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[0]
        return 0

    @property
    def weight_bone_id1(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return self._weights[1]
        return 0

    @property
    def weight_bone_id2(self):
        if self._weights[0] or self._weights[1] or self._weights[2]:
            return 100 - (self._weights[0] + self._weights[1] \
                    + self._weights[2])
        return 0


    def read(self, file):
        self._bone_ids = Ms3dIo.read_array(file, Ms3dIo.read_sbyte, 3)
        self._weights = Ms3dIo.read_array(file, Ms3dIo.read_byte, 3)
        self.extra = Ms3dIo.read_dword(file)
        return self

    def write(self, file):
        Ms3dIo.write_array(file, Ms3dIo.write_sbyte, 3, self.bone_ids)
        Ms3dIo.write_array(file, Ms3dIo.write_byte, 3, self.weights)
        Ms3dIo.write_dword(file, self.extra)


###############################################################################
class Ms3dJointEx:
    """ Ms3dJointEx """
    __slots__ = (
            '_color',
            )

    def __init__(
            self,
            default_color=(0.0, 0.0, 0.0)
            ):
        self._color = default_color

    def __repr__(self):
        return "\n<color={0}>".format(self.color)


    @property
    def color(self):
        return self._color


    def read(self, file):
        self._color = Ms3dIo.read_array(file, Ms3dIo.read_float, 3)
        return self

    def write(self, file):
        Ms3dIo.write_array(file, Ms3dIo.write_float, 3, self.color)


###############################################################################
class Ms3dModelEx:
    """ Ms3dModelEx """
    __slots__ = (
            'joint_size',
            'transparency_mode',
            'alpha_ref',
            )

    def __init__(
            self,
            default_joint_size=Ms3dSpec.DEFAULT_MODEL_JOINT_SIZE,
            default_transparency_mode\
                    =Ms3dSpec.DEFAULT_MODEL_TRANSPARENCY_MODE,
            default_alpha_ref=0.0
            ):
        self.joint_size = default_joint_size
        self.transparency_mode = default_transparency_mode
        self.alpha_ref = default_alpha_ref

    def __repr__(self):
        return "\n<joint_size={0}, transparency_mode={1}, alpha_ref={2}>".format(
                self.joint_size,
                self.transparency_mode,
                self.alpha_ref
                )

    def read(self, file):
        self.joint_size = Ms3dIo.read_float(file)
        self.transparency_mode = Ms3dIo.read_dword(file)
        self.alpha_ref = Ms3dIo.read_float(file)
        return self

    def write(self, file):
        Ms3dIo.write_float(file, self.joint_size)
        Ms3dIo.write_dword(file, self.transparency_mode)
        Ms3dIo.write_float(file, self.alpha_ref)


###############################################################################
#
# file format
#
###############################################################################
class Ms3dModel:
    """ Ms3dModel """
    __slot__ = (
            'header',
            'animation_fps',
            'current_time',
            'number_total_frames',
            'sub_version_comments',
            'sub_version_vertex_extra',
            'sub_version_joint_extra',
            'sub_version_model_extra',
            'name',
            '_vertices',
            '_triangles',
            '_groups',
            '_materials',
            '_joints',
            '_has_model_comment',
            '_comment_object', # Ms3dComment
            '_model_ex_object', # Ms3dModelEx
            )

    def __init__(
            self,
            default_name=""
            ):
        if (default_name is None):
            default_name = ""

        self.name = default_name

        self.animation_fps = Ms3dSpec.DEFAULT_MODEL_ANIMATION_FPS
        self.current_time = 0.0
        self.number_total_frames = 0
        self.sub_version_comments \
                = Ms3dSpec.DEFAULT_MODEL_SUB_VERSION_COMMENTS
        self.sub_version_vertex_extra \
                = Ms3dSpec.DEFAULT_MODEL_SUB_VERSION_VERTEX_EXTRA
        self.sub_version_joint_extra \
                = Ms3dSpec.DEFAULT_MODEL_SUB_VERSION_JOINT_EXTRA
        self.sub_version_model_extra \
                = Ms3dSpec.DEFAULT_MODEL_SUB_VERSION_MODEL_EXTRA

        self._vertices = [] #Ms3dVertex()
        self._triangles = [] #Ms3dTriangle()
        self._groups = [] #Ms3dGroup()
        self._materials = [] #Ms3dMaterial()
        self._joints = [] #Ms3dJoint()

        self.header = Ms3dHeader()
        self._model_ex_object = Ms3dModelEx()
        self._comment_object = None #Ms3dComment()


    @property
    def number_vertices(self):
        if self.vertices is None:
            return 0
        return len(self.vertices)

    @property
    def vertices(self):
        return self._vertices


    @property
    def number_triangles(self):
        if self.triangles is None:
            return 0
        return len(self.triangles)

    @property
    def triangles(self):
        return self._triangles


    @property
    def number_groups(self):
        if self.groups is None:
            return 0
        return len(self.groups)

    @property
    def groups(self):
        return self._groups


    @property
    def number_materials(self):
        if self.materials is None:
            return 0
        return len(self.materials)

    @property
    def materials(self):
        return self._materials


    @property
    def number_joints(self):
        if self.joints is None:
            return 0
        return len(self.joints)

    @property
    def joints(self):
        return self._joints


    @property
    def number_group_comments(self):
        if self.groups is None:
            return 0
        number = 0
        for item in self.groups:
            if item.comment_object is not None and item.comment_object.comment:
                number += 1
        return number

    @property
    def group_comments(self):
        if self.groups is None:
            return None
        items = []
        for item in self.groups:
            if item.comment_object is not None and item.comment_object.comment:
                items.append(item)
        return items


    @property
    def number_material_comments(self):
        if self.materials is None:
            return 0
        number = 0
        for item in self.materials:
            if item.comment_object is not None and item.comment_object.comment:
                number += 1
        return number

    @property
    def material_comments(self):
        if self.materials is None:
            return None
        items = []
        for item in self.materials:
            if item.comment_object is not None and item.comment_object.comment:
                items.append(item)
        return items


    @property
    def number_joint_comments(self):
        if self.joints is None:
            return 0
        number = 0
        for item in self.joints:
            if item.comment_object is not None and item.comment_object.comment:
                number += 1
        return number

    @property
    def joint_comments(self):
        if self.joints is None:
            return None
        items = []
        for item in self.joints:
            if item.comment_object is not None and item.comment_object.comment:
                items.append(item)
        return items


    @property
    def has_model_comment(self):
        if self.comment_object is not None and self.comment_object.comment:
            return 1
        return 0

    @property
    def comment_object(self):
        return self._comment_object


    @property
    def vertex_ex(self):
        if not self.sub_version_vertex_extra:
            return None
        return [item.vertex_ex_object for item in self.vertices]

    @property
    def joint_ex(self):
        if not self.sub_version_joint_extra:
            return None
        return [item.joint_ex_object for item in self.joints]

    @property
    def model_ex_object(self):
        if not self.sub_version_model_extra:
            return None
        return self._model_ex_object


    def print_internal(self):
        print()
        print("##############################################################")
        print("## the internal data of Ms3dModel object...")
        print("##")

        print("header={0}".format(self.header))

        print("number_vertices={0}".format(self.number_vertices))
        print("vertices=[", end="")
        if self.vertices:
            for obj in self.vertices:
                print("{0}".format(obj), end="")
        print("]")

        print("number_triangles={0}".format(self.number_triangles))
        print("triangles=[", end="")
        if self.triangles:
            for obj in self.triangles:
                print("{0}".format(obj), end="")
        print("]")

        print("number_groups={0}".format(self.number_groups))
        print("groups=[", end="")
        if self.groups:
            for obj in self.groups:
                print("{0}".format(obj), end="")
        print("]")

        print("number_materials={0}".format(self.number_materials))
        print("materials=[", end="")
        if self.materials:
            for obj in self.materials:
                print("{0}".format(obj), end="")
        print("]")

        print("animation_fps={0}".format(self.animation_fps))
        print("current_time={0}".format(self.current_time))
        print("number_total_frames={0}".format(self.number_total_frames))

        print("number_joints={0}".format(self.number_joints))
        print("joints=[", end="")
        if self.joints:
            for obj in self.joints:
                print("{0}".format(obj), end="")
        print("]")

        print("sub_version_comments={0}".format(self.sub_version_comments))

        print("number_group_comments={0}".format(self.number_group_comments))
        print("group_comments=[", end="")
        if self.group_comments:
            for obj in self.group_comments:
                print("{0}".format(obj), end="")
        print("]")

        print("number_material_comments={0}".format(
                self.number_material_comments))
        print("material_comments=[", end="")
        if self.material_comments:
            for obj in self.material_comments:
                print("{0}".format(obj), end="")
        print("]")

        print("number_joint_comments={0}".format(self.number_joint_comments))
        print("joint_comments=[", end="")
        if self.joint_comments:
            for obj in self.joint_comments:
                print("{0}".format(obj), end="")
        print("]")

        print("has_model_comment={0}".format(self.has_model_comment))
        print("model_comment={0}".format(self.comment_object))

        print("sub_version_vertex_extra={0}".format(
                self.sub_version_vertex_extra))
        print("vertex_ex={0}".format(self.vertex_ex))

        print("sub_version_joint_extra={0}".format(
                self.sub_version_joint_extra))
        print("joint_ex={0}".format(self.joint_ex))

        print("sub_version_model_extra={0}".format(
                self.sub_version_model_extra))
        print("model_ex={0}".format(self.model_ex_object))

        print("##")
        print("## ...end")
        print("##############################################################")
        print()


    def read(self, file):
        """
        opens, reads and pars MS3D file.
        add content to blender scene
        """

        self.header.read(file)
        if (self.header != Ms3dHeader()):
            print("\nwarning, invalid file header")

        _number_vertices = Ms3dIo.read_word(file)
        if (_number_vertices > Ms3dSpec.MAX_VERTICES):
            print("\nwarning, invalid count: number_vertices: {}".format(
                    _number_vertices))
        self._vertices = []
        for i in range(_number_vertices):
            self.vertices.append(Ms3dVertex().read(file))

        _number_triangles = Ms3dIo.read_word(file)
        if (_number_triangles > Ms3dSpec.MAX_TRIANGLES):
            print("\nwarning, invalid count: number_triangles: {}".format(
                    _number_triangles))
        self._triangles = []
        for i in range(_number_triangles):
            self.triangles.append(Ms3dTriangle().read(file))

        _number_groups = Ms3dIo.read_word(file)
        if (_number_groups > Ms3dSpec.MAX_GROUPS):
            print("\nwarning, invalid count: number_groups: {}".format(
                    _number_groups))
        self._groups = []
        for i in range(_number_groups):
            self.groups.append(Ms3dGroup().read(file))

        _number_materials = Ms3dIo.read_word(file)
        if (_number_materials > Ms3dSpec.MAX_MATERIALS):
            print("\nwarning, invalid count: number_materials: {}".format(
                    _number_materials))
        self._materials = []
        for i in range(_number_materials):
            self.materials.append(Ms3dMaterial().read(file))

        self.animation_fps = Ms3dIo.read_float(file)
        self.current_time = Ms3dIo.read_float(file)
        self.number_total_frames = Ms3dIo.read_dword(file)

        _progress = set()

        try:
            # optional data
            # doesn't matter if doesn't existing.

            Ms3dIo.raise_on_eof(file)

            _number_joints = Ms3dIo.read_word(file)
            if (_number_joints > Ms3dSpec.MAX_JOINTS):
                print("\nwarning, invalid count: number_joints: {}".format(
                        _number_joints))
            self._joints = []
            for i in range(_number_joints):
                self.joints.append(Ms3dJoint().read(file))
            _progress.add('JOINTS')

            Ms3dIo.raise_on_eof(file)

            self.sub_version_comments = Ms3dIo.read_dword(file)
            _number_group_comments = Ms3dIo.read_dword(file)
            if (_number_group_comments > Ms3dSpec.MAX_GROUPS):
                print("\nwarning, invalid count:"\
                        " number_group_comments: {}".format(
                        _number_group_comments))
            if _number_group_comments > _number_groups:
                print("\nwarning, invalid count:"\
                        " number_group_comments: {}, number_groups: {}".format(
                        _number_group_comments, _number_groups))
            for i in range(_number_group_comments):
                item = Ms3dCommentEx().read(file)
                if item.index >= 0 and item.index < _number_groups:
                    self.groups[item.index]._comment_object = item
                else:
                    print("\nwarning, invalid index:"\
                            " group_index: {}, number_groups: {}".format(
                            item.index, _number_groups))
            _progress.add('GROUP_COMMENTS')

            _number_material_comments = Ms3dIo.read_dword(file)
            if (_number_material_comments > Ms3dSpec.MAX_MATERIALS):
                print("\nwarning, invalid count:"\
                        " number_material_comments: {}".format(
                        _number_material_comments))
            if _number_material_comments > _number_materials:
                print("\nwarning, invalid count:"\
                        " number_material_comments:"\
                        " {}, number_materials: {}".format(
                        _number_material_comments, _number_materials))
            for i in range(_number_material_comments):
                item = Ms3dCommentEx().read(file)
                if item.index >= 0 and item.index < _number_materials:
                    self.materials[item.index]._comment_object = item
                else:
                    print("\nwarning, invalid index:"\
                            " material_index: {}, number_materials:"\
                            " {}".format(item.index, _number_materials))
            _progress.add('MATERIAL_COMMENTS')

            _number_joint_comments = Ms3dIo.read_dword(file)
            if (_number_joint_comments > Ms3dSpec.MAX_JOINTS):
                print("\nwarning, invalid count:"\
                        " number_joint_comments: {}".format(
                        _number_joint_comments))
            if _number_joint_comments > _number_joints:
                print("\nwarning, invalid count:"\
                        " number_joint_comments: {}, number_joints: {}".format(
                        _number_joint_comments, _number_joints))
            for i in range(_number_joint_comments):
                item = Ms3dCommentEx().read(file)
                if item.index >= 0 and item.index < _number_joints:
                    self.joints[item.index]._comment_object = item
                else:
                    print("\nwarning, invalid index:"\
                            " joint_index: {}, number_joints: {}".format(
                            item.index, _number_joints))
            _progress.add('JOINT_COMMENTS')

            _has_model_comment = Ms3dIo.read_dword(file)
            if (_has_model_comment != 0):
                self._comment_object = Ms3dComment().read(file)
            else:
                self._comment_object = None
            _progress.add('MODEL_COMMENTS')

            Ms3dIo.raise_on_eof(file)

            self.sub_version_vertex_extra = Ms3dIo.read_dword(file)
            if self.sub_version_vertex_extra > 0:
                length = len(self.joints)
                for i in range(_number_vertices):
                    if self.sub_version_vertex_extra == 1:
                        item = Ms3dVertexEx1()
                    elif self.sub_version_vertex_extra == 2:
                        item = Ms3dVertexEx2()
                    elif self.sub_version_vertex_extra == 3:
                        item = Ms3dVertexEx3()
                    else:
                        print("\nwarning, invalid version:"\
                                " sub_version_vertex_extra: {}".format(
                                sub_version_vertex_extra))
                        continue
                    self.vertices[i]._vertex_ex_object = item.read(file)
            _progress.add('VERTEX_EXTRA')

            Ms3dIo.raise_on_eof(file)

            self.sub_version_joint_extra = Ms3dIo.read_dword(file)
            if self.sub_version_joint_extra > 0:
                for i in range(_number_joints):
                    self.joints[i]._joint_ex_object = Ms3dJointEx().read(file)
            _progress.add('JOINT_EXTRA')

            Ms3dIo.raise_on_eof(file)

            self.sub_version_model_extra = Ms3dIo.read_dword(file)
            if self.sub_version_model_extra > 0:
                self._model_ex_object.read(file)
            _progress.add('MODEL_EXTRA')

        except EOF:
            # reached end of optional data.
            print("Ms3dModel.read - optional data read: {}".format(_progress))
            pass

        except Exception:
            type, value, traceback = exc_info()
            print("Ms3dModel.read - exception in optional try block,"
                    " _progress={0}\n  type: '{1}'\n  value: '{2}'".format(
                    _progress, type, value, traceback))

        else:
            pass

        # try best to continue far as possible
        if not 'JOINTS' in _progress:
            _number_joints = 0
            self._joints = []

        if not 'GROUP_COMMENTS' in _progress:
            self.sub_version_comments = 0
            _number_group_comments = 0

        if not 'MATERIAL_COMMENTS' in _progress:
            _number_material_comments = 0

        if not 'JOINT_COMMENTS' in _progress:
            _number_joint_comments = 0

        if not 'MODEL_COMMENTS' in _progress:
            _has_model_comment = 0
            self._comment_object = None # Ms3dComment()

        if not 'VERTEX_EXTRA' in _progress:
            self.sub_version_vertex_extra = 0

        if not 'JOINT_EXTRA' in _progress:
            self.sub_version_joint_extra = 0

        if not 'MODEL_EXTRA' in _progress:
            self.sub_version_model_extra = 0
            self._model_ex_object = Ms3dModelEx()

        return


    def write(self, file):
        """
        add blender scene content to MS3D
        creates, writes MS3D file.
        """

        self.header.write(file)

        Ms3dIo.write_word(file, self.number_vertices)
        for i in range(self.number_vertices):
            self.vertices[i].write(file)

        Ms3dIo.write_word(file, self.number_triangles)
        for i in range(self.number_triangles):
            self.triangles[i].write(file)

        Ms3dIo.write_word(file, self.number_groups)
        for i in range(self.number_groups):
            self.groups[i].write(file)

        Ms3dIo.write_word(file, self.number_materials)
        for i in range(self.number_materials):
            self.materials[i].write(file)

        Ms3dIo.write_float(file, self.animation_fps)
        Ms3dIo.write_float(file, self.current_time)
        Ms3dIo.write_dword(file, self.number_total_frames)

        try:
            # optional part
            # doesn't matter if it doesn't complete.
            Ms3dIo.write_word(file, self.number_joints)
            for i in range(self.number_joints):
                self.joints[i].write(file)

            Ms3dIo.write_dword(file, self.sub_version_comments)

            Ms3dIo.write_dword(file, self.number_group_comments)
            for i in range(self.number_group_comments):
                self.group_comments[i].write(file)

            Ms3dIo.write_dword(file, self.number_material_comments)
            for i in range(self.number_material_comments):
                self.material_comments[i].write(file)

            Ms3dIo.write_dword(file, self.number_joint_comments)
            for i in range(self.number_joint_comments):
                self.joint_comments[i].write(file)

            Ms3dIo.write_dword(file, self.has_model_comment)
            if (self.has_model_comment != 0):
                self.comment_object.write(file)

            Ms3dIo.write_dword(file, self.sub_version_vertex_extra)
            if (self.sub_version_vertex_extra in {1, 2, 3}):
                for i in range(self.number_vertices):
                    self.vertex_ex[i].write(file)

            Ms3dIo.write_dword(file, self.sub_version_joint_extra)
            for i in range(self.number_joints):
                self.joint_ex[i].write(file)

            Ms3dIo.write_dword(file, self.sub_version_model_extra)
            self.model_ex_object.write(file)

        except Exception:
            type, value, traceback = exc_info()
            print("Ms3dModel.write - exception in optional try block"
                    "\n  type: '{0}'\n  value: '{1}'".format(
                    type, value, traceback))
            pass

        else:
            pass

        return


    def is_valid(self):
        valid = True
        result = []

        format1 = "\n  number of {0}: {1}"
        format2 = " limit exceeded! (limit is {0})"

        result.append("MS3D statistics:")
        result.append(format1.format("vertices ........",
                self.number_vertices))
        if (self.number_vertices > Ms3dSpec.MAX_VERTICES):
            result.append(format2.format(Ms3dSpec.MAX_VERTICES))
            valid &= False

        result.append(format1.format("triangles .......",
                self.number_triangles))
        if (self.number_triangles > Ms3dSpec.MAX_TRIANGLES):
            result.append(format2.format(Ms3dSpec.MAX_TRIANGLES))
            valid &= False

        result.append(format1.format("groups ..........",
                self.number_groups))
        if (self.number_groups > Ms3dSpec.MAX_GROUPS):
            result.append(format2.format(Ms3dSpec.MAX_GROUPS))
            valid &= False

        result.append(format1.format("materials .......",
                self.number_materials))
        if (self.number_materials > Ms3dSpec.MAX_MATERIALS):
            result.append(format2.format(Ms3dSpec.MAX_MATERIALS))
            valid &= False

        result.append(format1.format("joints ..........",
                self.number_joints))
        if (self.number_joints > Ms3dSpec.MAX_JOINTS):
            result.append(format2.format(Ms3dSpec.MAX_JOINTS))
            valid &= False

        result.append(format1.format("model comments ..",
                self.has_model_comment))
        result.append(format1.format("group comments ..",
                self.number_group_comments))
        result.append(format1.format("material comments",
                self.number_material_comments))
        result.append(format1.format("joint comments ..",
                self.number_joint_comments))

        #if (not valid):
        #    result.append("\n\nthe data may be corrupted.")

        return (valid, ("".join(result)))


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
