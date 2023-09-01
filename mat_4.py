import math
import numpy as np
from runeblend.vec_3 import Vector3f
import mathutils


class Matrix4f:
    pool = [None] * 100
    pool_limit = 100
    pool_cursor = 0
    IDENTITY = None

    @staticmethod
    def initialize():
        Matrix4f.IDENTITY = Matrix4f()
        for i in range(Matrix4f.pool_limit):
            Matrix4f.pool[i] = Matrix4f()

    def __init__(self):
        self.m = np.zeros(16)
        self.identity()

    def release(self):
        if Matrix4f.pool_cursor < Matrix4f.pool_limit - 1:
            Matrix4f.pool[Matrix4f.pool_cursor] = self
            Matrix4f.pool_cursor += 1

    @staticmethod
    def take():
        if Matrix4f.pool_cursor == 0:
            return Matrix4f()
        else:
            Matrix4f.pool_cursor -= 1
            return Matrix4f.pool[Matrix4f.pool_cursor]

    def get_euler_angles_yxz(self):
        euler_angles = np.zeros(3)
        if 0.999 > self.m[2] > -0.999:
            euler_angles[1] = -math.asin(self.m[2])
            c = math.cos(euler_angles[1])
            euler_angles[0] = math.atan2(self.m[6] / c, self.m[10] / c)
            euler_angles[2] = math.atan2(self.m[1] / c, self.m[0] / c)
        else:
            euler_angles[0] = 0.0
            euler_angles[1] = math.atan2(self.m[2], 0.0)
            euler_angles[2] = math.atan2(-self.m[9], self.m[5])
        return euler_angles


    # euler angle yxz
    def get_euler_angles_yxz_inverse(self):
        eulerAngles = [0.0, 0.0, 0.0]
        eulerAngles[0] = -math.asin(self.m[6])
        var2 = math.cos(eulerAngles[0])

        if abs(var2) > 0.005:
            var4 = self.m[2]
            var6 = self.m[10]
            var8 = self.m[4]
            var10 = self.m[5]
            eulerAngles[1] = math.atan2(var4, var6)
            eulerAngles[2] = math.atan2(var8, var10)
        else:
            var4 = self.m[1]
            var6 = self.m[0]
            if self.m[6] < 0.0:
                eulerAngles[1] = math.atan2(var4, var6)
            else:
                eulerAngles[1] = -math.atan2(var4, var6)
            eulerAngles[2] = 0.0
        return eulerAngles


    def identity(self):
        self.m = np.array([1.0, 0.0, 0.0, 0.0,
                           0.0, 1.0, 0.0, 0.0,
                           0.0, 0.0, 1.0, 0.0,
                           0.0, 0.0, 0.0, 1.0])

    def zero(self):
        self.m = np.zeros(16)

    def copy(self, matrix):
        self.m = matrix.m.copy()


    def add(self, other):
        self.m += other.m

    def maya_to_blender_matrix(self):
        if len(self.m) != 16:
            raise ValueError("Maya matrix must have 16 elements")

        blender_matrix = mathutils.Matrix()
        copy = self.from_arr(self.m)
        for row in range(4):
            for col in range(4):
                blender_matrix[row][col] = copy.m[col * 4 + row]


        return blender_matrix


    def get_translation(self):
        return Vector3f(self.m[12], self.m[13], self.m[14])

    def invert(self):
        det = self.det()
        inv_det = 1.0 / det
        inverse_result = Matrix4f()

        inverse_result.m[0] = self.m[5] * self.m[10] * self.m[15] - self.m[5] * self.m[11] * \
                    self.m[14] - self.m[9] * self.m[6] * self.m[15] + self.m[9] * \
                    self.m[7] * self.m[14] + self.m[13] * self.m[6] * self.m[11] - \
                    self.m[13] * self.m[7] * self.m[10]
        inverse_result.m[4] = -self.m[4] * self.m[10] * self.m[15] + self.m[4] * self.m[11] * \
                    self.m[14] + self.m[8] * self.m[6] * self.m[15] - self.m[8] * \
                    self.m[7] * self.m[14] - self.m[12] * self.m[6] * self.m[11] + \
                    self.m[12] * self.m[7] * self.m[10]
        inverse_result.m[8] = self.m[4] * self.m[9] * self.m[15] - self.m[4] * self.m[11] * \
                    self.m[13] - self.m[8] * self.m[5] * self.m[15] + self.m[8] * \
                    self.m[7] * self.m[13] + self.m[12] * self.m[5] * self.m[11] - \
                    self.m[12] * self.m[7] * self.m[9]
        inverse_result.m[12] = -self.m[4] * self.m[9] * self.m[14] + self.m[4] * self.m[10] * \
                     self.m[13] + self.m[8] * self.m[5] * self.m[14] - self.m[8] * \
                     self.m[6] * self.m[13] - self.m[12] * self.m[5] * self.m[10] + \
                     self.m[12] * self.m[6] * self.m[9]

        inverse_result.m[1] = -self.m[1] * self.m[10] * self.m[15] + self.m[1] * self.m[11] * \
                    self.m[14] + self.m[9] * self.m[2] * self.m[15] - self.m[9] * \
                    self.m[3] * self.m[14] - self.m[13] * self.m[2] * self.m[11] + \
                    self.m[13] * self.m[3] * self.m[10]
        inverse_result.m[5] = self.m[0] * self.m[10] * self.m[15] - self.m[0] * self.m[11] * \
                    self.m[14] - self.m[8] * self.m[2] * self.m[15] + self.m[8] * \
                    self.m[3] * self.m[14] + self.m[12] * self.m[2] * self.m[11] - \
                    self.m[12] * self.m[3] * self.m[10]
        inverse_result.m[9] = -self.m[0] * self.m[9] * self.m[15] + self.m[0] * self.m[11] * \
                    self.m[13] + self.m[8] * self.m[1] * self.m[15] - self.m[8] * \
                    self.m[3] * self.m[13] - self.m[12] * self.m[1] * self.m[11] + \
                    self.m[12] * self.m[3] * self.m[9]
        inverse_result.m[13] = self.m[0] * self.m[9] * self.m[14] - self.m[0] * self.m[10] * \
                     self.m[13] - self.m[8] * self.m[1] * self.m[14] + self.m[8] * \
                     self.m[2] * self.m[13] + self.m[12] * self.m[1] * self.m[10] - \
                     self.m[12] * self.m[2] * self.m[9]

        inverse_result.m[2] = self.m[1] * self.m[6] * self.m[15] - self.m[1] * self.m[7] * \
                    self.m[14] - self.m[5] * self.m[2] * self.m[15] + self.m[5] * \
                    self.m[3] * self.m[14] + self.m[13] * self.m[2] * self.m[7] - \
                    self.m[13] * self.m[3] * self.m[6]
        inverse_result.m[6] = -self.m[0] * self.m[6] * self.m[15] + self.m[0] * self.m[7] * \
                    self.m[14] + self.m[4] * self.m[2] * self.m[15] - self.m[4] * \
                    self.m[3] * self.m[14] - self.m[12] * self.m[2] * self.m[7] + \
                    self.m[12] * self.m[3] * self.m[6]
        inverse_result.m[10] = self.m[0] * self.m[5] * self.m[15] - self.m[0] * self.m[7] * \
                     self.m[13] - self.m[4] * self.m[1] * self.m[15] + self.m[4] * \
                     self.m[3] * self.m[13] + self.m[12] * self.m[1] * self.m[7] - \
                     self.m[12] * self.m[3] * self.m[5]
        inverse_result.m[14] = -self.m[0] * self.m[5] * self.m[14] + self.m[0] * self.m[6] * \
                     self.m[13] + self.m[4] * self.m[1] * self.m[14] - self.m[4] * \
                     self.m[2] * self.m[13] - self.m[12] * self.m[1] * self.m[6] + \
                     self.m[12] * self.m[2] * self.m[5]

        inverse_result.m[3] = -self.m[1] * self.m[6] * self.m[11] + self.m[1] * self.m[7] * \
                    self.m[10] + self.m[5] * self.m[2] * self.m[11] - self.m[5] * \
                    self.m[3] * self.m[10] - self.m[9] * self.m[2] * self.m[7] + \
                    self.m[9] * self.m[3] * self.m[6]
        inverse_result.m[7] = self.m[0] * self.m[6] * self.m[11] - self.m[0] * self.m[7] * \
                    self.m[10] - self.m[4] * self.m[2] * self.m[11] + self.m[4] * \
                    self.m[3] * self.m[10] + self.m[8] * self.m[2] * self.m[7] - \
                    self.m[8] * self.m[3] * self.m[6]
        inverse_result.m[11] = -self.m[0] * self.m[5] * self.m[11] + self.m[0] * self.m[7] * \
                     self.m[9] + self.m[4] * self.m[1] * self.m[11] - self.m[4] * \
                     self.m[3] * self.m[9] - self.m[8] * self.m[1] * self.m[7] + \
                     self.m[8] * self.m[3] * self.m[5]
        inverse_result.m[15] = self.m[0] * self.m[5] * self.m[10] - self.m[0] * self.m[6] * \
                     self.m[9] - self.m[4] * self.m[1] * self.m[10] + self.m[4] * \
                     self.m[2] * self.m[9] + self.m[8] * self.m[1] * self.m[6] - \
                     self.m[8] * self.m[2] * self.m[5]

        self.m = [value * inv_det for value in inverse_result.m]

        return True

    def det(self):
        return (self.m[0] * self.m[5] - self.m[1] * self.m[4]) * (
                self.m[10] * self.m[15] - self.m[11] * self.m[14]) - (
                self.m[0] * self.m[6] - self.m[2] * self.m[4]) * (
                self.m[9] * self.m[15] - self.m[11] * self.m[13]) + (
                self.m[0] * self.m[7] - self.m[3] * self.m[4]) * (
                self.m[9] * self.m[14] - self.m[10] * self.m[13]) + (
                self.m[1] * self.m[6] - self.m[2] * self.m[5]) * (
                self.m[8] * self.m[15] - self.m[11] * self.m[12]) - (
                self.m[1] * self.m[7] - self.m[3] * self.m[5]) * (
                self.m[8] * self.m[14] - self.m[10] * self.m[12]) + (
                self.m[2] * self.m[7] - self.m[3] * self.m[6]) * (
                self.m[8] * self.m[13] - self.m[9] * self.m[12])


    def get_translation(self):
        return Vector3f(self.m[12], self.m[13], self.m[14])

    def set(self, m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33):
        self.m[0] = m00
        self.m[1] = m01
        self.m[2] = m02
        self.m[3] = m03
        self.m[4] = m10
        self.m[5] = m11
        self.m[6] = m12
        self.m[7] = m13
        self.m[8] = m20
        self.m[9] = m21
        self.m[10] = m22
        self.m[11] = m23
        self.m[12] = m30
        self.m[13] = m31
        self.m[14] = m32
        self.m[15] = m33

    def multiply(self, other):
        m00 = self.m[2] * other.m[8] + self.m[1] * other.m[4] + self.m[0] * other.m[
            0] + other.m[12] * self.m[3]
        m01 = self.m[3] * other.m[13] + other.m[9] * self.m[2] + self.m[0] * other.m[
            1] + other.m[5] * self.m[1]
        m02 = self.m[2] * other.m[10] + self.m[1] * other.m[6] + other.m[2] * self.m[
            0] + other.m[14] * self.m[3]
        m03 = self.m[3] * other.m[15] + other.m[11] * self.m[2] + self.m[0] * other.m[
            3] + self.m[1] * other.m[7]
        m10 = self.m[7] * other.m[12] + other.m[0] * self.m[4] + other.m[4] * self.m[
            5] + other.m[8] * self.m[6]
        m11 = self.m[7] * other.m[13] + other.m[1] * self.m[4] + self.m[5] * other.m[
            5] + other.m[9] * self.m[6]
        m12 = self.m[7] * other.m[14] + other.m[6] * self.m[5] + self.m[4] * other.m[
            2] + self.m[6] * other.m[10]
        m13 = other.m[15] * self.m[7] + self.m[6] * other.m[11] + self.m[5] * other.m[
            7] + other.m[3] * self.m[4]
        m20 = self.m[9] * other.m[4] + self.m[8] * other.m[0] + self.m[10] * other.m[
            8] + self.m[11] * other.m[12]
        m21 = other.m[9] * self.m[10] + self.m[8] * other.m[1] + other.m[5] * self.m[
            9] + self.m[11] * other.m[13]
        m22 = other.m[2] * self.m[8] + self.m[9] * other.m[6] + other.m[10] * self.m[
            10] + self.m[11] * other.m[14]
        m23 = other.m[15] * self.m[11] + other.m[11] * self.m[10] + other.m[7] * \
              self.m[9] + self.m[8] * other.m[3]
        m30 = self.m[15] * other.m[12] + other.m[4] * self.m[13] + other.m[0] * \
              self.m[12] + self.m[14] * other.m[8]
        m31 = self.m[12] * other.m[1] + other.m[5] * self.m[13] + self.m[14] * \
              other.m[9] + other.m[13] * self.m[15]
        m32 = other.m[10] * self.m[14] + self.m[13] * other.m[6] + other.m[2] * \
              self.m[12] + other.m[14] * self.m[15]
        m33 = other.m[15] * self.m[15] + other.m[3] * self.m[12] + self.m[13] * \
              other.m[7] + other.m[11] * self.m[14]
        self.set(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33)

    def get_scale(self):
        x = Vector3f(self.m[0], self.m[1], self.m[2])
        y = Vector3f(self.m[4], self.m[5], self.m[6])
        z = Vector3f(self.m[8], self.m[9], self.m[10])
        return Vector3f(x.length(), y.length(), z.length())

    def decompose(self):
        translation = self.get_translation().multiply(0.0078125)
        euler_inverse = self.get_euler_angles_yxz_inverse()
        eulerAnglesYXZ = Vector3f(euler_inverse[0], euler_inverse[1], euler_inverse[2])
        scale = self.get_scale()
        return translation, eulerAnglesYXZ, scale

    def to_array(self):
        return self.m.tolist()

    def getMatrix(self):
        return mathutils.Matrix((self.m))

    @staticmethod
    def from_arr(arr):
        matrix = Matrix4f()
        matrix.m = np.array(arr)
        return matrix

    def __str__(self):
        sb = []
        self.get_euler_angles_yxz_inverse()
        self.get_euler_angles_yxz()
        for i in range(4):
            row_values = []
            for j in range(4):
                if j > 0:
                    row_values.append("\t")
                value = self.m[j + i * 4]
                if math.sqrt(value * value) < 9.999999747378752e-5:
                    value = 0.0
                row_values.append(str(value))
            sb.append("".join(row_values))
        return "\n".join(sb)


Matrix4f.initialize()
