import math

import mathutils
import numpy as np
class Vector3f:

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


    def to_blender_vector(self):
        rotated_vector = mathutils.Vector((-self.z, self.y, self.x))
        return rotated_vector * 0.0078125

    def length(self):
        return math.sqrt(self.z * self.z + self.x * self.x + self.y * self.y)

    def add(self, other):
        return Vector3f(self.x + other.x, self.y + other.y, self.z + other.z)

    def sub(self, other):
        return Vector3f(self.x - other.x, self.y - other.y, self.z - other.z)

    def __str__(self):
        return f"{np.rad2deg(self.x)}, {np.rad2deg(self.y)}, {np.rad2deg(self.z)} ({self.x}, {self.y}, {self.z})"