from runeblend.skeletal_bone import SkeletalBone


class SkeletalBase:

    def __init__(self, buffer, count):
        self.bones = [SkeletalBone() for _ in range(count)]

        # this is always 0 in the actual game engine
        self.pose_count = buffer.read_unsigned_byte()

        for index in range(len(self.bones)):
            bone = SkeletalBone()
            bone.id = index
            bone.decode(self.pose_count, False, buffer)
            bone.extract_transformations()
            self.bones[index] = bone
        self.link_bones()


    def link_bones(self):
        for bone in self.bones:
            if bone.parent_id >= 0:
                bone.parent = self.bones[bone.parent_id]

    def get_bone_count(self):
        return len(self.bones)

    def get_bone(self, bone_index):
        return self.bones[bone_index]

    def __str__(self):
        return f"skeletal_base{{bones={self.bones}, pose_count={self.pose_count}}}"