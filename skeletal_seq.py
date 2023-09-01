from curve_type import get_curve_type_for_id
from curve_type import get_curve_type_for_id, get_curve_index
from curve_interp_type import get_interp_type_for_id
from skeletal_transform_type import SkeletalTransformType, get_transform_type_for_id, get_curve_count
from curve import Curve
from byte_buffer import ByteBuffer


class SkeletalSeq:
    def __init__(self, id, version, base, skeletal_base, buffer):
        self.id = id
        self.version = version
        self.base = base
        self.skeletal_base = skeletal_base
        buffer.read_unsigned_short()
        buffer.read_unsigned_short()
        self.pose_id = buffer.read_unsigned_byte()
        self.curve_count = buffer.read_unsigned_short()
        self.bone_curves = [None] * len(skeletal_base.bones)
        self.curves = [None] * base.count
        self.has_alpha_transform = False

        for i in range(self.curve_count):
            transform_type = get_transform_type_for_id(buffer.read_unsigned_byte())
            bone_index = buffer.read_smart_2()
            curve_type = get_curve_type_for_id(buffer.read_unsigned_byte())

            curve = Curve(i)
            curve.decode(buffer, version)

            if transform_type == SkeletalTransformType.BONE:
                curves = self.bone_curves
            else:
                curves = self.curves

            if curves[bone_index] is None:
                curves[bone_index] = [None] * get_curve_count(transform_type)

            curve.load()
            curves[bone_index][get_curve_index(curve_type)] = curve

            if transform_type == SkeletalTransformType.ALPHA:
                self.has_alpha_transform = True

    def update_anim_matrix(self, frame, bone, bone_index, pose_id):
        matrix = MatrixPool.get()

        self.apply_rotation(matrix, bone_index, bone, frame)
        self.apply_scaling(matrix, bone_index, bone, frame)
        self.apply_translation(matrix, bone_index, bone, frame)
        bone.set_anim_matrix(matrix)

        MatrixPool.release(matrix)

    def apply_rotation(self, matrix, bone_index, bone, frame):
        rotation = bone.get_rotation(self.pose_id)
        rotate_x, rotate_y, rotate_z = rotation

        if self.bone_curves[bone_index]:
            curve_x = self.bone_curves[bone_index][0]
            curve_y = self.bone_curves[bone_index][1]
            curve_z = self.bone_curves[bone_index][2]
            if curve_x:
                rotate_x = curve_x.get_value(frame)
            if curve_y:
                rotate_y = curve_y.get_value(frame)
            if curve_z:
                rotate_z = curve_z.get_value(frame)

        quat_x = QuatPool.get()
        vec3.set(rotate_axis, 1, 0, 0)
        quat.set_axis_angle(quat_x, rotate_axis, rotate_x)
        quat_y = QuatPool.get()
        vec3.set(rotate_axis, 0, 1, 0)
        quat.set_axis_angle(quat_y, rotate_axis, rotate_y)
        quat_z = QuatPool.get()
        vec3.set(rotate_axis, 0, 0, 1)
        quat.set_axis_angle(quat_z, rotate_axis, rotate_z)
        quaternion = QuatPool.get()
        quat.mul(quaternion, quat_z, quaternion)
        quat.mul(quaternion, quat_x, quaternion)
        quat.mul(quaternion, quat_y, quaternion)

        rotate_matrix = MatrixPool.get()

        mat4.from_quat(rotate_matrix, quaternion)
        mat4.mul(matrix, rotate_matrix, matrix)

        QuatPool.release(quat_x)
        QuatPool.release(quat_y)
        QuatPool.release(quat_z)
        QuatPool.release(quaternion)
        MatrixPool.release(rotate_matrix)

    def apply_scaling(self, matrix, bone_index, bone, frame):
        scaling = bone.get_scaling(self.pose_id)
        scale_x, scale_y, scale_z = scaling

        if self.bone_curves[bone_index]:
            curve_x = self.bone_curves[bone_index][6]
            curve_y = self.bone_curves[bone_index][7]
            curve_z = self.bone_curves[bone_index][8]
            if curve_x:
                scale_x = curve_x.get_value(frame)
            if curve_y:
                scale_y = curve_y.get_value(frame)
            if curve_z:
                scale_z = curve_z.get_value(frame)

        scale_matrix = MatrixPool.get()

        vec3.set(scale_vector, scale_x, scale_y, scale_z)
        mat4.from_scaling(scale_matrix, scale_vector)
        mat4.mul(matrix, scale_matrix, matrix)

        MatrixPool.release(scale_matrix)

    def apply_translation(self, matrix, bone_index, bone, frame):
        translation = bone.get_translation(self.pose_id)
        trans_x, trans_y, trans_z = translation

        if self.bone_curves[bone_index]:
            curve_x = self.bone_curves[bone_index][3]
            curve_y = self.bone_curves[bone_index][4]
            curve_z = self.bone_curves[bone_index][5]
            if curve_x:
                trans_x = curve_x.get_value(frame)
            if curve_y:
                trans_y = curve_y.get_value(frame)
            if curve_z:
                trans_z = curve_z.get_value(frame)

        matrix[12] = trans_x
        matrix[13] = trans_y
        matrix[14] = trans_z

    @staticmethod
    def load(base_loader, id, data):
        buffer = ByteBuffer(data)

        version = buffer.read_unsigned_byte()
        base_id = buffer.read_unsigned_short()
        base = base_loader.load(base_id)
        if not base:
            raise ValueError("Invalid skeletal base id: " + str(base_id))
        skeletal_base = base.skeletal_base
        if not skeletal_base:
            raise ValueError("Missing skeletal base: " + str(base_id))

        return SkeletalSeq(id, version, base, skeletal_base, buffer)
