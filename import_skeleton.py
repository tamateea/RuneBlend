import bpy
import mathutils
from runeblend.base import Base


def read_skeleton(filepath):
    try:
        with open(filepath, "rb") as file:
            data = file.read()

        base = Base()
        base.decode(base, data)

        # Switch to OBJECT mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Select the active object
        obj = bpy.context.active_object
        obj.select_set(True)

        if obj and obj.type == 'MESH':
            armature_obj = create_armature(base, obj)
            mesh_obj = obj
            mesh_obj.parent = armature_obj
            mesh_obj.parent_type = 'OBJECT'
            armature_modifier = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
            armature_modifier.object = armature_obj
            armature_modifier.use_vertex_groups = True  # This ensures that pre-defined vertex groups are used


        return base
    except IOError:
        print("Error: Failed to read file.")


def create_armature(base, obj):

    bones = base.skeletal_base.bones

    tmp_rig_name = "runescape_rig"

    armature = bpy.data.armatures.new("armature")
    armature.name = "imported_armature"
    # armature.display_type = "STICK"

    # create the object and link to the scene
    new_rig = bpy.data.objects.new(tmp_rig_name, armature)
    bpy.context.scene.collection.objects.link(new_rig)
    bpy.context.view_layer.objects.active = new_rig
    new_rig.show_in_front = True
    new_rig.select_set(state=True)


    bpy.ops.object.mode_set(mode='EDIT')



    bone_list = [0] * len(bones)


    for bone_data in bones:

        index = bone_data.index
        name = f"Bone_{index}"


        new_bone = armature.edit_bones.new(name)
        bone_list[index] = new_bone  # Store bone by name
        pos = bone_data.get_local_translation().to_blender_vector()


        new_bone.head = pos
        new_bone.tail = pos
        new_bone.use_inherit_rotation = True


    for bone_data in bones:
        bone = bone_list[bone_data.index]

        # Set parent bone if applicable
        if bone_data.parent_id >= 0:
            parent_bone = bone_list[bone_data.parent_id]
            bone.parent = parent_bone
            bone.head = parent_bone.tail
        else:
            bone.name = f"bone_{bone_data.index}_root"
            bone.tail += mathutils.Vector((0, 1, 0))
            bone.use_connect = False

        # since blender removes bones with no length
        if bone.length == 0:
            bone.tail += mathutils.Vector((-1, 0, 0))


    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    return new_rig

def load(self):
    read_skeleton(self.filepath)

    return {"FINISHED"}


