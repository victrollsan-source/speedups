import bpy
import os
import time
from bpy.props import BoolProperty, StringProperty
from bpy.props import IntProperty


class SPEEDUPSPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    # Master toggle for the purge options
    show_create_textures_options: bpy.props.BoolProperty(
        name="Show Create Textures Options",
        description="Toggle the visibility of the Create Textures options in the UI",
        default=True
    )
    # Master toggle for the multi-export options
    show_multi_export_options: bpy.props.BoolProperty(
        name="Show Multi-Export Options",
        description="Enable or disable the multi-export options in the UI",
        default=True
    )
    # Master toggle for the purge options
    show_purge_options: bpy.props.BoolProperty(
        name="Show Purge Options",
        description="Toggle the visibility of the Purge options in the UI",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_create_textures_options")
        layout.prop(self, "show_multi_export_options")
        layout.prop(self, "show_purge_options")


def propeties():
    """Create the properties for the addon"""
    # Multibake props
    bpy.types.Scene.diffuse_prop = BoolProperty(
        name="Diffuse Texture",
        description="Select to include Diffuse Texture",
        default=True  # Initial value
    )
    bpy.types.Scene.roughness_prop_with_update = BoolProperty(
    name="Roughness Texture",
    description="Select to include Roughness Texture",
    default=True  # Initial value
    )
    bpy.types.Scene.normal_prop = BoolProperty(
        name="Normal Texture",
        description="Select to include Normal Texture",
        default=True  # Initial value
    )
    bpy.types.Scene.metalness_prop = BoolProperty(
        name="Metalness Texture",
        description="Select to include Metalness Texture",
        default=True  # Initial value
    )
    bpy.types.Scene.ao_prop = BoolProperty(
        name="AO Texture",
        description="Select to include AO Texture",
        default=False  # Initial value
    )
    bpy.types.Scene.opacity_prop = BoolProperty(
        name="Opacity Texture",
        description="Select to include Opacity Texture",
        default=False  # Initial value
    )
    bpy.types.Scene.emissive_prop = BoolProperty(
        name="Emissive Texture",
        description="Select to include Emissive Texture",
        default=False  # Initial value
    )

    # Multiexport props
    bpy.types.Scene.alembic_prop = BoolProperty(
        name="Alembic Export",
        description="Select to include Alembic Export",
        default=True  # Initial value
    )
    bpy.types.Scene.usd_prop = BoolProperty(
        name="USD Export",
        description="Select to include USD Export",
        default=True  # Initial value
    )
    bpy.types.Scene.obj_prop = BoolProperty(
        name="OBJ Export",
        description="Select to include OBJ Export",
        default=True  # Initial value
    )
    bpy.types.Scene.ply_prop = BoolProperty(
        name="PLY Export",
        description="Select to include PLY Export",
        default=True  # Initial value
    )
    bpy.types.Scene.fbx_prop = BoolProperty(
        name="FBX Export",
        description="Select to include FBX Export",
        default=True  # Initial value
    )
    bpy.types.Scene.glb_prop = BoolProperty(
        name="GLB Export",
        description="Select to include GLB Export",
        default=True  # Initial value
    )

    # Bake Material props
    bpy.types.Scene.texture_size_prop = IntProperty(
        name="Texture Size",
        description="Sets the size of the texture to generate",
        default=4096,
        min=1,
    )
    bpy.types.Scene.texture_name_prop = StringProperty(
        name="Texture Name",
        description="Sets the name of the texture to generate",
        default="Texture"
    )


def get_all_principled_nodes(node_tree, principled_list=None):
    """Recursively finds all Principled BSDF nodes in a given node tree."""
    if principled_list is None:
        principled_list = []

    if not node_tree:
        return principled_list

    for node in node_tree.nodes:
        # Check if the node is a Principled BSDF
        if node.type == 'BSDF_PRINCIPLED':
            principled_list.append(node)
            
        # If the node is a group, search inside its internal node_tree
        elif node.type == 'GROUP' and node.node_tree:
            get_all_principled_nodes(node.node_tree, principled_list)

    return principled_list


def create_bake_material(float= True, Type: str = "_Bake"):
    """Create a new material for baking and assign a new image texture to it"""
    img = None
    w = bpy.context.scene.texture_size_prop
    h = bpy.context.scene.texture_size_prop
    if bpy.context.object:
        # Get the active selected object
        obj = bpy.context.active_object
        image_name = obj.name + Type
        img = bpy.data.images.new(image_name, w, h, alpha=True, float_buffer=float)
        img.generated_color = (0, 0, 0, 0)
        img.colorspace_settings.name = 'sRGB'
        bpy.data.images[image_name].use_generated_float = float
        

        # Check if an object is selected and is of a type that can have materials (like MESH)
        if obj is not None and hasattr(obj, 'material_slots'):
            # The length of the material_slots list indicates the number of slots
            if len(obj.material_slots) <= 0:
                new_material = bpy.data.materials.new(name=image_name)
                new_material.use_nodes = True
                # Get material
                mat = bpy.data.materials.get(image_name)
                if mat is None:
                    # create material
                    mat = bpy.data.materials.new(name=image_name)

                # Assign it to object
                obj.data.materials.append(mat)
        else:
            return "No suitable object selected or the object type does not support materials."
        
        unrepeated_materials = []
        seen = set()

        for mat in obj.data.materials:
            if mat not in seen:
                unrepeated_materials.append(mat)
                seen.add(mat)
        
        for mat in unrepeated_materials:

            node_tree = mat.node_tree
            nodes = node_tree.nodes

            texture_node = nodes.new('ShaderNodeTexImage')
            texture_node.name = 'Bake_node'
            texture_node.location = (-200, 600)
            texture_node.select = True
            nodes.active = texture_node
            texture_node.image = img


        bpy.context.view_layer.objects.active = obj
        return f"Image Node with the image: '{img.name}' successfully created."
    else:
        return "No context object"


def remove_bake_material():
    if bpy.context.object:
        # Get the active selected object
        obj = bpy.context.active_object
        # Check if an object is selected and is of a type that can have materials (like MESH)
        if obj is not None and hasattr(obj, 'material_slots'):
            # The length of the material_slots list indicates the number of slots
            if len(obj.material_slots) > 0:
                has_assigned_material = any(slot.material is not None for slot in obj.material_slots)
                
                if has_assigned_material:
                    print(f"The selected object '{obj.name}' has at least one material assigned.")
                else:
                    print(f"The selected object '{obj.name}' has material slots, but no material data-block is assigned to them.")
            else:
                print(f"The selected object '{obj.name}' has no material slots.")
        else:
            return "No suitable object selected or the object type does not support materials."
        
        unrepeated_materials = []
        seen = set()

        for mat in obj.data.materials:
            if mat not in seen:
                unrepeated_materials.append(mat)
                seen.add(mat)
        
        node_name_to_delete = 'Bake_node'

        for mat in unrepeated_materials:
            node_tree = mat.node_tree
            nodes = node_tree.nodes

            badnode = nodes.get(node_name_to_delete)
            if badnode is not None:
                nodes.remove(badnode)
                return (f"Node '{node_name_to_delete}' found and deleted from material '{mat}' .")                
            else:
                return (f"Node '{node_name_to_delete}' not found in material '{mat}' .")


    else:
        return "No context object"



def get_current_image():

    # Obtain the active node of the active material of the active object
    node = bpy.context.active_object.active_material.node_tree.nodes.active

    # Verify image node and obtain data
    if node.type == 'TEX_IMAGE':
        current_image = node.image
        return current_image.name
    else:
        print("The active node is not image type.")
        return "The active node is not image type."


def save_image(current_image_name):
    """Save the image to the same directory as the .blend file"""
    filepath = bpy.data.filepath

    img = bpy.data.images[current_image_name]

    if filepath:
        # Extract the dirname from the full path
        dirname = os.path.dirname(filepath)
        img_path = dirname + "\\" + current_image_name + ".png"
        
        img.filepath_raw = img_path
        img.file_format = 'PNG'

        img.save()

    else:
        print("The current Blender file is not saved.")


def has_metalic_link(mat):
    """Check if the material has a metalness link"""
    if mat and mat.use_nodes:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            input_socket = principled_node.inputs["Metallic"]
            if input_socket:
                if input_socket.links: # Check if a link exists
                    return True
                else:
                    return False
            else:
                print(f"The input '{input_socket.name}' does not have a metalness link.")
                return False


def has_emission_color_link(mat):
    """Check if the material has a emission color link"""
    if mat and mat.use_nodes:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            input_socket = principled_node.inputs["Emission Color"]
            if input_socket:
                if input_socket.links: # Check if a link exists
                    return True
                else:
                    return False
            else:
                print(f"The input '{input_socket.name}' does not have a emission color link.")
                return False


def has_emission_link(mat):
    """Check if the material has a emission link"""
    if mat and mat.use_nodes:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            input_socket = principled_node.inputs["Emission Strength"]
            if input_socket:
                if input_socket.links: # Check if a link exists
                    return True
                else:
                    return False
            else:
                print(f"The input '{input_socket.name}' does not have a emission link.")
                return False



def metallicLink_to_emissionLink(mat):
    """Connect the metalness link to emission link and set the emission strength to 1"""
    node_tree = mat.node_tree
    for principled_node in get_all_principled_nodes(node_tree):
        node_tree = principled_node.id_data
        input_socket = principled_node.inputs["Metallic"]
        if input_socket.links: # Check if a link exists
            link_to_remove = input_socket.links[0]
        else:
            link_to_remove = None
            print("There is no METALLIC link to remove")
        if link_to_remove:
            connected_socket = link_to_remove.from_socket
            metalness_output_socket = connected_socket
            emission_input_socket = principled_node.inputs.get("Emission Color")
            node_tree.links.new(metalness_output_socket, emission_input_socket)
            principled_node.inputs["Emission Strength"].default_value = 1
            node_tree.links.remove(link_to_remove)


def emissionColorLink_to_bEmissionColorLink(mat):
    """ Remove the emission color link and set the emission color to white with strength of 1"""
    node_tree = mat.node_tree
    for principled_node in get_all_principled_nodes(node_tree):
        node_tree = principled_node.id_data
        input_socket = principled_node.inputs["Emission Color"]
        if input_socket.links: # Check if a link exists
            link_to_remove = input_socket.links[0]
        else:
            link_to_remove = None
            print("There is no EMISSION COLOR link to remove")
        if link_to_remove:
            connected_socket = link_to_remove.from_socket
            emissiveColor_output_socket = connected_socket
            principled_node.inputs["Emission Color"].default_value = (1, 1, 1, 1)
            node_tree.links.remove(link_to_remove)
            return emissiveColor_output_socket


def emissionStrengthLink_to_bEmissionStrengthLink(mat):
    """ Remove the emission link and set the emission strength to white with strength of 1"""
    node_tree = mat.node_tree
    for principled_node in get_all_principled_nodes(node_tree):
        node_tree = principled_node.id_data
        input_socket = principled_node.inputs["Emission"]
        if input_socket.links: # Check if a link exists
            link_to_remove = input_socket.links[0]
        else:
            link_to_remove = None
            print("There is no EMISSION link to remove")
        if link_to_remove:
            connected_socket = link_to_remove.from_socket
            emmissiveStrength_output_socket = connected_socket
            principled_node.inputs["Emission Strength"].default_value = 0
            node_tree.links.remove(link_to_remove)
            return emmissiveStrength_output_socket


def emissionLink_to_metallicLink(mat, metallic: bool):
    """Connect the emission link to metalness link"""
    if metallic == True:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            node_tree = principled_node.id_data
            input_socket = principled_node.inputs["Emission Color"]
            if input_socket.links: # Check if a link exists
                link_to_remove = input_socket.links[0]
            else:
                link_to_remove = None
                print("There is no EMISSION link to remove")
            if link_to_remove:
                connected_socket = link_to_remove.from_socket
                metalness_output_socket = connected_socket
                metallic_input_socket = principled_node.inputs.get("Metallic")
                node_tree.links.new(metalness_output_socket, metallic_input_socket)
                principled_node.inputs["Emission Strength"].default_value = 0
                node_tree.links.remove(link_to_remove)


def backups(obj, metallic_BK, emit_color_BK, emit_BK, metallic_L_BK_b):
    """Backup the metallic and emission values and links, set metallic to 0 and emission to metallic value"""
    # For every material in the object
    unrepeated_materials = []
    seen = set()

    for mat in obj.data.materials:
        if mat not in seen:
            unrepeated_materials.append(mat)
            seen.add(mat)
    
    # For every material in unrepeated_materials
    i = 0
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            metallic_BK.append(principled_node.inputs["Metallic"].default_value)
            emit_color_BK.append(list(principled_node.inputs["Emission Color"].default_value))
            emit_BK.append(principled_node.inputs["Emission Strength"].default_value)
            principled_node.inputs["Emission Strength"].default_value = 0.0

            metallic_L_BK_b.append(has_metalic_link(mat))
            principled_node.inputs["Metallic"].default_value = 0
            i = i + 1
        
    i = 0
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            principled_node.inputs["Emission Color"].default_value = (1, 1, 1, 1)
            principled_node.inputs["Emission Strength"].default_value = metallic_BK[i]
            if metallic_L_BK_b[i] == True:
                metallicLink_to_emissionLink(mat)
            i = i + 1


def restore_backups(obj, metallic_backups, metallicLinks_backups, emit_color_backups, emit_backups):
    """Restore the metallic and emission values and links from backups"""
    index = 0
    # For every material in the object
    unrepeated_materials = []
    seen = set()

    for mat in obj.data.materials:
        if mat not in seen:
            unrepeated_materials.append(mat)
            seen.add(mat)
    
    
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            principled_node.inputs["Emission Color"].default_value = emit_color_backups[index]
            principled_node.inputs["Emission Strength"].default_value = emit_backups[index]
            principled_node.inputs["Metallic"].default_value = metallic_backups[index]
            if metallicLinks_backups[index] == True:
                emissionLink_to_metallicLink(mat, metallic=metallicLinks_backups[index])
            index = index + 1


def backups_opacity(obj, opacity_BKs, emit_BK_opacity, emit_strength):
    """Backup the emission values for opacity baking, set emission to 1"""

    # For every material in the object
    unrepeated_materials = []
    seen = set()

    for mat in obj.data.materials:
        if mat not in seen:
            unrepeated_materials.append(mat)
            seen.add(mat)
    
    index = 0
    # For every material in unrepeated_materials
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            opacity_BKs.append(principled_node.inputs["Alpha"].default_value)
            emit_BK_opacity.append(list(principled_node.inputs["Emission Color"].default_value))
            emit_strength.append(principled_node.inputs["Emission Strength"].default_value)
            principled_node.inputs["Emission Strength"].default_value = 1
            index = index + 1
    
    index = 0
    # For every material in the object
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            principled_node.inputs["Emission Color"].default_value = (opacity_BKs[index], opacity_BKs[index], opacity_BKs[index], 1)
            index = index + 1

def restore_backups_opacity(obj, emit_BKs_opacity, emit_strength):
    index = 0
    # For every material in the object
    unrepeated_materials = []
    seen = set()

    for mat in obj.data.materials:
        if mat not in seen:
            unrepeated_materials.append(mat)
            seen.add(mat)

    # For every material in unrepeated_materials
    for mat in unrepeated_materials:
        node_tree = mat.node_tree
        for principled_node in get_all_principled_nodes(node_tree):
            principled_node.inputs["Emission Color"].default_value = emit_BKs_opacity[index]
            principled_node.inputs["Emission Strength"].default_value = emit_strength[index]
            index = index + 1
    pass



def baking_diffuse():
    """Bake the diffuse texture"""
    print("Baking Diffuse")

    create_bake_material(False, "_Diffuse")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'sRGB'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("bake DIFFUSE finished")


def baking_normal():
    """Bake the normal texture"""
    print("Baking Normal")

    create_bake_material(True, "_Normal")

    current_image_name = get_current_image()
    
    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'NORMAL'
    bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("Bake NORMAL finished")


def baking_roughness():
    """Bake the roughness texture"""
    print("Baking Roughness")

    create_bake_material(False, "_Roughness")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
    bpy.ops.object.bake(type='ROUGHNESS', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("bake ROUGHNESS finished")


def baking_metalness():
    """Bake the metalness texture"""
    print("Baking Metalness")

    create_bake_material(False, "_Metalness")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.ops.object.bake(type='EMIT', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()
    
    print("bake METALNESS finished")


def baking_ao():
    """Bake the Ambient Occlution texture"""
    print("Baking Ambient Occlusion")

    create_bake_material(False, "_AO")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'AO'
    bpy.ops.object.bake(type='AO', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("bake AO finished")


def baking_opacity():
    """Bake the opacitty texture"""
    print("Baking Opacity")

    create_bake_material(False, "_Opacity")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.ops.object.bake(type='EMIT', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("bake OPACITY finished")


def baking_emissive():
    """Bake the metalness texture"""
    print("Baking Emissive")

    create_bake_material(False, "_Emissive")

    current_image_name = get_current_image()

    bpy.data.images[current_image_name].colorspace_settings.name = 'Non-Color'
    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.ops.object.bake(type='EMIT', save_mode='EXTERNAL')
    save_image(current_image_name=current_image_name)

    remove_bake_material()

    print("bake EMISSIVE finished")


# Selection to Active False
def multi_bake_state_false():
    """Bake the active object only"""
    selected_objects = bpy.context.selected_objects

    metallic_BK = []
    emitColor_BK = []
    emit_BK = []
    metallic_L_BK_b = []

    opacity_BK = []
    emit_BK_opacity = []
    emit_stength = []

    i = 0
    for obj in selected_objects:
        metallic_BK.append([])
        emitColor_BK.append([])
        emit_BK.append([])
        metallic_L_BK_b.append([])


        scene = bpy.context.scene

        if scene.diffuse_prop:
            backups(obj, metallic_BK[i], emitColor_BK[i], emit_BK[i], metallic_L_BK_b[i])
            baking_diffuse()
            restore_backups(obj, metallic_BK[i], metallic_L_BK_b[i], emitColor_BK[i], emit_BK[i])
        if scene.normal_prop:
            baking_normal()
        if scene.roughness_prop_with_update:
            baking_roughness()
        if scene.metalness_prop:
            backups(obj, metallic_BK[i], emitColor_BK[i], emit_BK[i], metallic_L_BK_b[i])
            baking_metalness()
            restore_backups(obj, metallic_BK[i], metallic_L_BK_b[i], emitColor_BK[i], emit_BK[i])
        if scene.ao_prop:
            baking_ao()
        

        if scene.opacity_prop:
            opacity_BK.append([])
            emit_BK_opacity.append([])
            emit_stength.append([])
            backups_opacity(obj, opacity_BK[i], emit_BK_opacity[i], emit_stength[i])
            baking_opacity()
            restore_backups_opacity(obj, emit_BK_opacity[i], emit_stength[i])

        if scene.emissive_prop:
            baking_emissive()
        i = i + 1


# Selection to Active True
def multi_bake_state_true():
    """Bake the active object using the other selected objects for baking"""

    # Get the list of all selected objects and the single active object
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.active_object
    scene = bpy.context.scene

    metallic_BK = []
    emit_color_BK = []
    emit_BK = []
    metallic_L_BK_b = []


    opacity_BK = []
    emit_BK_opacity = []
    emit_BK = []

    # Check if there are multiple objects selected
    i = 0
    for obj in selected_objects:
        if obj != active_object:
            metallic_BK.append([])
            emit_color_BK.append([])
            emit_BK.append([])
            metallic_L_BK_b.append([])

            backups(obj, metallic_BK[i], emit_color_BK[i], emit_BK[i], metallic_L_BK_b[i])

            i = i + 1
    for obj in selected_objects:
        if obj == active_object:
            if scene.diffuse_prop:
                baking_diffuse()
            if scene.normal_prop:
                baking_normal()
            if scene.roughness_prop_with_update:
                baking_roughness()
            if scene.metalness_prop:
                baking_metalness()
            if scene.ao_prop:
                baking_ao()
    i = 0
    for obj in selected_objects:
        if obj != active_object:
            restore_backups(obj, metallic_BK[i], metallic_L_BK_b[i], emit_color_BK[i], emit_BK[i])
            i = i + 1

    if scene.opacity_prop:
        i = 0
        for obj in selected_objects:
            if obj != active_object:
                opacity_BK.append([])
                emit_BK_opacity.append([])
                emit_BK.append([])
                backups_opacity(obj, opacity_BK[i], emit_BK_opacity[i], emit_BK[i])
                i = i + 1
        for obj in selected_objects:
            if obj == active_object:
                    baking_opacity()
        i = 0
        for obj in selected_objects:
            if obj != active_object:
                restore_backups_opacity(obj, emit_BK_opacity[i], emit_BK[i])
                i = i + 1

    if scene.emissive_prop:
        for obj in selected_objects:
            if obj == active_object:
                    baking_emissive()


def create_textures():
    """Pack the textures to the blend file and creates the textures folder in disc"""
    bpy.ops.file.pack_all()
    bpy.ops.file.unpack_all(method='USE_LOCAL')
    bpy.ops.file.pack_all()
    return "Textures pack and folder texture created"


def multi_export():
    """Exports as various formats using the name of the blend file name"""
    # Get the absolute path to the currently open .blend file
    filepath = bpy.data.filepath

    # Check if the file is saved (filepath will be empty if not saved)
    if filepath:
        # Extract the filename from the full path
        filename = os.path.basename(filepath)
        # Extract the dirname from the full path
        dirname = os.path.dirname(filepath)
        parts = filename.split('.')
        path_alembic = dirname + "\\" + parts[0] + ".abc"
        path_usd = dirname + "\\" + parts[0] + ".usdc"
        path_obj = dirname + "\\" + parts[0] + ".obj"
        path_ply = dirname + "\\" + parts[0] + ".ply"
        path_fbx = dirname + "\\" + parts[0] + ".fbx"
        path_glb = dirname + "\\" + parts[0] + ".glb"

        # Export the object(s)
        bpy.ops.wm.alembic_export(filepath=path_alembic)
        bpy.ops.wm.usd_export(filepath=path_usd)
        bpy.ops.wm.obj_export(filepath=path_obj)
        bpy.ops.wm.ply_export(filepath=path_ply)
        bpy.ops.export_scene.fbx(filepath=path_fbx)
        bpy.ops.export_scene.gltf(filepath=path_glb)

        return "Multiexport finished"
    else:
        return "The current Blender file is not saved."




#########################################
# Operators
#########################################


class SPEEDUPS_OT_SuperPurge(bpy.types.Operator):
    """Purge all the unused data blocks in the blend file"""
    bl_idname = "file.super_purge"
    bl_label = "Super Purge"
    bl_description = "Purge all the unused data blocks in the blend file"


    def execute(self, context):
        bpy.ops.outliner.orphans_purge()
        return {'FINISHED'}


class SPEEDUPS_OT_Multiexport(bpy.types.Operator):
    """Exports as various formats using the name of the blend file name"""
    bl_idname = "wm.export_multi"
    bl_label = "Multi export"
    bl_description = "Exports as usdc, obj, ply, fbx, glb using the name of the blend file name"


    def execute(self, context):
        message = multi_export()
        self.report({'INFO'}, message)
        return {'FINISHED'}


class SPEEDUPS_OT_CreateTextures(bpy.types.Operator):
    """Pack the textures to the blend file and creates the textures folder in disc"""
    bl_idname = "file.create_textures"
    bl_label = "Create Textures"
    bl_description = "Pack the textures to the blend file and creates the textures folder in disc"


    def execute(self, context):
        message = create_textures()
        self.report({'INFO'}, message)
        return {'FINISHED'}


class SPEEDUPS_OT_MultiBake(bpy.types.Operator):
    """Bakes textures for PBR with previus set up"""
    bl_idname = "object.multi_bake"
    bl_label = "Multi Bake"
    bl_description = "Bake Multiple Textures"


    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        for obj in selected_objects:
            if obj.type != 'MESH':
                self.report({'WARNING'}, f"Object {obj.name} is not a mesh, please select only mesh objects")
                return {'CANCELLED'}
            
        current_engine = bpy.context.scene.render.engine
        # Check if the engine is "CYCLES"
        if current_engine == "CYCLES":
            start = time.perf_counter()
            if (bpy.context.scene.render.bake.use_selected_to_active == False):
                multi_bake_state_false()
            if (bpy.context.scene.render.bake.use_selected_to_active == True):
                if len(selected_objects) > 1:
                    multi_bake_state_true()
                elif len(selected_objects) == 1 and active_object:
                    self.report({'WARNING'}, "Only the active object is selected.")
                    return {'CANCELLED'}
                else:
                    self.report({'WARNING'}, "No objects are selected.")
                    return {'CANCELLED'}
            end = time.perf_counter()
            execution_time =  end - start
            self.report({'INFO'}, f"Baking Complete in {execution_time:.6f} seconds")
            return {'FINISHED'}
        else:
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'GPU'
            self.report({'INFO'}, "Changing to cycles with GPU enabled if posible")
            return {'FINISHED'}



#########################################
# UI Panels
#########################################


# CATEGORYY_MT_name
class SPEEDUPS_MT_F5(bpy.types.Menu):
    bl_idname = "SPEEDUPS_MT_F5_menu"
    bl_label = "Speed Ups"

    def draw(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        layout = self.layout
        # Add operators, properties, or sub-menus here
        layout.operator("object.multi_bake", text="Multi Bake")
        if addon_prefs.show_create_textures_options:
            layout.operator("file.create_textures", text="Create Textures Folder")
        if addon_prefs.show_multi_export_options:
            layout.operator("wm.export_multi", text="Multi Export", icon="EXPORT")
        if addon_prefs.show_purge_options:
            layout.operator("file.super_purge", text="Super Purge", icon="TRASH")


# CATEGORYY_PT_name
class PROPERTIES_PT_MainPanel(bpy.types.Panel):
    bl_label = "Speed Ups Main Panel"
    bl_idname = "SPEEDUPS_PT_MAINPANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Speed Ups'

    def draw(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        layout = self.layout
        row = layout.row()
        row.label(text= "Press F5 for quick actions", icon="INFO")
        col = layout.column()
        col.operator("object.multi_bake", text="Multi Bake")
        if addon_prefs.show_create_textures_options:
            col = layout.column()
            col.operator("file.create_textures", text="Create Textures Folder")
        if addon_prefs.show_multi_export_options:
            col = layout.column()
            col.operator("wm.export_multi", text="Multi Export", icon="EXPORT")
        if addon_prefs.show_purge_options:
            col = layout.column()
            col.operator("file.super_purge", text="Super Purge", icon="TRASH")


# CATEGORYY_PT_name
class PROPERTIES_PT_textures_selector(bpy.types.Panel):
    """Creates a Panel in the Render properties window"""
    # where to add the panel in the UI
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Speed Ups'
    bl_idname = "PROPERTIES_PT_textures_selector"
    bl_label = "Speed Ups Textures Selector"
    bl_parent_id = "SPEEDUPS_PT_MAINPANEL"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'CYCLES'}


    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'


    def draw(self, context):
        """define the layout of the panel"""
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "diffuse_prop")
        layout.prop(scene, "roughness_prop_with_update")
        layout.prop(scene, "normal_prop")
        layout.prop(scene, "metalness_prop")
        layout.prop(scene, "ao_prop")
        layout.prop(scene, "opacity_prop")
        layout.prop(scene, "emissive_prop")
        pass


# CATEGORYY_PT_name
class PROPERTIES_PT_bake_material(bpy.types.Panel):
    """Creates a Panel in the Render properties window"""
    # where to add the panel in the UI
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Speed Ups'
    bl_idname = "VIEW3D_PT_bake_material_panel"
    bl_label = "Bake Material Options"
    bl_idname = "VIEW3D_PT_custom_panel"
    bl_parent_id = "SPEEDUPS_PT_MAINPANEL"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'CYCLES'}


    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

    def draw(self, context):
        """define the layout of the panel"""
        layout = self.layout
        scene = context.scene
        cycles = scene.cycles
        bake_settings = scene.render.bake

        layout.label(text="Options for baking:")
        layout.prop(scene, "texture_name_prop", text="Texture Prefix")
        layout.prop(scene, "texture_size_prop", text="Texture Size")
        col = layout.column()
        col.label(text="Render Max Samples:")
        col.prop(cycles, "samples", text="")
        col = layout.column()
        col.prop(scene.render.bake, "use_selected_to_active", text="Selected to Active")

        col.prop(bake_settings, "use_clear", text="Clear Image")
        col.prop(bake_settings, "margin", text="Margin Size")




# CATEGORYY_PT_name
class PROPERTIES_PT_multi_export(bpy.types.Panel):
    """Creates a Panel in the Render properties window"""
    # where to add the panel in the UI

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Speed Ups'
    bl_idname = "VIEW3D_PT_multi_export_panel"
    bl_label = "Multi Export Options"
    bl_parent_id = "SPEEDUPS_PT_MAINPANEL"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        # Access the preference toggle
        addon_prefs = context.preferences.addons[__name__].preferences
        return addon_prefs.show_multi_export_options


    def draw(self, context):
        # This only runs if poll() returns True
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "alembic_prop")
        layout.prop(scene, "usd_prop")
        layout.prop(scene, "obj_prop")
        layout.prop(scene, "ply_prop")
        layout.prop(scene, "fbx_prop")
        layout.prop(scene, "glb_prop")
        pass


addon_keymaps = []


classes = [
    SPEEDUPSPreferences,
    SPEEDUPS_OT_SuperPurge,
    SPEEDUPS_OT_Multiexport,
    SPEEDUPS_OT_CreateTextures,
    SPEEDUPS_OT_MultiBake,
    SPEEDUPS_MT_F5,
    PROPERTIES_PT_MainPanel,
    PROPERTIES_PT_textures_selector,
    PROPERTIES_PT_bake_material,
    PROPERTIES_PT_multi_export,
    ]


#########################################
# Register and Unregister
#########################################


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu", type='F5', value='PRESS')
        kmi.properties.name = SPEEDUPS_MT_F5.bl_idname
        addon_keymaps.append((km, kmi))
    propeties()


def unregister():
    print("SpeedUps Unregister")
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    # multibake props
    del bpy.types.Scene.diffuse_prop
    del bpy.types.Scene.roughness_prop_with_update
    del bpy.types.Scene.normal_prop
    del bpy.types.Scene.metalness_prop
    del bpy.types.Scene.ao_prop
    del bpy.types.Scene.opacity_prop
    del bpy.types.Scene.emissive_prop
    # multiexport props
    del bpy.types.Scene.alembic_prop
    del bpy.types.Scene.usd_prop
    del bpy.types.Scene.obj_prop
    del bpy.types.Scene.ply_prop
    del bpy.types.Scene.fbx_prop
    del bpy.types.Scene.glb_prop

if __name__ == "__main__":
    register()
