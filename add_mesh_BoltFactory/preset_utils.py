import bpy
import os, sys


def getPresets():

    scriptPath = sys.path[0] + "\\add_mesh_BoltFactory"
    presetPath = scriptPath + "\\presets"
    presetFiles = os.listdir(presetPath)
    #presetFiles.sort()

    presets = [(presetFile, presetFile.rpartition(".")[0], presetFile)
                for i, presetFile in enumerate(presetFiles)]

    #print(presets)
    return presets, presetPath


#presets = getPresets()



def setProps(props, preset, presetsPath):
    
    #bpy.ops.script.python_file_run(filepath=presetsPath + '\\' + preset)

    file = open(presetsPath + '\\' + preset)

    for line in file:
        exec(line)

    file.close()

    return