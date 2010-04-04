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

"""
This script imports images and creates Planes with them as textures.
At the moment the naming for objects, materials, textures and meshes
is derived from the imagename.

One can either import a single image, or all images in one directory.
When imporing a directory one can either check the checkbox or leave
the filename empty.

As a bonus one can choose to import images of only one type.
Atm this is the list of possible extensions:
extList =
    ('jpeg', 'jpg', 'png', 'tga', 'tiff', 'tif', 'exr',
    'hdr', 'avi', 'mov', 'mp4', 'ogg', 'bmp', 'cin', 'dpx', 'psd')

If someone knows a better way of telling if a file is an image which
Blender can read, please tell so ;)

when importing images that are allready referenced they are not
reimported but the old ones reused as not to clutter the materials,
textures and image lists.
Instead the plane gets linked against an existing material.

If one reimports images but chooses different material/texture mapping
new materials are created.
So one doesn't has to go through everything if one decides differently
after importing 236 images.

"""

##############################################################################
##############################################################################
##############################################################################

bl_addon_info = {
    'name': 'Planes from Images',
    'author': 'Florian Meyer (testscreenings)',
    'version': '0.6',
    'blender': (2, 5, 2),
    'location': 'View3D > Add Mesh',
    'url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Object/Image_To_Planes',
    'description': 'Imports images and creates planes \
with the appropiate aspect ratio',
    'category': 'Object'}

##############################################################################
##############################################################################
##############################################################################

import bpy
from bpy.props import *
from os import listdir
from Mathutils import Vector

# Apply view rotation to objects if "Align To" for new objects
# was set to "VIEW" in the User Preference.
def apply_view_rotation(ob):
    context = bpy.context
    align = bpy.context.user_preferences.edit.object_align

    if (context.space_data.type == 'VIEW_3D'
        and align == 'VIEW'):
            view3d = context.space_data
            region = view3d.region_3d
            viewMatrix = region.view_matrix
            rot = viewMatrix.rotation_part()
            ob.rotation_euler = rot.invert().to_euler()



######################
#### Create plane ####
######################


#### gets called from createPlane ####
def createMesh(x):
    #### x is x-aspectRatio ####
    verts = []
    faces = []
    v1 = (-x, -1, 0)
    v2 = (x, -1, 0)
    v3 = (x, 1, 0)
    v4 = (-x, 1, 0)
    verts.append(v1)
    verts.append(v2)
    verts.append(v3)
    verts.append(v4)
    faces.append([0, 1, 2, 3])

    return verts, faces


def createPlane(name, aspect):
    scene = bpy.context.scene
    me = bpy.data.meshes.new(name)
    verts, faces = createMesh(aspect)
    me.from_pydata(verts, [], faces)
    plane = bpy.data.objects.new(name, me)
    plane.data.add_uv_texture()
    scene.objects.link(plane)
    plane.location = scene.cursor_location
    apply_view_rotation(plane)

    return plane


#######################################
#### get imagepaths from directory ####
#######################################

def getImageFilesInDirectory(directory, extension):
    import os

    extList = [
        'jpeg', 'jpg', 'png', 'tga', 'tiff',
        'tif', 'exr', 'hdr', 'avi', 'mov', 'mp4',
        'ogg', 'bmp', 'cin', 'dpx', 'psd']

    #### get all Files in the directory ####
    allFiles = listdir(directory)
    allImages = []

    # Convert to lower case
    e = extension.lower()

    if e in extList:
        extList = extension

    #### Put all ImageFiles in List and return ####
    for file in allFiles:
        # Get the file extension (includes the ".")
        e = os.path.splitext(file)[1]

        # Separate by "." and get the last list-entry.
        e = e.rpartition(".")[-1]

        # Convert to lower case
        e = e.lower()

        if e in extList:
            allImages.append(file)

    return allImages


##########################################
#### get ImageDataBlock from Filepath ####
##########################################

def getImage(path):
    img = []

    #### Check every Image if it is allready there ####
    for image in bpy.data.images:
        #### If image with same path exists take that one ####
        if image.filename == path:
            img = image

    #### Else create new Image and load from path ####
    if not img:
        name = path.rpartition('\\')[2].rpartition('.')[0]
        img = bpy.data.images.new(name)
        img.source = 'FILE'
        img.filename = path

    return img


#############################
#### Create/get Material ####
#############################
def getMaterial(tex, mapping):
    mat = []
    #### Check all existing Materials ####
    for material in bpy.data.materials:
        #### if Material with name and mapping        ####
        #### and texture with image                   ####
        #### exists take that one                     ####
        if (material.name == tex.image.name
        and tex.name in material.texture_slots
        and material.mapping == mapping):
            mat = material

    #### Else Create new one and apply mapping ####
    if not mat:
        mat = bpy.data.materials.new(name=tex.name)
        mat.add_texture(tex, texture_coordinates='UV', map_to='COLOR')
        mat.mapping = mapping
        mat.name = tex.name

    return mat


############################
#### Create/get Texture ####
############################

def getTexture(path, img):
    tex = []

    #### Check all existing Textures ####
    for texture in bpy.data.textures:
        #### if (image)texture with image exists take that one ####
        if (texture.type == 'IMAGE'
            and texture.image
            and texture.image.filename == path):
            tex = texture

    #### Else Create new one and apply mapping ####
    if not tex:
        name = path.rpartition('\\')[2].rpartition('.')[0]
        tex = bpy.data.textures.new(name=name)
        tex.type = 'IMAGE'
        tex = tex.recast_type()
        tex.image = img

    return tex


#########################################
#### Create custom Material Property ####
#########################################

def mapget(self):
    """custom property of the image_to_planes addon"""
    mapping = []
    mapping.append(self.shadeless)
    mapping.append(self.transparency)
    mapping.append(self.alpha)
    mapping.append(self.specular_alpha)
    mapping.append(self.transparency_method)
    if (self.texture_slots[0]
        and self.texture_slots[0].texture.type == 'IMAGE'
        and self.texture_slots[0].texture.image):
        mapping.append(self.texture_slots[0].texture.image.premultiply)
    else:
        mapping.append("no image")
    return mapping


def mapset(self, value):
    self.shadeless = value[0]
    self.transparency = value[1]
    self.alpha = float(value[2])
    self.specular_alpha = float(value[3])
    self.transparency_method = value[4]
    if (self.texture_slots[0]
        and self.texture_slots[0].texture.type == 'IMAGE'
        and self.texture_slots[0].texture.image):
        self.texture_slots[0].texture.image.premultiply = value[5]


bpy.types.Material.mapping = property(mapget, mapset)

#######################
#### MAIN FUNCTION ####
#######################


def main(filePath, options, mapping):
    #### Lists ####
    images = []
    scene = bpy.context.scene

    #### if Create from Directory (no filename or checkbox) ####
    if options[0] or not filePath[1]:
        imageFiles = getImageFilesInDirectory(filePath[2], options[1])
        #### Check if images are loaded and put in List ####
        for imageFile in imageFiles:
            img = getImage(str(filePath[2]) + "\\" + str(imageFile))
            images.append(img)

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        #### Assign/get all things ####
        for img in images:
            aspect = img.size[0] / img.size[1]

            #### Create/get Texture ####
            tex = getTexture(img.filename, img)

            #### Create/get Material ####
            mat = getMaterial(tex, mapping)

            #### Create Plane ####
            plane = createPlane(img.name, aspect)

            #### Assign Material ####
            plane.data.add_material(mat)

            scene.objects.active = plane

            #### put Image into  UVTextureLayer ####
            plane.data.uv_textures[0].data[0].image = img
            plane.data.uv_textures[0].data[0].tex = True
            plane.data.uv_textures[0].data[0].transp = 'ALPHA'
            plane.data.uv_textures[0].data[0].twoside = True

            plane.selected = True

    #### if Create Single Plane (filename and is image)####
    else:

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        #### Check if Image is loaded ####
        img = getImage(filePath[0])

        aspect = img.size[0] / img.size[1]

        #### Create/get Texture ####
        tex = getTexture(filePath[0], img)

        #### Create/get Material ####
        mat = getMaterial(tex, mapping)

        #### Create Plane ####
        plane = createPlane(img.name, aspect)

        #### Assign Material ####
        plane.data.add_material(mat)

        #### put Image into  UVTextureLayer ####
        plane.data.uv_textures[0].data[0].image = img
        plane.data.uv_textures[0].data[0].tex = True
        plane.data.uv_textures[0].data[0].transp = 'ALPHA'
        plane.data.uv_textures[0].data[0].twoside = True

        plane.selected = True


##############################################################################
#################       O P E R A T O R        ###############################
##############################################################################

class image_to_planes(bpy.types.Operator):
    ''''''
    bl_idname = "mesh.image_to_planes"
    bl_label = "Import Images as Planes"
    bl_description = "Create plane(s) from images"
    bl_options = {'REGISTER', 'UNDO'}

    path = StringProperty(name="File Path",
        description="File path used for importing the file",
        maxlen=1024,
        default="")
    filename = StringProperty(name="File Name",
        description="Name of the file.")
    directory = StringProperty(name="Directory",
        description="Directory of the file.")
    fromDirectory = BoolProperty(name="All in directory",
        description="Import all images in this directory",
        default=False)
    extension = StringProperty(name="Extension",
        description="Only import files with this extension " \
            "(e.g. png, jpg, ...")

    shadeless = BoolProperty(name="Shadeless",
        description="Set material to shadeless",
        default=False)
    transp = BoolProperty(name="Use alpha",
        description="Use alphachannel for transparency",
        default=False)
    premultiply = BoolProperty(name="Premultiply",
        description="Premultiply image",
        default=False)
    tEnum = [
        ('Z_TRANSPARENCY', 'Z_TRANSPARENCY', 'Z_TRANSPARENCY'),
        ('RAYTRACE', 'RAYTRACE', 'RAYTRACE')]
    transp_method = EnumProperty(items=tEnum,
        description="Transparency Method",
            name="transMethod")

#items=[(cats[i], cats[i], str(i)) for i in range(len(cats))

    def execute(self, context):
        #### File Path ####
        path = self.properties.path
        filename = self.properties.filename
        directory = self.properties.directory
        filePath = [path, filename, directory]
        #print(filePath)

        #### General Options ####
        fromDirectory = self.properties.fromDirectory
        extension = self.properties.extension
        options = [fromDirectory, extension]

        #### mapping ####
        alphavalue = 1
        shadeless = self.properties.shadeless
        transp = self.properties.transp
        if transp:
            alphavalue = 0
        transp_method = self.properties.transp_method
        premultiply = self.properties.premultiply

        mapping = ([shadeless,
                    transp,
                    alphavalue,
                    alphavalue,
                    transp_method,
                    premultiply])

        #### Call Main Function ####
        main(filePath, options, mapping)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.manager
        wm.add_fileselect(self)

        return {'RUNNING_MODAL'}


#### Registering ####

menu_func = (lambda self, context: self.layout.operator(image_to_planes.bl_idname,
                                        text="Imageplanes", icon='PLUGIN'))

def register():
    bpy.types.register(image_to_planes)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.unregister(image_to_planes)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
