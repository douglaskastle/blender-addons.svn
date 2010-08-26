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
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_addon_info = {
	"name": "Save As Runtime",
	"author": "Mitchell Stokes (Moguri)",
	"version": "0.2",
	"blender": (2, 5, 3),
	"location": "File > Export",
	"description": "Bundle a .blend file with the Blenderplayer",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Import/Export"}

import bpy
import struct
import os
import sys

def WriteAppleRuntime(player_path, output_path):
	# Use the system's cp command to preserve some meta-data
	os.system('cp -R "%s" "%s"' % (player_path, output_path))
	
	bpy.ops.save_as_mainfile(filepath=output_path+"/Contents/Resources/game.blend", copy=True)

def WriteRuntime(player_path, output_path):

	# Check the paths
	if not os.path.isfile(player_path):
		print("The player could not be found! Runtime not saved.")
		return
	
	# Check if we're bundling a .app
	if player_path.endswith('.app'):
		WriteAppleRuntime(player_path, output_path)
		return
	
	# Get the player's binary and the offset for the blend
	file = open(player_path, 'rb')
	player_d = file.read()
	offset = file.tell()
	file.close()
	
	# Create a tmp blend file
	blend_path = output_path+'__'
	bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False, copy=True)
	blend_path += '.blend'
	
	
	# Get the blend data
	file = open(blend_path, 'rb')
	blend_d = file.read()
	file.close()
	
	# Get rid of the tmp blend, we're done with it
	os.remove(blend_path)
	
	# Create a new file for the bundled runtime
	output = open(output_path, 'wb')
	
	# Write the player and blend data to the new runtime
	output.write(player_d)
	output.write(blend_d)
	
	# Store the offset (an int is 4 bytes, so we split it up into 4 bytes and save it)
	output.write(struct.pack('B', (offset>>24)&0xFF))
	output.write(struct.pack('B', (offset>>16)&0xFF))
	output.write(struct.pack('B', (offset>>8)&0xFF))
	output.write(struct.pack('B', (offset>>0)&0xFF))
	
	# Stuff for the runtime
	output.write("BRUNTIME".encode())
	output.close()
	
	# Make the runtime executable on Linux
	if os.name == 'posix':
		os.chmod(output_path, 0o755)
	
from bpy.props import *
class SaveAsRuntime(bpy.types.Operator):
	bl_idname = "wm.save_as_runtime"
	bl_label = "Save As Runtime"
	bl_options = {'REGISTER'}
	
	ext = ""
	
	if os.name == "nt":
		ext = ".exe"
	elif os.name == "mac":
		ext = ".app"
	
	player_path = StringProperty(name="Player Path", description="The path to the player to use", default=sys.argv[0].replace("blender"+ext, "blenderplayer"+ext))
	filepath = StringProperty(name="Output Path", description="Where to save the runtime", default="")
	
	def execute(self, context):
		WriteRuntime(self.properties.player_path,
					self.properties.filepath)
		return {'FINISHED'}
					
	def invoke(self, context, event):
		wm = context.manager
		wm.add_fileselect(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	ext = ""
	
	if os.name == "nt":
		ext = ".exe"

	default_path = bpy.data.filepath.replace(".blend", ext)
	self.layout.operator(SaveAsRuntime.bl_idname, text=SaveAsRuntime.bl_label).filepath = default_path


def register():
	bpy.types.INFO_MT_file_export.append(menu_func)
	
def unregister():
	bpy.types.INFO_MT_file_export.remove(menu_func)
	
if __name__ == "__main__":
	register()