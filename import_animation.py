import math
import bpy
import mathutils
from runeblend.byte_buffer import ByteBuffer
import bpy
from enum import Enum


# ################################################################
# There is a bunch of data read here to-do with interpolation.
# But none of it is really utilized inside the actual game engine
# Despite it having code for interpolating curves, it appears all curve
# data has been pre-processsed to bake the interpolation so all keyframes
# are just interpolated linearly.
#
# For a full look at how this system works stand-alone check:
# https://github.com/dennisdev/rs-map-viewer/blob/master/src/rs/model/skeletal/
# ################################################################


def load(self):
    read_animation(self.filepath)
    return {"FINISHED"}


def read_animation(filepath):
    try:
        with open(filepath, "rb") as file:
            data = file.read()
            create_animation(data)
    except IOError:
        print("Error: Failed to read file.")


def create_animation(data):
    bpy.ops.object.mode_set(mode='OBJECT')

    ob = bpy.data.objects["imported_rig"]
    armature = ob.data
    buffer = ByteBuffer(data)

    # not used in the game engine or here
    version = buffer.read_unsigned_byte()

    # not needed here, in the game engine this is just the id
    # of the skeleton that it needs to use, we already have it loaded though.
    skeleton_id = buffer.read_unsigned_short()

    bone_count = len(armature.bones)
    start_frame = buffer.read_unsigned_short()
    end_frame = buffer.read_unsigned_short()

    # this is always 0 in the game engine
    pose_id = buffer.read_unsigned_byte()
    curve_count = buffer.read_unsigned_short()
    length = bpy.context.object['base_length']
    face_curves = [None] * length  # pre-defined property for alpha transforms
    has_alpha_transform = False  # not used yet
    rig = bpy.data.objects["imported_rig"]
    action = bpy.data.actions.new("imported_animation")

    bpy.context.scene.frame_set(1)
    animation_data = {}
    for i in range(curve_count):
        transform_type = get_transform_type_for_id(buffer.read_unsigned_byte())
        bone_index = buffer.readSignedSmart
        curve_type = get_curve_type_for_id(buffer.read_unsigned_byte())
        curve = Curve(i)
        curve.decode(buffer)

        if bone_index not in animation_data:
            animation_data[bone_index] = {}

        if transform_type not in animation_data[bone_index]:
            animation_data[bone_index][transform_type] = {}

        animation_data[bone_index][transform_type][curve_type] = curve

    for bone_index in range(len(animation_data)):
        bone_name = f"Bone_{bone_index}"
        bone = armature.bones.get(bone_name)
        if bone is None:
            # this will skip over face groups used for alpha anims
            print(f"none bone: {bone_index}")
            continue
        for transform_type in animation_data.get(bone_index, {}).keys():
            for curve_type in animation_data.get(bone_index, {}).get(transform_type, {}):
                transformation_type = curve_type.get_transformation_type()
                axis_idx = curve_type.get_axis_index()
                data_path = f'pose.bones["{bone_name}"].{transformation_type}'
                # Create a new FCurve for this bone and curve
                f_curve = action.fcurves.new(data_path, index=axis_idx, action_group=bone_name)
                curve = animation_data[bone_index][transform_type][curve_type]
                for p in curve.points:
                    frame = p.x
                    if curve_type.is_transformation() or curve_type.is_rotation():
                        value = p.y - p.offset
                    else:
                        value = p.y




                    # because runescape is scaled up by 128
                    if curve_type.is_transformation():
                        value *= 0.0078125


                    # runescape -Y = up
                    if curve_type is CurveType.TRANSLATE_Z:
                        value = -value

                    if curve_type is CurveType.ROTATE_Z:
                        value = -value

                    # there is a keyframe added for almost every frame so we don't need any
                    # fancy interpolation
                    keyframe = f_curve.keyframe_points.insert(frame, value, options={'FAST'})
                    keyframe.interpolation = 'BEZIER'
                    # Calculate the handles based on your tangent data
                    tan_in_x = p.tan_in_x
                    tan_out_x = p.tan_out_x
                    tan_in_y = p.tan_in_y
                    tan_out_y = p.tan_out_y

                    # Set the handles
                    keyframe.handle_left = (frame - tan_in_x, value - tan_in_y)
                    keyframe.handle_right = (frame + tan_out_x, value + tan_out_y)

                if transform_type == SkeletalTransformType.ALPHA:
                    has_alpha_transform = True

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    rig.animation_data_create()
    rig.animation_data.action = action


class KeyFramePoint:
    def __init__(self):
        self.offset = 0
        self.x = 0  # this is a frame number
        self.y = 0  # this is the frames value

        # handle data
        self.tan_in_x = 0
        self.tan_in_y = 0
        self.tan_out_x = 0
        self.tan_out_y = 0
        self.next = None

    def decode(self, buffer):
        self.x = buffer.read_short()
        self.y = buffer.read_float()
        self.tan_in_x = buffer.read_float()
        self.tan_in_y = buffer.read_float()
        self.tan_out_x = buffer.read_float()
        self.tan_out_y = buffer.read_float()


class Curve:
    def __init__(self, curve_id):
        self.id = curve_id
        self.type = 0
        self.start_interp_type = None
        self.end_interp_type = None
        self.bool = False
        self.points = []



    def decode(self, buffer):
        count = buffer.read_unsigned_short()

        # this variable is never used in the actual game engine
        self.type = buffer.read_unsigned_byte()

        # this is always TYPE_0 (none)
        self.start_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())

        # this is always TYPE_0 (none)
        self.end_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())

        # this is always false, has to do with interpolation
        self.bool = buffer.read_unsigned_byte() != 0

        self.points = [KeyFramePoint() for _ in range(count)]
        last_point = None
        offset = 0
        for i in range(count):
            keyframe_point = KeyFramePoint()
            keyframe_point.decode(buffer)
            if i is 0:
                offset = keyframe_point.y
            else:
                keyframe_point.offset = offset

            self.points[i] = keyframe_point
            if last_point:
                last_point.next = keyframe_point
            last_point = keyframe_point


class CurveType(Enum):
    NONE = 0
    ROTATE_X = 1
    ROTATE_Y = 2
    ROTATE_Z = 3
    TRANSLATE_X = 4
    TRANSLATE_Y = 5  # this is actually z in blender
    TRANSLATE_Z = 6
    SCALE_X = 7
    SCALE_Y = 8
    SCALE_Z = 9
    TYPE_10 = 10
    TYPE_11 = 11
    TYPE_12 = 12
    TYPE_13 = 13
    TYPE_14 = 14
    TYPE_15 = 15
    TRANSPARENCY = 16

    # todo restructure thi a bit better
    def get_transformation_type(self):
        transformation_types = [
            "NONE",
            "rotation_euler", "rotation_euler", "rotation_euler",
            "location", "location", "location",
            "scale", "scale", "scale",
            "NONE", "NONE", "NONE",
            "NONE", "NONE", "NONE",
            "alpha"
        ]
        return transformation_types[self.value]

    # conversion of the axis index for adding fcurves
    def get_axis_index(self):
        axis_indices = [
            -1,
            # rs x = blender y
            1, 2, 0,  # rot
            1, 2, 0,  # loc

            1, 2, 0,  # scale
            0, 1, 2,  # hsl
            0, 1, 2,  # rgb
            0
        ]
        return axis_indices[self.value]

    def is_scale(self):
        return 7 <= self.value <= 9

    def is_transformation(self):
        return 4 <= self.value <= 6

    def is_rotation(self):
        return 1 <= self.value <= 3


def get_curve_type_for_id(curve_type_id):
    if curve_type_id < 0 or curve_type_id > CurveType.TRANSPARENCY.value:
        return CurveType.NONE
    return CurveType(curve_type_id)


CURVE_INDICES = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2, 3, 4, 5, 0]


def get_curve_index(curve_type):
    return CURVE_INDICES[curve_type.value]


# this is always BONE, or ALPHA
class SkeletalTransformType(Enum):
    TYPE_0 = 0
    BONE = 1
    TYPE_2 = 2
    TYPE_3 = 3
    ALPHA = 4
    TYPE_5 = 5


def get_transform_type_for_id(transform_type):
    if transform_type < 0 or transform_type > SkeletalTransformType.TYPE_5.value:
        return SkeletalTransformType.TYPE_0
    return SkeletalTransformType(transform_type)


CURVE_COUNTS = [0, 9, 3, 6, 1, 3]


def get_curve_count(transform_type):
    return CURVE_COUNTS[transform_type.value]


class CurveInterpType(Enum):
    TYPE_0 = 0
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4


def get_interp_type_for_id(interp_id):
    if interp_id < 0 or interp_id > CurveInterpType.TYPE_4.value:
        return CurveInterpType.TYPE_0
    return CurveInterpType(interp_id)
