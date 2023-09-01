import math

import mathutils
import numpy as np
class Vector3f:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return math.sqrt(self.z * self.z + self.x * self.x + self.y * self.y)


    def multiply(self, value):
        return Vector3f(self.x * value, self.y * value, self.z * value)

    def __str__(self):
        return "{:.2f}, {:.2f}, {:.2f}".format(self.x, self.y, self.z)

    def print_angle(self):
        return "{:.2f}, {:.2f}, {:.2f}".format(math.degrees(self.x), math.degrees(self.y), math.degrees(self.z))