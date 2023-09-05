from runeblend.skeletal_base import SkeletalBase
from runeblend.byte_buffer import ByteBuffer


##############################################
# None of this data is really relevant for the skeletal animations
# most of it is utilized for runescape legacy animation system which
# we are not supporting in blender yet.
##############################################
class Base:

    def __init__(self):
        self.id = 0
        self.types = []
        # the vertex groups this skeleton influences in the legacy system
        # not used for skeletal anims
        self.group_labels = []
        # amount of face groups for alpha animations
        self.length = 0
        self.skeletal_base = None

    @staticmethod
    def decode(self, data):
        buffer = ByteBuffer(data)

        length = buffer.read_unsigned_byte()
        self.length = length
        types = [0] * length
        group_labels = [[] for _ in range(length)]

        for i in range(length):
            types[i] = buffer.read_unsigned_byte()

        for i in range(length):
            group_labels[i] = [0] * buffer.read_unsigned_byte()

        for i in range(length):
            for j in range(len(group_labels[i])):
                group_labels[i][j] = buffer.read_unsigned_byte()

        if buffer.get_pos() < len(buffer.getArray()):
            bone_count = buffer.read_unsigned_short()
            if bone_count > 0:
                self.skeletal_base = SkeletalBase(buffer, bone_count)

        self.types = types
        self.group_labels = group_labels
