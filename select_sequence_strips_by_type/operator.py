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

import bpy

def main(context, select_types, deselect):
    # Simply check all strips in the sequencer and select those of given type(s)
    # and not yet selected…
    # If deselect is True, remove them from selection instead!
    for seq in context.sequences:
        if seq.type in select_types:
            if not deselect and not seq.select: seq.select = True
            elif seq.select: seq.select = False

from bpy.props import BoolProperty, StringProperty

class SelectSequenceStripsByType(bpy.types.Operator):
    '''
    (De)select sequence strips by type.
    '''
    bl_idname = "sequencer.select_by_type"
    bl_label = "Propagate Render Settings"
    # Enable undo…
    bl_options = {'REGISTER', 'UNDO'}

    # TODO: learn CollectionProperty to see whether it is possible to get
    #       directly a set of strings…
    # For now, list of types separated by white spaces.
    select_types = StringProperty(name="Select Types",
                                  description="Type(s) of strip to select",
                                  default="")

    deselect = BoolProperty(name="Deselect",
                            description="Deselect strips instead of selecting "
                                       +"them.",
                            default=False)

    @classmethod
    def poll(cls, context):
        return context.scene.sequence_editor != None

    def execute(self, context):
        select_types = set(str(self.select_types).split())
        main(context, self.select_types, self.deselect)
        return {'FINISHED'}


if __name__ == "__main__":
    bpy.ops.sequencer.select_by_type()

