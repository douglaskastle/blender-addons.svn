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
import math
from bpy.props import *

bl_addon_info = {
    'name': 'Render to Print',
    'author': 'Marco Crippa <thekrypt77@tiscali.it>',
    'version': (0,1),
    'blender': (2, 5, 4),
    'location': 'Render > Render to Print',
    'description': 'Set the size of the render for a print',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/'\
        'Scripts/Render/Render to Print',
    'tracker_url': 'https://projects.blender.org/tracker/index.php?'\
        'func=detail&aid=24219&group_id=153&atid=468',
    'category': 'Render'}

class RenderButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

class RENDER_PT_Print(RenderButtonsPanel, bpy.types.Panel):
    bl_label = "Render to Print"

    bpy.types.Scene.Preset = EnumProperty(
        name="Select preset",
        description="Select from preset",
        items=(
            ("custom_1_1", "custom", ""),
            ("A0_84.1_118.9", "A0 (84.1x118.9 cm)", ""),
            ("A1_59.4_84.1", "A1 (59.4x84.1 cm)", ""),
            ("A2_42.0_59.4", "A2 (42.0x59.4 cm)", ""),
            ("A3_29.7_42.0", "A3 (29.7 42.0 cm)", ""),
            ("A4_21.0_29.7", "A4 (21.0x29.7 cm)", ""),
            ("A5_14.8_21.0", "A5 (14.8x21.0 cm)", ""),
            ("A6_10.5_14.8", "A6 (10.5x14.8 cm)", ""),
            ("A7_7.4_10.5", "A7 (7.4x10.5 cm)", ""),
            ("A8_5.2_7.4", "A8 (5.2x7.4 cm)", ""),
            ("A9_3.7_5.2", "A9 (3.7x5.2 cm)", ""),
            ("A10_2.6_3.7", "A10 (2.6x3.7 cm)", ""),

            ("B0_100.0_141.4", "B0 (100.0x141.4 cm)", ""),
            ("B1_70.7_100.0", "B1 (70.7x100.0 cm)", ""),
            ("B2_50.0_70.7", "B2 (50.0x70.7 cm)", ""),
            ("B3_35.3_50.0", "B3 (35.3x50.0 cm)", ""),
            ("B4_25.0_35.3", "B4 (25.0x35.3 cm)", ""),
            ("B5_17.6_25.0", "B5 (17.6x25.0 cm)", ""),
            ("B6_12.5_17.6", "B6 (12.5x17.6 cm)", ""),
            ("B7_8.8_12.5", "B7 (8.8x12.5 cm)", ""),
            ("B8_6.2_8.8", "B8 (6.2x8.8 cm)", ""),
            ("B9_4.4_6.2", "B9 (4.4x6.2 cm)", ""),
            ("B10_3.1_4.4", "B10 (3.1x4.4 cm)", ""),

            ("C0_91.7_129.7", "C0 (91.7x129.7 cm)", ""),
            ("C1_64.8_91.7", "C1 (64.8x91.7 cm)", ""),
            ("C2_45.8_64.8", "C2 (45.8x64.8 cm)", ""),
            ("C3_32.4_45.8", "C3 (32.4x45.8 cm)", ""),
            ("C4_22.9_32.4", "C4 (22.9x32.4 cm)", ""),
            ("C5_16.2_22.9", "C5 (16.2x22.9 cm)", ""),
            ("C6_11.4_16.2", "C6 (11.4x16.2 cm)", ""),
            ("C7_8.1_11.4", "C7 (8.1x11.4 cm)", ""),
            ("C8_5.7_8.1", "C8 (5.7x8.1 cm)", ""),
            ("C9_4.0_5.7", "C9 (4.0x5.7 cm)", ""),
            ("C10_2.8_4.0", "C10 (2.8x4.0 cm)", ""),

            ("Letter_21.6_27.9", "Letter (21.6x27.9 cm)", ""),
            ("Legal_21.6_35.6", "Legal (21.6x35.6 cm)", ""),
            ("Legal junior_20.3_12.7", "Legal junior (20.3x12.7 cm)", ""),
            ("Ledger_43.2_27.9", "Ledger (43.2x27.9 cm)", ""),
            ("Tabloid_27.9_43.2", "Tabloid (27.9x43.2 cm)", ""),

            ("ANSI C_43.2_55.9", "ANSI C (43.2×55.9 cm)", ""),
            ("ANSI D_55.9_86.4", "ANSI D (55.9×86.4 cm)", ""),
            ("ANSI E_86.4_111.8", "ANSI E (86.4×111.8 cm)", ""),

            ("Arch A_22.9_30.5", "Arch A (22.9×30.5 cm)", ""),
            ("Arch B_30.5_45.7", "Arch B (30.5×45.7 cm)", ""),
            ("Arch C_45.7_61.0", "Arch C (45.7×61.0 cm)", ""),
            ("Arch D_61.0_91.4", "Arch D (61.0×91.4 cm)", ""),
            ("Arch E_91.4_121.9", "Arch E (91.4×121.9 cm)", ""),
            ("Arch E1_76.2_106.7", "Arch E1 (76.2×106.7 cm)", ""),
            ("Arch E2_66.0_96.5", "Arch E2 (66.0x96.5 cm)", ""),
            ("Arch E3_68.6_99.1", "Arch E3 (68.6x99.1 cm)", "")
        ),
        default="custom_1_1"
    )

    bpy.types.Scene.Orientation = EnumProperty(
        name="Set orientation", 
        description="Set orientation", 
        items=(
            ("Portrait", "Portrait", "Portrait"),
            ("Landscape", "Landscape", "Landscape")
        ),
        default="Portrait")

    bpy.types.Scene.From = EnumProperty(
        name="Set from",
        description="Set from",
        items=(
            ("Cm--->Pixel", "Cm--->Pixel", "Cm--->Pixel"),
            ("Pixel--->Cm", "Pixel--->Cm", "Pixel--->Cm")
        ),
        default="Cm--->Pixel")

    bpy.types.Scene.Width = FloatProperty(
        name = "Width",
        description = "Width",
        default = 5.0,
        min = 1.0,
        max = 100000.0)
    bpy.types.Scene.Height = FloatProperty(
        name = "Height",
        description = "Height",
        default = 3.0,
        min = 1.0,
        max = 100000.0)

    bpy.types.Scene.DPI = IntProperty(
        name = "DPI",
        description = "DPI",
        default = 300,
        min = 1,
        max = 100000)

    bpy.types.Scene.PWidth = IntProperty(
        name = "Pixel Width",
        description = "Pixel Width",
        default = 900,
        min = 4,
        max = 10000)
    bpy.types.Scene.PHeight = IntProperty(
        name = "Pixel Height",
        description = "Pixel Height",
        default = 600,
        min = 4,
        max = 10000)

    bpy.types.Scene.WInch = StringProperty(
        name = "Inch Width",
        description = "",
        default = "AAA")
    bpy.types.Scene.HInch = StringProperty(
        name = "Inch Height",
        description = "",
        default = "AAA")

    def draw(self, context):
        layout = self.layout

        scn = context.scene

        row = layout.row(align=True)
        row1 = layout.row(align=True)
        row2 = layout.row(align=True)
        row3 = layout.row(align=True)
        row4 = layout.row(align=True)
        row5 = layout.row(align=True)
        row6 = layout.row(align=True)
        row7 = layout.row(align=True)
        col = layout.column(align=True)

        row.prop(scn, "From")
        row1.prop(scn, "Orientation")
        row2.prop(scn, "Preset")

        col.separator()
        row3.prop(scn, "Width")
        row3.separator()
        row3.prop(scn, "Height")
        col.separator()
        row4.prop(scn, "DPI")
        col.separator()
        row5.prop(scn, "PWidth")
        row5.separator()
        row5.prop(scn, "PHeight")

        col.separator()
        row6.prop(scn, "WInch")
        row6.prop(scn, "HInch")
        row6.active=False
        row6.enabled=False
        col.separator()

        row7.operator("Do_P2R", text="SET RENDER!", icon="RENDER_STILL")
        
        tipo,dim_w,dim_h=scn.Preset.split("_")

        if scn.From == "Cm--->Pixel":
            row5.active=False
            row5.enabled=False

            if tipo=="custom":
                row3.active=True
                row3.enabled=True
                row1.active=False
                row1.enabled=False
                dim_w=scn.Width
                dim_h=scn.Height
                scn.Width=float(dim_w)
                scn.Height=float(dim_h)
            elif tipo!="custom" and scn.Orientation=="Landscape":
                row3.active=False
                row3.enabled=False
                row1.active=True
                row1.enabled=True
                scn.Width=float(dim_h)
                scn.Height=float(dim_w)
            elif tipo!="custom" and scn.Orientation=="Portrait":
                row3.active=False
                row3.enabled=False
                row1.active=True
                row1.enabled=True
                scn.Width=float(dim_w)
                scn.Height=float(dim_h)

            scn.PWidth=math.ceil((scn.Width*scn.DPI)/2.54)
            scn.PHeight=math.ceil((scn.Height*scn.DPI)/2.54)
        else:
            row3.active=False
            row3.enabled=False

            if tipo=="custom":
                row1.active=False
                row1.enabled=False
            elif tipo!="custom" and scn.Orientation=="Landscape":
                row1.active=True
                row1.enabled=True
                row5.active=False
                row5.enabled=False
                scn.Width=float(dim_h)
                scn.Height=float(dim_w)
                scn.PWidth=math.ceil((scn.Width*scn.DPI)/2.54)
                scn.PHeight=math.ceil((scn.Height*scn.DPI)/2.54)
            elif tipo!="custom" and scn.Orientation=="Portrait":
                row1.active=True
                row1.enabled=True
                row5.active=False
                row5.enabled=False
                scn.Width=float(dim_w)
                scn.Height=float(dim_h)
                scn.PWidth=math.ceil((scn.Width*scn.DPI)/2.54)
                scn.PHeight=math.ceil((scn.Height*scn.DPI)/2.54)


            scn.Width=float(scn.PWidth/scn.DPI)*2.54
            scn.Height=float(scn.PHeight/scn.DPI)*2.54

        scn.WInch="%.2f" % (scn.Width/2.54)
        scn.HInch="%.2f" % (scn.Height/2.54)


class DoP2R(bpy.types.Operator):
    bl_idname = "Do_P2R"
    bl_label = "Run P2R"
    bl_description = "Set the render dimension"

    def execute(self, context):
        scn = context.scene
        rnd = context.scene.render
        #set render resolution
        rnd.resolution_x=scn.PWidth
        rnd.resolution_y=scn.PHeight

        return {'FINISHED'}


def register():
    pass

def unregister():
    pass

if __name__ == "__main__":
    register()
