import math


class Quaternionf:
    pool_limit = 100
    pool = [0] * pool_limit
    pool_cursor = 0

    @staticmethod
    def identity():
        return Quaternionf(0.0, 0.0, 0.0, 1.0)

    def __init__(self, x=0.0, y=0.0, w=0.0, z=1.0):
        self.x = x
        self.y = y
        self.w = w
        self.z = z

    def release(self):
        if Quaternionf.pool_cursor < Quaternionf.pool_limit - 1:
            # Reset the quaternion's values (if needed) before releasing
            # For example: self.x = 0.0, self.y = 0.0, self.z = 0.0, self.w = 1.0
            new_quaternion = Quaternionf(self.x, self.y, self.w, self.z)
            Quaternionf.pool[Quaternionf.pool_cursor] = new_quaternion
            Quaternionf.pool_cursor += 1

    @staticmethod
    def take():
        if Quaternionf.pool_cursor == 0:
            return Quaternionf.identity()
        else:
            Quaternionf.pool_cursor -= 1
            quaternion = Quaternionf.pool[Quaternionf.pool_cursor]
            quaternion.x = 0.0
            quaternion.y = 0.0
            quaternion.z = 0.0
            quaternion.w = 1.0
            return quaternion

    def set(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def multiply(self, other):
        self.set(
            other.x * self.w + other.w * self.x + other.y * self.z - other.z * self.y,
            other.z * self.x + self.w * other.y + (self.y * other.w - self.z * other.x),
            other.x * self.y + other.w * self.z - self.x * other.y + other.z * self.w,
            other.w * self.w - other.x * self.x - self.y * other.y - other.z * self.z
        )

    def __eq__(self, other):
        if not isinstance(other, Quaternionf):
            return False
        return (
                self.x == other.x and
                self.y == other.y and
                self.z == other.z and
                self.w == other.w
        )



    def normalize(self):
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if magnitude > 0.0:
            inv_magnitude = 1.0 / magnitude
            self.x *= inv_magnitude
            self.y *= inv_magnitude
            self.z *= inv_magnitude
            self.w *= inv_magnitude



    def __str__(self):
        return f"{self.x},{self.y},{self.z},{self.w}"

    def __hash__(self):
        hash_code = 1.0
        hash_code = hash_code * 31.0 + self.x
        hash_code = self.y + hash_code * 31.0
        hash_code = 31.0 * hash_code + self.z
        hash_code = 31.0 * hash_code + self.w
        return int(hash_code)
