import bpy
import os


def get_by_name(name):
    return bpy.data.materials.get(name)


class Materials:

    @staticmethod
    def create_or_get_palette_material(obj):
        name = "palette"
        material = get_by_name(name)
        if material:
            if name in obj.data.materials:
                return material
            else:
                obj.data.materials.append(material)
                return material

        texture = bpy.data.textures.new("Texture", type='IMAGE')
        texture_path = os.path.join(os.path.dirname(__file__), "./textures/palette.png")

        # Load the image
        image = bpy.data.images.load(filepath=texture_path, check_existing=True)
        texture.image = image

        # Create a material and assign the texture
        material = bpy.data.materials.new("palette")
        material.use_nodes = True
        material.node_tree.nodes.clear()
        material_output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')

        # Create the Principled BSDF shader node
        principled_bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_bsdf.inputs['Specular'].default_value = 0.0
        principled_bsdf.inputs['Roughness'].default_value = 1.0
        material.use_backface_culling = True

        material.node_tree.links.new(texture_node.outputs["Color"], principled_bsdf.inputs["Base Color"])
        material.node_tree.links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

        # Check if "Alpha" or "Alpha 1" exists and link it
        if "Alpha" in material_output.inputs:
            material.node_tree.links.new(texture_node.outputs["Alpha"], material_output.inputs["Alpha"])
        elif "Alpha 1" in material_output.inputs:
            material.node_tree.links.new(texture_node.outputs["Alpha"], material_output.inputs["Alpha 1"])

        texture_node.image = image
        obj.data.materials.append(material)
        return material

    @staticmethod
    def create_or_get_alpha_palette_material(obj, alpha):
        name = f"palette_alpha_{alpha}"
        material = get_by_name(name)
        if material:
            if name in obj.data.materials:
                return material
            else:
                obj.data.materials.append(material)
                return material

        # Assign the image to the UV texture
        texture = bpy.data.textures.new("Texture", type='IMAGE')
        texture_path = os.path.join(os.path.dirname(__file__), "./textures/palette.png")

        # Load the image
        image = bpy.data.images.load(filepath=texture_path, check_existing=True)
        texture.image = image

        # Create a material and assign the texture
        material = bpy.data.materials.new(f"palette_alpha_{alpha}")
        material.use_nodes = True
        material.node_tree.nodes.clear()
        material_output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')

        # Create the Principled BSDF shader node
        principled_bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_bsdf.inputs['Specular'].default_value = 0.0
        principled_bsdf.inputs['Roughness'].default_value = 1.0
        material.use_backface_culling = True
        material.blend_method = 'BLEND'
        alpha = 1.0 - (alpha / 255)
        principled_bsdf.inputs['Alpha'].default_value = alpha

        material.node_tree.links.new(texture_node.outputs["Color"], principled_bsdf.inputs["Base Color"])
        material.node_tree.links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

        # Check if "Alpha" or "Alpha 1" exists and link it
        if "Alpha" in material_output.inputs:
            material.node_tree.links.new(texture_node.outputs["Alpha"], material_output.inputs["Alpha"])
        elif "Alpha 1" in material_output.inputs:
            material.node_tree.links.new(texture_node.outputs["Alpha"], material_output.inputs["Alpha 1"])

        texture_node.image = image
        obj.data.materials.append(material)
        return material

    @staticmethod
    def create_or_get_runescape_texture_material(obj, texture_id):
        name = "text_{}".format(texture_id)
        material = get_by_name(name)
        if material:
            if name in obj.data.materials:
                return material
            else:
                obj.data.materials.append(material)
                return material

        texture = bpy.data.textures.new("Texture", type='IMAGE')
        texture_path = os.path.join(os.path.dirname(__file__), "./textures/{}.png".format(texture_id))

        # Load the image
        image = bpy.data.images.load(filepath=texture_path, check_existing=True)
        texture.image = image

        # Create a material and assign the texture
        material = bpy.data.materials.new("text_{}".format(texture_id))
        material.use_nodes = True
        material.node_tree.nodes.clear()
        material_output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')

        # Create the Principled BSDF shader node
        principled_bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_bsdf.inputs['Specular'].default_value = 0.0
        principled_bsdf.inputs['Roughness'].default_value = 1.0
        material.use_backface_culling = True
        material.blend_method = 'CLIP'

        # Connect the texture to the Principled BSDF node
        material.node_tree.links.new(texture_node.outputs["Color"], principled_bsdf.inputs["Base Color"])
        material.node_tree.links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

        # Check if "Alpha" input exists and link it
        if "Alpha" in principled_bsdf.inputs:
            material.node_tree.links.new(texture_node.outputs["Alpha"], principled_bsdf.inputs["Alpha"])

        texture_node.image = image
        obj.data.materials.append(material)
        return material
