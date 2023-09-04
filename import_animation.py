import math
import bpy
import mathutils
from runeblend.byte_buffer import ByteBuffer
import bpy
from enum import Enum


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
    version = buffer.read_unsigned_byte()  # not used
    base_id = buffer.read_unsigned_short()  # not used
    bone_count = len(armature.bones)  # this will be replaced later
    start_frame = buffer.read_unsigned_short()  # not used
    end_frame = buffer.read_unsigned_short()  # not usd
    pose_id = buffer.read_unsigned_byte()  # not used
    curve_count = buffer.read_unsigned_short()
    bone_curves = [None] * bone_count
    length = bpy.context.object['base_length']
    face_curves = [None] * length  # pre-defined property for alpha transforms
    has_alpha_transform = False  # not used yet
    rig = bpy.data.objects["imported_rig"]
    action = bpy.data.actions.new("imported_animation")

    bpy.context.scene.frame_set(1)
    for i in range(curve_count):
        transform_type = get_transform_type_for_id(buffer.read_unsigned_byte())
        bone_index = buffer.readSignedSmart
        curve_type = get_curve_type_for_id(buffer.read_unsigned_byte())
        curve = Curve(i)
        curve.decode(buffer)

        if transform_type == SkeletalTransformType.BONE:
            curves = bone_curves
        else:
            curves = face_curves  # alpha curves

        if curves[bone_index] is None:
            curves[bone_index] = [0] * get_curve_count(transform_type)

        index = get_curve_index(curve_type)
        curves[bone_index][index] = curve

        bone_name = f"Bone_{bone_index}"
        transformation_type = curve_type.get_transformation_type()
        axis_idx = curve_type.get_axis_index()
        data_path = f'pose.bones["{bone_name}"].{transformation_type}'
        if transformation_type != SkeletalTransformType.ALPHA:
            f_curve = action.fcurves.new(data_path, index=axis_idx, action_group=bone_name)
            for p in curve.points:
                frame = p.x
                value = p.y

                if curve_type.is_transformation():
                    value *= 0.0078125

                if curve_type.is_scale():
                    print(f"scale value:{value}")


                if curve_type is CurveType.TRANSLATE_Z:
                    value = -value


                if curve_type is CurveType.ROTATE_Z:
                    value = -value

                print(f"{data_path} ")
                keyframe = f_curve.keyframe_points.insert(frame, value, options={'FAST'})
                keyframe.interpolation = 'LINEAR'

            if transform_type == SkeletalTransformType.ALPHA:
                has_alpha_transform = True

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    rig.animation_data_create()
    rig.animation_data.action = action


class KeyFramePoint:
    def __init__(self):
        self.x = 0  # this is a frame number
        self.y = 0  # this is the frames value

        # these could be values to do with handles
        self.field2 = 0  # start time i think
        self.field3 = 0  # also to do with start time
        self.field4 = 0  # end time
        self.field5 = 0  # end time i think
        self.next = None

    def decode(self, buffer):
        self.x = buffer.read_short()
        self.y = buffer.read_float()
        self.field2 = buffer.read_float()
        self.field3 = buffer.read_float()
        self.field4 = buffer.read_float()
        self.field5 = buffer.read_float()


class Curve:
    def __init__(self, curve_id):
        self.id = curve_id
        self.type = 0
        self.start_interp_type = None
        self.end_interp_type = None
        self.bool = False
        self.points = []
        self.start_tick = 0
        self.end_tick = 0
        self.values = []
        self.min_value = 0  # interpolated
        self.max_value = 0  # interpolated
        self.no_interp = False
        self.point_index = 0
        self.point_index_updated = True
        self.interp_bool = False
        self.interp_v0 = 0
        self.interp_v1 = 0
        self.interp_v2 = 0
        self.interp_v3 = 0
        self.interp_v4 = 0
        self.interp_v5 = 0
        self.interp_v6 = 0
        self.interp_v7 = 0
        self.interp_v8 = 0
        self.interp_v9 = 0

    def decode(self, buffer):
        count = buffer.read_unsigned_short()
        self.type = buffer.read_unsigned_byte()  # ignored
        self.start_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())  # ignored
        self.end_interp_type = get_interp_type_for_id(buffer.read_unsigned_byte())  # ignored
        self.bool = buffer.read_unsigned_byte() != 0  # not used

        self.points = [KeyFramePoint() for _ in range(count)]
        last_point = None
        for i in range(count):
            keyframe_point = KeyFramePoint()
            keyframe_point.decode(buffer)
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
