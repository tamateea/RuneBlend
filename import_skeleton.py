import math

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



        return base
    except IOError:
        print("Error: Failed to read file.")


def to_vector(data):
    return mathutils.Vector((data.x, -data.z, data.y))

def create_armature(base, obj):
    tmp_rig_name = "imported_rig"
    armature = bpy.data.armatures.new("armature")
    armature.name = "imported_armature"

    # create the object and link to the scene
    new_rig = bpy.data.objects.new(tmp_rig_name, armature)
    bpy.context.scene.collection.objects.link(new_rig)
    bpy.context.view_layer.objects.active = new_rig
    new_rig.show_in_front = True
    new_rig.select_set(state=True)
    bpy.ops.object.mode_set(mode='EDIT')

    bones = base.skeletal_base.bones


    bone_list = [0] * len(bones)

    for bone in bones:
        bone_id = bone.id
        #we only need the location of the bones, since the heirarchy has already been calculated
        #by multiplying bone matrices, so the location expresses it's rotation/scale
        loc, rot, scale = bone.get_model_matrix(0).decompose()
        name = f"Bone_{bone_id}"
        new_bone = armature.edit_bones.new(name)
        new_bone.use_inherit_rotation = True
        new_bone.use_connect = False
        bone_list[bone_id] = new_bone
        # set the head and tail, since this is the only data we have to go by
        new_bone.tail = to_vector(loc)
        new_bone.head = to_vector(loc)

    for bone in bones:
        bone_id = bone.id
        parent_id = bone.parent_id
        edit_bone = bone_list[bone_id]

        if parent_id >= 0:
            #set the head of the bone to the parents tail
            #some of these might need to be changed
            edit_bone.parent = bone_list[parent_id]
            edit_bone.head = bone_list[parent_id].tail
        else:
            #this is the parent bone, we need to set offset it's position so it's not deleted
            edit_bone.head = edit_bone.tail + mathutils.Vector((0.1, 0, 0))
            edit_bone.use_connect = False

        # blender removes bones with a length of 0 so add to it so it's not deleted until we figure out what it does
        if edit_bone.length == 0:
            edit_bone.head = edit_bone.tail + mathutils.Vector((0.1, 0, 0))


    bpy.ops.object.mode_set(mode='POSE')
    for pose_bone in new_rig.pose.bones:
        pose_bone.rotation_mode = 'XYZ'
    bpy.ops.object.mode_set(mode='EDIT')
    mesh_obj = obj
    bpy.context.object['base_length'] = base.length
    mesh_obj.parent = new_rig
    mesh_obj.parent_type = 'OBJECT'
    armature_modifier = mesh_obj.modifiers.new(name='Armature', type='ARMATURE')
    armature_modifier.object = new_rig
    armature_modifier.use_vertex_groups = True  # This ensures that pre-defined vertex groups are used

def load(self):
    read_skeleton(self.filepath)

    return {"FINISHED"}


