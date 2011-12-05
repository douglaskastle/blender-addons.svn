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

""" This script is an exporter to the nuke's .chan files.
It takes the currently active object and writes it's transformation data
into a text file with .chan extension."""

import bpy
from mathutils import Matrix, Euler
from math import radians, degrees, atan, atan2, tan


def save_chan(context, filepath, y_up, rot_ord):

    # get the active scene and object
    scene = context.scene
    obj = context.active_object

    # get the range of an animation
    f_start = scene.frame_start
    f_end = scene.frame_end

    # get the resolution (needed by nuke)
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    res_ratio = res_y / res_x

    # prepare the correcting matrix
    rot_mat = Matrix.Rotation(radians(-90.0), 4, 'X').to_4x4()

    filehandle = open(filepath, 'w')
    fw = filehandle.write

    # iterate the frames
    for frame in range(f_start, f_end, 1):

        # set the current frame
        scene.frame_set(frame)

        # get the objects world matrix
        mat = obj.matrix_world.copy()

        # if the setting is proper use the rotation matrix
        # to flip the Z and Y axis
        if y_up:
            mat = rot_mat * mat

        # create the first component of a new line, the frame number
        fw("%i\t" % frame)

        # create transform component
        t = mat.to_translation()
        fw("%f\t%f\t%f\t" % t[:])

        # create rotation component
        r = mat.to_euler(rot_ord)

        fw("%f\t%f\t%f\t" % (degrees(r[0]), degrees(r[1]), degrees(r[2])))

        # if we have a camera, add the focal length
        if obj.type == 'CAMERA':
            # I've found via the experiments that this is a blenders 
            # default sensor size (in mm)
            sensor_x = 32.0
            # the vertical sensor size we get by multiplying the sensor_x by
            # resolution ratio
            sensor_y = sensor_x * res_ratio
            cam_lens = obj.data.lens
            # calculate the vertical field of view
            # we know the vertical size of (virtual) sensor, the focal length
            # of the camera so all we need to do is to feed this data to
            # atan2 function whitch returns the degree (in radians) of 
            # an angle formed by a triangle with two legs of a given lengths
            vfov = degrees(atan2(sensor_y / 2, cam_lens))*2
            fw("%f" % vfov)

        fw("\n")

    # after the whole loop close the file
    filehandle.close()

    return {'FINISHED'}
