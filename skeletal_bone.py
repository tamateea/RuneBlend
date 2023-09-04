from runeblend.mat_4 import Matrix4f
from runeblend.vec_3 import Vector3f
from mathutils import Euler


class SkeletalBone:
    def __init__(self):
        self.parent_id = 0
        self.id = 0
        self.parent = None
        self.unused = None
        self.local_matrices = []
        self.model_matrices = []
        self.inverted_model_matrices = []
        self.anim_matrix = Matrix4f()
        self.update_anim_model_matrix = False
        self.anim_matrix = Matrix4f()
        self.update_final_matrix = False
        self.final_matrix = Matrix4f()
        self.rotations = []
        self.translations = []
        self.scalings = []
        self.local_translation = Vector3f()

    def decode(self, pose_id, compact_matrix, buffer):
        self.parent_id = buffer.read_short()
        self.local_matrices = [None for _ in range(pose_id)]
        self.model_matrices = [None for _ in range(len(self.local_matrices))]
        self.inverted_model_matrices = [None for _ in range(len(self.local_matrices))]
        self.unused = [[0.0] * 3 for _ in range(len(self.local_matrices))]
        for index in range(len(self.local_matrices)):
            local_matrix = Matrix4f()
            self.read_mat_4(buffer, local_matrix, compact_matrix)
            self.local_matrices[index] = local_matrix
            self.unused[index][0] = buffer.read_float()
            self.unused[index][1] = buffer.read_float()
            self.unused[index][2] = buffer.read_float()


    def read_mat_4(self, buffer, matrix, compact_matrix):
        if compact_matrix:
            pass
        else:
            for index in range(16):
                matrix.m[index] = buffer.read_float()

    def extract_transformations(self):
        pose_count = len(self.local_matrices)
        self.rotations = []
        self.translations = []
        self.scalings = []
        inverted_local_matrix = Matrix4f.take()

        for pose in range(pose_count):
            local_matrix = self.get_local_matrix(pose)
            inverted_local_matrix.copy(local_matrix)
            inverted_local_matrix.invert()
            self.rotations.append(inverted_local_matrix.get_euler_angles_yxz_inverse())
            self.translations.append(local_matrix.get_translation())
            self.scalings.append(local_matrix.get_scale())
        inverted_local_matrix.release()

    def get_local_matrix(self, bone_index):
        return self.local_matrices[bone_index]

    def get_model_matrix(self, pose_id):
        if self.model_matrices[pose_id] is None:
            self.model_matrices[pose_id] = Matrix4f.from_arr(self.local_matrices[pose_id].m)
            if self.parent:
                self.model_matrices[pose_id].multiply(self.parent.get_model_matrix(pose_id))
            else:
                self.model_matrices[pose_id].multiply(Matrix4f.IDENTITY)
        return self.model_matrices[pose_id]

    def get_inverted_model_matrix(self, pose_id):
        if self.inverted_model_matrices[pose_id] is None:
            self.inverted_model_matrices[pose_id] = self.get_model_matrix(pose_id)
            self.inverted_model_matrices[pose_id].invert()
        return self.inverted_model_matrices[pose_id]

    def set_anim_matrix(self, anim_matrix):
        self.anim_matrix.copy(anim_matrix)
        self.update_anim_model_matrix = True
        self.update_final_matrix = True

    def get_anim_matrix(self):
        return self.anim_matrix

    def get_anim_model_matrix(self):
        if self.update_anim_model_matrix:
            self.update_anim_model_matrix = False
            if self.parent:
                self.anim_matrix.multiply(self.parent.get_anim_model_matrix())
            else:
                self.anim_matrix.copy(self.get_anim_matrix())
        return self.anim_matrix

    def get_final_matrix(self, pose_id):
        if self.update_final_matrix:
            self.update_final_matrix = False
            self.final_matrix.copy(self.get_inverted_model_matrix(pose_id))
            self.final_matrix.multiply(self.get_anim_model_matrix())
        return self.final_matrix

    def get_rotation(self, pose_id):
        return self.rotations[pose_id]


    def get_translation(self, pose_id):
        return self.translations[pose_id]

    def get_scaling(self, pose_id):
        return self.scalings[pose_id]

