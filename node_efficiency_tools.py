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

bl_info = {
    'name': "Nodes Efficiency Tools",
    'author': "Bartek Skorupa",
    'version': (2, 0.08),
    'blender': (2, 6, 6),
    'location': "Node Editor Properties Panel (Ctrl-SPACE)",
    'description': "Nodes Efficiency Tools",
    'warning': "", 
    'wiki_url': "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Nodes/Nodes_Efficiency_Tools",
    'tracker_url': "http://projects.blender.org/tracker/?func=detail&atid=468&aid=33543&group_id=153",
    'category': "Node",
    }

import bpy
from bpy.props import EnumProperty, StringProperty

#################
# rl_outputs:
# list of outputs of Input Render Layer
# with attributes determinig if pass is used,
# and MultiLayer EXR outputs names and corresponding render engines
#
# rl_outputs entry = (render_pass, rl_output_name, exr_output_name, in_internal, in_cycles)
rl_outputs = (
    ('use_pass_ambient_occlusion', 'AO', 'AO', True, True),
    ('use_pass_color', 'Color', 'Color',True, False),
    ('use_pass_combined', 'Image', 'Combined', True, True),
    ('use_pass_diffuse', 'Diffuse', 'Diffuse', True, False),
    ('use_pass_diffuse_color', 'Diffuse Color', 'DiffCol', False, True),
    ('use_pass_diffuse_direct', 'Diffuse Direct', 'DiffDir', False, True),
    ('use_pass_diffuse_indirect', 'Diffuse Indirect', 'DiffInd', False, True),
    ('use_pass_emit', 'Emit', 'Emit', True, False),
    ('use_pass_environment', 'Environment', 'Env', True, False),
    ('use_pass_glossy_color', 'Glossy Color', 'GlossCol', False, True),
    ('use_pass_glossy_direct', 'Glossy Direct', 'GlossDir', False, True),
    ('use_pass_glossy_indirect', 'Glossy Indirect', 'GlossInd', False, True),
    ('use_pass_indirect', 'Indirect', 'Indirect', True, False),
    ('use_pass_material_index', 'IndexMA', 'IndexMA', True, True),
    ('use_pass_mist', 'Mist', 'Mist', True, False),
    ('use_pass_normal', 'Normal', 'Normal', True, True),
    ('use_pass_object_index', 'IndexOB', 'IndexOB', True, True),
    ('use_pass_reflection', 'Reflect', 'Reflect', True, False),
    ('use_pass_refraction', 'Refract', 'Refract', True, False),
    ('use_pass_shadow', 'Shadow', 'Shadow', True, True),
    ('use_pass_specular', 'Specular', 'Spec', True, False),
    ('use_pass_transmission_color', 'Transmission Color', 'TransCol', False, True),
    ('use_pass_transmission_direct', 'Transmission Direct', 'TransDir', False, True),
    ('use_pass_transmission_indirect', 'Transmission Indirect', 'TransInd', False, True),
    ('use_pass_uv', 'UV', 'UV', True, True),
    ('use_pass_vector', 'Speed', 'Vector', True, True),
    ('use_pass_z', 'Z', 'Depth', True, True),
    )

# list of blend types of "Mix" nodes
blend_types = (
    'MIX', 'ADD', 'MULTIPLY', 'SUBTRACT', 'SCREEN',
    'DIVIDE', 'DIFFERENCE', 'DARKEN', 'LIGHTEN', 'OVERLAY',
    'DODGE', 'BURN', 'HUE', 'SATURATION', 'VALUE',
    'COLOR', 'SOFT_LIGHT', 'LINEAR_LIGHT',
    )
# list of operations of "Math" nodes
operations = (
    'ADD', 'MULTIPLY', 'SUBTRACT', 'DIVIDE', 'SINE',
    'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT',
    'POWER', 'LOGARITHM', 'MINIMUM', 'MAXIMUM', 'ROUND',
    'LESS_THAN', 'GREATER_THAN',
    )
# list of mixing shaders
merge_shaders = ('MIX', 'ADD')

def set_convenience_variables(context):
    global nodes
    global links

    space = context.space_data
    tree = space.node_tree
    nodes = tree.nodes
    links = tree.links
    active = nodes.active
    context_active = context.active_node
    # check if we are working on regular node tree or node group is currently edited.
    # if group is edited - active node of space_tree is the group
    # if context.active_node != space active node - it means that the group is being edited.
    # in such case we set "nodes" to be nodes of this group, "links" to be links of this group
    # if context.active_node == space.active_node it means that we are not currently editing group
    is_main_tree = True
    if active:
        is_main_tree = context_active == active
    if not is_main_tree:  # if group is currently edited
        tree = active.node_tree
        nodes = tree.nodes
        links = tree.links
    
    return


class MergeNodes(bpy.types.Operator):
    bl_idname = "node.merge_nodes"
    bl_label = "Merge Selected Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    combo = StringProperty(
        name = "Combo",
        description = "BlendType/ShaderKind/MathOperation and Node Kind",
        )
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        tree_type = context.space_data.node_tree.type
        if tree_type == 'COMPOSITING':
            node_type = 'CompositorNode'
        elif tree_type == 'SHADER':
            node_type = 'ShaderNode'
        set_convenience_variables(context)
        combo_split = self.combo.split( )
        mode = combo_split[0]
        node_kind = combo_split[1]  # kinds: 'AUTO', 'SHADER', 'MIX', 'MATH'
        selected_mix = []  # entry = [index, loc]
        selected_shader = []  # entry = [index, loc]
        selected_math = []  # entry = [index, loc]
        
        for i, node in enumerate(nodes):
            if node.select and node.outputs:
                if node_kind == 'AUTO':
                    for (type, the_list, dst) in (
                        ('SHADER', merge_shaders, selected_shader),
                        ('RGBA', blend_types, selected_mix),
                        ('VALUE', operations, selected_math),
                        ):
                        output_type = node.outputs[0].type
                        valid_mode = mode in the_list
                        # When mode is 'MIX' use mix node for both 'RGBA' and 'VALUE' output types.
                        # Cheat that output type is 'RGBA',
                        # and that 'MIX' exists in math operations list.
                        # This way when selected_mix list is analyzed:
                        # Node data will be appended even though it doesn't meet requirements.
                        if output_type != 'SHADER' and mode == 'MIX':
                            output_type = 'RGBA'
                            valid_mode = True
                        if output_type == type and valid_mode:
                            dst.append([i, node.location.x, node.location.y])
                else:
                    for (kind, the_list, dst) in (
                        ('MIX', blend_types, selected_mix),
                        ('SHADER', merge_shaders, selected_shader),
                        ('MATH', operations, selected_math),
                        ):
                        if node_kind == kind and mode in the_list:
                            dst.append([i, node.location.x, node.location.y])
        # When nodes with output kinds 'RGBA' and 'VALUE' are selected at the same time
        # use only 'Mix' nodes for merging.
        # For that we add selected_math list to selected_mix list and clear selected_math.
        if selected_mix and selected_math and node_kind == 'AUTO':
            selected_mix += selected_math
            selected_math = []
        
        for the_list in [selected_mix, selected_shader, selected_math]:
            if the_list:
                count_before = len(nodes)
                # sort list by loc_x - reversed
                the_list.sort(key = lambda k: k[1], reverse = True)
                # get maximum loc_x
                loc_x = the_list[0][1] + 350.0
                the_list.sort(key = lambda k: k[2], reverse = True)
                loc_y = the_list[len(the_list) - 1][2]
                offset_y = 40.0
                if the_list == selected_shader:
                    offset_y = 150.0
                the_range = len(the_list)-1
                do_hide = True
                if len(the_list) == 1:
                    the_range = 1
                    do_hide = False
                for i in range(the_range):
                    if the_list == selected_mix:
                        add_type = node_type + 'MixRGB'
                        add = nodes.new(add_type)
                        add.blend_type = mode
                        add.show_preview = False
                        add.hide = do_hide
                        first = 1
                        second = 2
                        add.width_hidden = 100.0
                    elif the_list == selected_math:
                        add_type = node_type + 'Math'
                        add = nodes.new(add_type)
                        add.operation = mode
                        add.hide = do_hide
                        first = 0
                        second = 1
                        add.width_hidden = 100.0
                    elif the_list == selected_shader:
                        if mode == 'MIX':
                            add_type = node_type + 'MixShader'
                            add = nodes.new(add_type)
                            first = 1
                            second = 2
                            add.width_hidden = 100.0
                        elif mode == 'ADD':
                            add_type = node_type + 'AddShader'
                            add = nodes.new(add_type)
                            first = 0
                            second = 1
                            add.width_hidden = 100.0
                    add.location.x = loc_x
                    add.location.y = loc_y
                    loc_y += offset_y
                    add.select = True
                count_adds = i + 1
                count_after = len(nodes)
                index = count_after - 1
                # add link from "first" selected and "first" add node
                links.new(nodes[the_list[0][0]].outputs[0], nodes[count_after - 1].inputs[first])
                # add links between added ADD nodes and between selected and ADD nodes
                for i in range(count_adds):
                    if i < count_adds - 1:
                        links.new(nodes[index-1].inputs[first], nodes[index].outputs[0])
                    if len(the_list) > 1:
                        links.new(nodes[index].inputs[second], nodes[the_list[i+1][0]].outputs[0])
                    index -= 1
                # set "last" of added nodes as active    
                nodes.active = nodes[count_before]
                for [i, x, y] in the_list:
                    nodes[i].select = False
                    
        return {'FINISHED'}


class BatchChangeNodes(bpy.types.Operator):
    bl_idname = "node.batch_change"
    bl_label = "Batch Change Blend Type and Math Operation"
    bl_options = {'REGISTER', 'UNDO'}
    
    combo = StringProperty(
        name = "Combo",
        description = "Mix Blend Type and Math Operation"
        )
        
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        navs = ('CURRENT', 'NEXT', 'PREV')
        combo_split = self.combo.split( )
        blend_type = combo_split[0]
        operation = combo_split[1]
        for node in context.selected_nodes:
            if node.type == 'MIX_RGB':
                if not blend_type in navs:
                    node.blend_type = blend_type
                else:
                    if blend_type == 'NEXT':
                        index = blend_types.index(node.blend_type)
                        if index == len(blend_types) - 1:
                            node.blend_type = blend_types[0]
                        else:
                            node.blend_type = blend_types[index + 1]

                    if blend_type == 'PREV':
                        index = blend_types.index(node.blend_type)
                        if index == 0:
                            node.blend_type = blend_types[len(blend_types) - 1]
                        else:
                            node.blend_type = blend_types[index - 1]
                                                        
            if node.type == 'MATH':
                if not operation in navs:
                    node.operation = operation
                else:
                    if operation == 'NEXT':
                        index = operations.index(node.operation)
                        if index == len(operations) - 1:
                            node.operation = operations[0]
                        else:
                            node.operation = operations[index + 1]

                    if operation == 'PREV':
                        index = operations.index(node.operation)
                        if index == 0:
                            node.operation = operations[len(operations) - 1]
                        else:
                            node.operation = operations[index - 1]

        return {'FINISHED'}


class ChangeMixFactor(bpy.types.Operator):
    bl_idname = "node.factor"
    bl_label = "Change Factors of Mix Nodes and Mix Shader Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    change = StringProperty(
        name = "Fac_Change",
        description = "Factor Change",
        )
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        change = float(self.change)
        selected = []  # entry = index
        for si, node in enumerate(nodes):
            if node.select:
                if node.type in {'MIX_RGB', 'MIX_SHADER'}:
                    selected.append(si)
                
        for si in selected:
            fac = nodes[si].inputs[0]
            nodes[si].hide = False
            if change in {0.0, 1.0}:
                fac.default_value = change
            else:
                fac.default_value += change
        
        return {'FINISHED'}


class NodesCopySettings(bpy.types.Operator):
    bl_idname = "node.copy_settings"
    bl_label = "Copy Settings of Active Node to Selected Nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        valid = False
        if (space.type == 'NODE_EDITOR' and
                space.node_tree is not None and
                context.active_node is not None and
                context.active_node.type is not 'FRAME'
                ):
            valid = True
        return valid
    
    def execute(self, context):
        set_convenience_variables(context)
        selected = [n for n in nodes if n.select]
        reselect = []  # duplicated nodes will be selected after execution
        active = nodes.active
        if active.select:
            reselect.append(active)
        
        for node in selected:
            if node.type == active.type and node != active:
                # duplicate active, relink links as in 'node', append copy to 'reselect', delete node
                bpy.ops.node.select_all(action = 'DESELECT')
                nodes.active = active
                active.select = True
                bpy.ops.node.duplicate()
                copied = nodes.active
                # Copied active should however inherit some properties from 'node'
                attributes = (
                    'hide', 'show_preview', 'mute', 'label',
                    'use_custom_color', 'color', 'width', 'width_hidden',
                    )
                for attr in attributes:
                    setattr(copied, attr, getattr(node, attr))
                # Handle scenario when 'node' is in frame. 'copied' is in same frame then.
                if copied.parent:
                    bpy.ops.node.parent_clear()
                locx = node.location.x
                locy = node.location.y
                # get absolute node location
                parent = node.parent
                while parent:
                    locx += parent.location.x
                    locy += parent.location.y
                    parent = parent.parent
                copied.location = [locx, locy]
                # reconnect links from node to copied
                for i, input in enumerate(node.inputs):
                    if input.links:
                        link = input.links[0]
                        links.new(link.from_socket, copied.inputs[i])
                for out, output in enumerate(node.outputs):
                    if output.links:
                        out_links = output.links
                        for link in out_links:
                            links.new(copied.outputs[out], link.to_socket)
                bpy.ops.node.select_all(action = 'DESELECT')
                node.select = True
                bpy.ops.node.delete()
                reselect.append(copied)
            else:  # If selected wasn't copied, need to reselect it afterwards.
                reselect.append(node)
        # clean up
        bpy.ops.node.select_all(action = 'DESELECT')
        for node in reselect:
            node.select = True
        nodes.active = active
        
        return {'FINISHED'}


class NodesCopyLabel(bpy.types.Operator):
    bl_idname = "node.copy_label"
    bl_label = "Copy Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    # option: 'from active', 'from node', 'from socket'
    option = StringProperty()
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        option = self.option
        active = nodes.active
        if option == 'from active':
            if active:
                src_label = active.label
                for node in [n for n in nodes if n.select and nodes.active != n]:
                    node.label = src_label
        elif option == 'from node':
            selected = [n for n in nodes if n.select]
            for node in selected:
                for input in node.inputs:
                    if input.links:
                        src = input.links[0].from_node
                        node.label = src.label
                        break
        elif option == 'from socket':
            selected = [n for n in nodes if n.select]
            for node in selected:
                for input in node.inputs:
                    if input.links:
                        src = input.links[0].from_socket
                        node.label = src.name
                        break
        
        return {'FINISHED'}


class NodesClearLabel(bpy.types.Operator):
    bl_idname = "node.clear_label"
    bl_label = "Clear Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        for node in [n for n in nodes if n.select]:
            node.label = ''
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class NodesAddTextureSetup(bpy.types.Operator):
    bl_idname = "node.add_texture"
    bl_label = "Add Texture Node to Active Node Input"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        valid = False
        if space.type == 'NODE_EDITOR':
            if space.tree_type == 'ShaderNodeTree' and space.node_tree is not None:
                valid = True
        return valid
    
    def execute(self, context):
        set_convenience_variables(context)
        active = nodes.active
        valid = False
        if active:
            if active.select:
                if active.type in (
                    'BSDF_ANISOTROPIC',
                    'BSDF_DIFFUSE',
                    'BSDF_GLOSSY',
                    'BSDF_GLASS',
                    'BSDF_REFRACTION',
                    'BSDF_TRANSLUCENT',
                    'BSDF_TRANSPARENT',
                    'BSDF_VELVET',
                    'EMISSION',
                    'AMBIENT_OCCLUSION',
                    ):
                    if not active.inputs[0].is_linked:
                        valid = True
        if valid:
            locx = active.location.x
            locy = active.location.y
            tex = nodes.new('ShaderNodeTexImage')
            tex.location = [locx - 200.0, locy + 28.0]
            map = nodes.new('ShaderNodeMapping')
            map.location = [locx - 490.0, locy + 80.0]
            coord = nodes.new('ShaderNodeTexCoord')
            coord.location = [locx - 700, locy + 40.0]
            active.select = False
            nodes.active = tex
            
            links.new(tex.outputs[0], active.inputs[0])
            links.new(map.outputs[0], tex.inputs[0])
            links.new(coord.outputs[2], map.inputs[0])
            
        return {'FINISHED'}


class NodesAddReroutes(bpy.types.Operator):
    bl_idname = "node.add_reroutes"
    bl_label = "Add Reroutes to Outputs"
    bl_options = {'REGISTER', 'UNDO'}
    
    # option: 'all', 'loose'
    option = StringProperty()
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        tree_type = context.space_data.node_tree.type
        if tree_type == 'COMPOSITING':
            node_type = 'CompositorNode'
        elif tree_type == 'SHADER':
            node_type = 'ShaderNode'
        option = self.option
        set_convenience_variables(context)
        # output valid when option is 'all' or when 'loose' output has no links
        valid = False
        post_select = []  # nodes to be selected after execution
        # create reroutes and recreate links
        for node in [n for n in nodes if n.select]:
            if node.outputs:
                x = node.location.x
                y = node.location.y
                width = node.width
                # unhide 'REROUTE' nodes to avoid issues with location.y
                if node.type == 'REROUTE':
                    node.hide = False
                # When node is hidden - width_hidden not usable.
                # Hack needed to calculate real width
                if node.hide:
                    bpy.ops.node.select_all(action = 'DESELECT')
                    helper = nodes.new('NodeReroute')
                    helper.select = True
                    node.select = True
                    # resize node and helper to zero. Then check locations to calculate width
                    bpy.ops.transform.resize(value = (0.0, 0.0, 0.0))
                    width = 2.0 * (helper.location.x - node.location.x)
                    # restore node location
                    node.location = [x,y]
                    # delete helper
                    node.select = False
                    # only helper is selected now
                    bpy.ops.node.delete()
                x = node.location.x + width + 20.0
                if node.type != 'REROUTE':
                    y -= 35.0
                y_offset = -20.0
                loc = [x, y]
            reroutes_count = 0  # will be used when aligning reroutes added to hidden nodes
            for out_i, output in enumerate(node.outputs):
                pass_used = False  # initial value to be analyzed if 'R_LAYERS'
                # if node is not 'R_LAYERS' - "pass_used" not needed, so set it to True
                if node.type != 'R_LAYERS':
                    pass_used = True
                else:  # if 'R_LAYERS' check if output represent used render pass
                    node_scene = node.scene
                    node_layer = node.layer
                    # If output - "Alpha" is analyzed - assume it's used. Not represented in passes.
                    if output.name == 'Alpha':
                        pass_used = True
                    else:
                        # check entries in global 'rl_outputs' variable
                        for [render_pass, out_name, exr_name, in_internal, in_cycles] in rl_outputs:
                            if output.name == out_name:
                                pass_used = getattr(node_scene.render.layers[node_layer], render_pass)
                                break
                if pass_used:
                    valid = option == 'all' or (option == 'loose' and not output.links)
                    # Add reroutes only if valid, but offset location in all cases.
                    if valid:
                        n = nodes.new('NodeReroute')
                        nodes.active = n
                        for link in output.links:
                            links.new(n.outputs[0], link.to_socket)
                        links.new(output, n.inputs[0])
                        n.location = loc
                        post_select.append(n)
                    reroutes_count += 1
                    y += y_offset 
                    loc = [x, y]
            # disselect the node so that after execution of script only newly created nodes are selected
            node.select = False
            # nicer reroutes distribution along y when node.hide
            if node.hide:
                y_translate = reroutes_count * y_offset / 2.0 - y_offset - 35.0
                for reroute in [r for r in nodes if r.select]:
                    reroute.location.y -= y_translate
            for node in post_select:
                node.select = True
        
        return {'FINISHED'}
    

class NodesReroutesSwitchesSwap(bpy.types.Operator):
    bl_idname = "node.reroutes_switches_swap"
    bl_label = "Swap Reroutes and Switches"
    bl_options = {'REGISTER', 'UNDO'}
    
    # option: 'CompositorNodeSwitch', 'NodeReroute'
    # 'CompositorNodeSwitch' - change selected reroutes to switches
    # 'NodeReroute' - change selected switches to reroutes
    option = StringProperty()
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        valid = False
        if space.type == 'NODE_EDITOR':
            if space.tree_type == 'CompositorNodeTree' and space.node_tree is not None:
                valid = True
        return valid
    
    def execute(self, context):
        set_convenience_variables(context)
        option = self.option
        selected = [n for n in nodes if n.select]
        reselect = []
        # If change to switches - replace reroutes
        if option == 'CompositorNodeSwitch':
            replace_type = 'REROUTE'
        # If change to reroutes - replace switches
        elif option == 'NodeReroute':
            replace_type = 'SWITCH'
        for node in selected:
            if node.type == replace_type:
                valid = True
                if option == 'NodeReroute':
                    # If something is linked to second input of switch - don't replace.
                    if node.inputs[1].links:
                        valid = False
                if valid:
                    new_node = nodes.new(option)
                    in_link = node.inputs[0].links[0]
                    if in_link:
                        links.new(in_link.from_socket, new_node.inputs[0])
                    for out_link in node.outputs[0].links:
                        links.new(new_node.outputs[0], out_link.to_socket)
                    new_node.location = node.location
                    new_node.label = node.label
                    new_node.hide = True
                    new_node.width_hidden = 100.0
                    nodes.active = new_node
                    reselect.append(new_node)
                    bpy.ops.node.select_all(action = "DESELECT")
                    node.select = True
                    bpy.ops.node.delete()
                else:
                    reselect.append(node)
        for node in reselect:
            node.select = True
            
        return {'FINISHED'}


class NodesLinkActiveToSelected(bpy.types.Operator):
    bl_idname = "node.link_active_to_selected"
    bl_label = "Link Active Node to Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    # option: 'True/Nodes Names', 'True/Nodes Location', 'True/First Output Only'
    #         'False/Nodes Names', 'False/Nodes Location', 'False/First Output Only'
    option = StringProperty()    
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        valid = False
        if space.type == 'NODE_EDITOR':
            if space.node_tree is not None and context.active_node is not None:
                valid = True
        return valid
    
    def execute(self, context):
        set_convenience_variables(context)
        splitted_option = self.option.split('/')
        # Will replace existing links or not
        replace = eval(splitted_option[0])  # True or False
        # basis for linking: 'Nodes Names', 'Nodes Location', 'First Output Only'
        option = splitted_option[1]
        # Links will be made from active node
        active = nodes.active
        # create list of selected nodes. Links will be made to those nodes
        selected = []  # entry = [node index, node locacion.x, node.location.y]
        for i, node in enumerate(nodes):
            is_selected = node.select
            is_not_active = node != active
            has_inputs = len(node.inputs) > 0
            is_valid = is_selected and is_not_active and has_inputs
            if is_valid:
                selected.append([i, node.location.x, node.location.y])
        # sort selected by location.y, then location.x. Easier handling of "Nodes Location" option
        selected.sort(key = lambda k: (-k[2], k[1]))
        if active:
            if active.select:
                # create manageable list of active outputs
                outputs = []
                for i, out in enumerate(active.outputs):
                    if active.type != 'R_LAYERS':
                        outputs.append(i)
                    else:
                        # 'R_LAYERS' node type needs special handling.
                        # Check if pass represented by output is used.
                        # global 'rl_outputs' list will be used for that
                        for [render_pass, out_name, exr_name, in_internal, in_cycles] in rl_outputs:
                            pass_used = False
                            if out.name == 'Alpha':
                                pass_used = True
                            elif out.name == out_name:
                                # example 'render_pass' entry: 'use_pass_uv' Check if True in scene render layers
                                pass_used = getattr(node.scene.render.layers[node.layer], render_pass)
                                break
                        if pass_used:
                            outputs.append(i)
                if outputs:
                    if option == 'Nodes Names':
                        for i, out in enumerate(outputs):
                            for [ni, x, y] in selected:  # [node index, location.x, location.y]
                                name = nodes[ni].name
                                l = len(nodes[ni].inputs)
                                if nodes[ni].label:
                                    name = nodes[ni].label
                                for [render_pass, out_name, exr_name, in_internal, in_cycles] in rl_outputs:
                                    if name in {out_name, exr_name}:
                                        names = [out_name, exr_name]  # if out name matches any of those - valid
                                        break
                                    else:
                                        names = [name]  # length of entry doesn't matter.
                                if len(outputs) > 1:
                                    if active.outputs[out].name in names:
                                        out_type = active.outputs[out].type
                                        input_i = 0
                                        if (nodes[ni].inputs[0].type != out_type and l > 1):
                                            for ii in range (1, l):
                                                if nodes[ni].inputs[ii].type == out_type:
                                                    input_i = ii
                                                    break
                                        links.new(active.outputs[out], nodes[ni].inputs[input_i])
                                else:
                                    a_name = active.name
                                    if active.label:
                                        a_name = active.label
                                    if a_name in names:
                                        out_type = active.outputs[0].type
                                        input_i = 0
                                        if (nodes[ni].inputs[0].type != out_type and l > 1):
                                            for ii in range (1, l):
                                                if nodes[ni].inputs[ii].type == out_type:
                                                    input_i = ii
                                                    break
                                        links.new(active.outputs[0], nodes[ni].inputs[input_i])
                    elif option == 'Nodes Location':
                        for i, out in enumerate(outputs):
                            if i < len(selected):
                                out_type = active.outputs[out].type
                                l = len(nodes[selected[i][0]].inputs)
                                input_i = 0
                                if (nodes[selected[i][0]].inputs[0].type != out_type and l > 1):
                                    for ii in range (1, l):
                                        if nodes[selected[i][0]].inputs[ii].type == out_type:
                                            input_i = ii
                                            break
                                links.new(active.outputs[out], nodes[selected[i][0]].inputs[input_i])
                    elif option == 'First Output Only':
                        out_type = active.outputs[0].type
                        for [ni, x, y] in selected:
                            l = len(nodes[ni].inputs)
                            input_i = 0
                            if (nodes[ni].inputs[0].type != out_type and l > 1):
                                for ii in range (1, l):
                                    if nodes[ni].inputs[ii].type == out_type:
                                        input_i = ii
                                        break
                            links.new(active.outputs[0], nodes[ni].inputs[input_i])

        return {'FINISHED'}            


class AlignNodes(bpy.types.Operator):
    bl_idname = "node.align_nodes"
    bl_label = "Align nodes"
    bl_options = {'REGISTER', 'UNDO'}
    
    axes = []
    axes_list = ['Vertically', 'Horizontally']
    for axis in axes_list:
        axes.append((axis, axis, axis))
    
    align_axis = EnumProperty(
        name = "align_axis",
        description = "Align Axis",
        items = axes
        )
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        selected = []  # entry = [index, loc.x, loc.y, width, height]
        frames_reselect = []  # entry = frame node. will be used to reselect all selected frames
        active = nodes.active
        for i, node in enumerate(nodes):
            if node.select:
                if node.type == 'FRAME':
                    node.select = False
                    frames_reselect.append(i)
                else:
                    locx = node.location.x
                    locy = node.location.y
                    parent = node.parent
                    while parent != None:
                        locx += parent.location.x
                        locy += parent.location.y
                        parent = parent.parent
                    selected.append([i, locx, locy])
        count = len(selected)
        # add reroute node then scale all to 0.0 and calculate widths and heights of nodes
        if count > 1:  # aligning makes sense only if at least 2 nodes are selected
            helper = nodes.new('NodeReroute')
            helper.select = True
            bpy.ops.transform.resize(value = (0.0, 0.0, 0.0))
            # store helper's location for further calculations
            zero_x = helper.location.x
            zero_y = helper.location.y
            nodes.remove(helper)
            # helper is deleted but its location is stored
            # helper's width and height are 0.0.
            # Check loc of other nodes in relation to helper to calculate their dimensions
            # and append them to entries of "selected"
            total_w = 0.0  # total width of all nodes. Will be calculated later.
            total_h = 0.0  # total height of all nodes. Will be calculated later
            for j, [i, x, y] in enumerate(selected):
                locx = nodes[i].location.x
                locy = nodes[i].location.y
                # take node's parent (frame) into account. Get absolute location
                parent = nodes[i].parent
                while parent != None:
                        locx += parent.location.x
                        locy += parent.location.y
                        parent = parent.parent
                width = abs((zero_x - locx) * 2.0)
                height = abs((zero_y - locy) * 2.0)
                selected[j].append(width)  # complete selected's entry for nodes[i]
                selected[j].append(height)  # complete selected's entry for nodes[i]
                total_w += width  # add nodes[i] width to total width of all nodes
                total_h += height  # add nodes[i] height to total height of all nodes
            selected_sorted_x = sorted(selected, key = lambda k: (k[1], -k[2]))
            selected_sorted_y = sorted(selected, key = lambda k: (-k[2], k[1]))
            min_x = selected_sorted_x[0][1]  # min loc.x
            min_x_loc_y = selected_sorted_x[0][2]  # loc y of node with min loc x
            min_x_w = selected_sorted_x[0][3]  # width of node with max loc x
            max_x = selected_sorted_x[count - 1][1]  # max loc.x
            max_x_loc_y = selected_sorted_x[count - 1][2]  # loc y of node with max loc.x
            max_x_w = selected_sorted_x[count - 1][3]  #  width of node with max loc.x
            min_y = selected_sorted_y[0][2]  # min loc.y
            min_y_loc_x = selected_sorted_y[0][1]  # loc.x of node with min loc.y
            min_y_h = selected_sorted_y[0][4]  # height of node with min loc.y
            min_y_w = selected_sorted_y[0][3]  # width of node with min loc.y
            max_y = selected_sorted_y[count - 1][2]  # max loc.y
            max_y_loc_x = selected_sorted_y[count - 1][1]  # loc x of node with max loc.y
            max_y_w = selected_sorted_y[count - 1][3]  # width of node with max loc.y
            max_y_h = selected_sorted_y[count - 1][4]  # height of node with max loc.y
            
            if self.align_axis == 'Vertically':
                loc_x = min_x
                #loc_y = (max_x_loc_y + min_x_loc_y) / 2.0
                loc_y = (max_y - max_y_h / 2.0 + min_y - min_y_h / 2.0) / 2.0
                offset_x = (max_x - min_x - total_w + max_x_w) / (count - 1)
                for [i, x, y, w, h] in selected_sorted_x:
                    nodes[i].location.x = loc_x
                    nodes[i].location.y = loc_y + h / 2.0
                    parent = nodes[i].parent
                    while parent != None:
                        nodes[i].location.x -= parent.location.x
                        nodes[i].location.y -= parent.location.y
                        parent = parent.parent
                    loc_x += offset_x + w
            else:  # if align Horizontally
                #loc_x = (max_y_loc_x + max_y_w / 2.0 + min_y_loc_x + min_y_w / 2.0) / 2.0
                loc_x = (max_x + max_x_w / 2.0 + min_x + min_x_w / 2.0) / 2.0
                loc_y = min_y
                offset_y = (max_y - min_y + total_h - min_y_h) / (count - 1)
                for [i, x, y, w, h] in selected_sorted_y:
                    nodes[i].location.x = loc_x - w / 2.0
                    nodes[i].location.y = loc_y
                    parent = nodes[i].parent
                    while parent != None:
                        nodes[i].location.x -= parent.location.x
                        nodes[i].location.y -= parent.location.y
                        parent = parent.parent
                    loc_y += offset_y - h
    
            # reselect selected frames
            for i in frames_reselect:
                nodes[i].select = True
            # restore active node
            nodes.active = active
        
        return {'FINISHED'}


class SelectParentChildren(bpy.types.Operator):
    bl_idname = "node.select_parent_child"
    bl_label = "Select Parent or Children"
    bl_options = {'REGISTER', 'UNDO'}
    
    option = StringProperty(
        name = "option",
        description = "Parent/Children",
        )
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def execute(self, context):
        set_convenience_variables(context)
        option = self.option
        selected = [node for node in nodes if node.select]
        if option == 'Parent':
            for sel in selected:
                parent = sel.parent
                if parent:
                    parent.select = True
        else:
            for sel in selected:
                children = [node for node in nodes if node.parent == sel]
                for kid in children:
                    kid.select = True
        
        return {'FINISHED'}


#############################################################
#  P A N E L S
#############################################################

class EfficiencyToolsPanel(bpy.types.Panel):
    bl_idname = "NODE_PT_efficiency_tools"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Efficiency Tools (Ctrl-SPACE)"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None

    def draw(self, context):
        type = context.space_data.tree_type
        layout = self.layout

        box = layout.box()
        box.menu(MergeNodesMenu.bl_idname)
        if type == 'ShaderNodeTree':
            box.operator(NodesAddTextureSetup.bl_idname, text = 'Add Image Texture (Ctrl T)')
        box.menu(BatchChangeNodesMenu.bl_idname, text = 'Batch Change...')
        box.operator_menu_enum(AlignNodes.bl_idname, "align_axis", text = "Align Nodes (Shift =)")
        box.menu(CopyNodePropertiesMenu.bl_idname, text = 'Copy to Selected (Shift-C)')
        box.operator(NodesClearLabel.bl_idname)
        box.menu(AddReroutesMenu.bl_idname, text = 'Add Reroutes')
        box.menu(ReroutesSwitchesSwapMenu.bl_idname, text = 'Swap Reroutes and Switches')
        box.menu(LinkActiveToSelectedMenu.bl_idname, text = 'Link Active To Selected')


#############################################################
#  M E N U S
#############################################################

class EfficiencyToolsMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_node_tools_menu"
    bl_label = "Efficiency Tools"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        type = context.space_data.tree_type
        layout = self.layout
        layout.menu(MergeNodesMenu.bl_idname, text = 'Merge Selected Nodes')
        if type == 'ShaderNodeTree':
            layout.operator(NodesAddTextureSetup.bl_idname, text = 'Add Image Texture with coordinates')
        layout.menu(BatchChangeNodesMenu.bl_idname, text = 'Batch Change')
        layout.operator_menu_enum(
            AlignNodes.bl_idname,
            property="align_axis",
            text="Align Nodes",
            )
        layout.menu(CopyNodePropertiesMenu.bl_idname, text = 'Copy to Selected')
        layout.menu(AddReroutesMenu.bl_idname, text = 'Add Reroutes')
        layout.menu(ReroutesSwitchesSwapMenu.bl_idname, text = 'Swap Reroutes and Switches')
        layout.menu(LinkActiveToSelectedMenu.bl_idname, text = 'Link Active To Selected')


class MergeNodesMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_merge_nodes_menu"
    bl_label = "Merge Selected Nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        type = context.space_data.tree_type
        layout = self.layout
        if type == 'ShaderNodeTree':
            layout.menu(MergeShadersMenu.bl_idname, text = 'Use Shaders')
        layout.menu(MergeMixMenu.bl_idname, text="Use Mix Nodes")
        layout.menu(MergeMathMenu.bl_idname, text="Use Math Nodes")


class MergeShadersMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_merge_shaders_menu"
    bl_label = "Merge Selected Nodes using Shaders"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for type in merge_shaders:
            combo = type + ' SHADER'
            layout.operator(MergeNodes.bl_idname, text = type).combo = combo


class MergeMixMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_merge_mix_menu"
    bl_label = "Merge Selected Nodes using Mix"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for type in blend_types:
            combo = type + ' MIX'
            layout.operator(MergeNodes.bl_idname, text = type).combo = combo        


class MergeMathMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_merge_math_menu"
    bl_label = "Merge Selected Nodes using Math"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for type in operations:
            combo = type + ' MATH'
            layout.operator(MergeNodes.bl_idname, text = type).combo = combo


class BatchChangeNodesMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_batch_change_nodes_menu"
    bl_label = "Batch Change Selected Nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        layout.menu(BatchChangeBlendTypeMenu.bl_idname)
        layout.menu(BatchChangeOperationMenu.bl_idname)
                                  

class BatchChangeBlendTypeMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_batch_change_blend_type_menu"
    bl_label = "Batch Change Blend Type"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for blend_type in blend_types:
            combo = blend_type + ' CURRENT'
            layout.operator(BatchChangeNodes.bl_idname, text = blend_type).combo = combo


class BatchChangeOperationMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_batch_change_operation_menu"
    bl_label = "Batch Change Math Operation"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for operation in operations:
            combo = 'CURRENT ' + operation
            layout.operator(BatchChangeNodes.bl_idname, text = operation).combo = combo
                                  

class CopyNodePropertiesMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_copy_node_properties_menu"
    bl_label = "Copy Active Node's Properties to Selected"

    def draw(self, context):
        layout = self.layout
        layout.operator(NodesCopySettings.bl_idname, text = 'Settings from Active')
        layout.menu(CopyLabelMenu.bl_idname)


class CopyLabelMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_copy_label_menu"
    bl_label = "Copy Label"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(NodesCopyLabel.bl_idname, text = 'from Active Node\'s Label').option = 'from active'
        layout.operator(NodesCopyLabel.bl_idname, text = 'from Linked Node\'s Label').option = 'from node'
        layout.operator(NodesCopyLabel.bl_idname, text = 'from Linked Output\'s Name').option = 'from socket'


class AddReroutesMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_add_reroutes_menu"
    bl_label = "Add Reroutes"

    def draw(self, context):
        layout = self.layout
        layout.operator(NodesAddReroutes.bl_idname, text = 'to All Outputs').option = 'all'
        layout.operator(NodesAddReroutes.bl_idname, text = 'to Loose Outputs').option = 'loose'


class ReroutesSwitchesSwapMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_reroutes_switches_swap_menu"
    bl_label = "Swap Reroutes and Switches"
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        layout.operator(NodesReroutesSwitchesSwap.bl_idname, text = "Change to Switches").option = 'CompositorNodeSwitch'
        layout.operator(NodesReroutesSwitchesSwap.bl_idname, text = "Change to Reroutes").option = 'NodeReroute'


class LinkActiveToSelectedMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_link_active_to_selected_menu"
    bl_label = "Link Active to Selected, base on..."

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        for opt in ('Nodes Names', 'Nodes Location', 'First Output Only'):
            full_opt = 'True/' + opt
            layout.operator(NodesLinkActiveToSelected.bl_idname, text=opt).option = full_opt


class NodeAlignMenu(bpy.types.Menu):
    bl_idname = "NODE_MT_node_align_menu"
    bl_label = "Align Nodes"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and space.node_tree is not None
    
    def draw(self, context):
        layout = self.layout
        layout.operator_menu_enum(
            AlignNodes.bl_idname,
            property="align_axis",
            text="Direction...",
            )

#############################################################
#  MENU ITEMS
#############################################################

def select_parent_children_buttons(self, context):
    layout = self.layout
    layout.operator(SelectParentChildren.bl_idname, text = 'Select frame\'s members (children)').option = "Children"
    layout.operator(SelectParentChildren.bl_idname, text = 'Select parent frame').option = "Parent"

#############################################################
#  REGISTER/UNREGISTER CLASSES AND KEYMAP ITEMS
#############################################################

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Node Editor', space_type = "NODE_EDITOR")

    kmi = km.keymap_items.new('wm.call_menu', 'SPACE', 'PRESS', ctrl = True)
    kmi.properties.name = EfficiencyToolsMenu.bl_idname
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_0', 'PRESS', ctrl = True)
    kmi.properties.combo = 'MIX AUTO'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl = True)
    kmi.properties.combo = 'ADD AUTO'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl = True)
    kmi.properties.combo = 'MULTIPLY AUTO'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl = True)
    kmi.properties.combo = 'SUBTRACT AUTO'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_SLASH', 'PRESS', ctrl = True)
    kmi.properties.combo = 'DIVIDE AUTO'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'COMMA', 'PRESS', ctrl = True)
    kmi.properties.combo = 'LESS_THAN MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'PERIOD', 'PRESS', ctrl = True)
    kmi.properties.combo = 'GREATER_THAN MATH'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_0', 'PRESS', ctrl = True, alt = True)
    kmi.properties.combo = 'MIX MIX'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl = True, alt = True)
    kmi.properties.combo = 'ADD MIX'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl = True, alt = True)
    kmi.properties.combo = 'MULTIPLY MIX'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl = True, alt = True)
    kmi.properties.combo = 'SUBTRACT MIX'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_SLASH', 'PRESS', ctrl = True, alt = True)
    kmi.properties.combo = 'DIVIDE MIX'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'ADD MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'MULTIPLY MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'SUBTRACT MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'NUMPAD_SLASH', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'DIVIDE MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'COMMA', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'LESS_THAN MATH'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(MergeNodes.bl_idname, 'PERIOD', 'PRESS', ctrl = True, shift = True)
    kmi.properties.combo = 'GREATER_THAN MATH'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'NUMPAD_0', 'PRESS', alt = True)
    kmi.properties.combo = 'MIX CURRENT'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'NUMPAD_PLUS', 'PRESS', alt = True)
    kmi.properties.combo = 'ADD ADD'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', alt = True)
    kmi.properties.combo = 'MULTIPLY MULTIPLY'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'NUMPAD_MINUS', 'PRESS', alt = True)
    kmi.properties.combo = 'SUBTRACT SUBTRACT'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'NUMPAD_SLASH', 'PRESS', alt = True)
    kmi.properties.combo = 'DIVIDE DIVIDE'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'DOWN_ARROW', 'PRESS', alt = True)
    kmi.properties.combo = 'NEXT NEXT'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'UP_ARROW', 'PRESS', alt = True)
    kmi.properties.combo = 'PREV PREV'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'COMMA', 'PRESS', alt = True)
    kmi.properties.combo = 'CURRENT LESS_THAN'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BatchChangeNodes.bl_idname, 'PERIOD', 'PRESS', alt = True)
    kmi.properties.combo = 'CURRENT GREATER_THAN'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'LEFT_ARROW', 'PRESS', alt = True)
    kmi.properties.change = '-0.1'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'RIGHT_ARROW', 'PRESS', alt = True)
    kmi.properties.change = '0.1'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'LEFT_ARROW', 'PRESS', alt = True, shift = True)
    kmi.properties.change = '-0.01'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'RIGHT_ARROW', 'PRESS', alt = True, shift = True)
    kmi.properties.change = '0.01'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'LEFT_ARROW', 'PRESS', ctrl = True, alt = True, shift = True)
    kmi.properties.change = '0.0'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'RIGHT_ARROW', 'PRESS', ctrl = True, alt = True, shift = True)
    kmi.properties.change = '1.0'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'NUMPAD_0', 'PRESS', ctrl = True, alt = True, shift = True)
    kmi.properties.change = '0.0'
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(ChangeMixFactor.bl_idname, 'NUMPAD_1', 'PRESS', ctrl = True, alt = True, shift = True)
    kmi.properties.change = '1.0'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.call_menu', 'SLASH', 'PRESS')
    kmi.properties.name = AddReroutesMenu.bl_idname
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.call_menu', 'EQUAL', 'PRESS', shift = True)
    kmi.properties.name = NodeAlignMenu.bl_idname
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.call_menu', 'F', 'PRESS', shift = True)
    kmi.properties.name = LinkActiveToSelectedMenu.bl_idname
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.call_menu', 'C', 'PRESS', shift = True)
    kmi.properties.name = CopyNodePropertiesMenu.bl_idname
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(NodesClearLabel.bl_idname, 'L', 'PRESS', alt = True)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.call_menu', 'S', 'PRESS', shift = True)
    kmi.properties.name = ReroutesSwitchesSwapMenu.bl_idname
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(NodesAddTextureSetup.bl_idname, 'T', 'PRESS', ctrl = True)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(SelectParentChildren.bl_idname, 'RIGHT_BRACKET', 'PRESS')
    kmi.properties.option = 'Children'
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new(SelectParentChildren.bl_idname, 'LEFT_BRACKET', 'PRESS')
    kmi.properties.option = 'Parent'
    addon_keymaps.append((km, kmi))
    
    bpy.types.NODE_MT_select.append(select_parent_children_buttons)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.NODE_MT_select.remove(select_parent_children_buttons)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()