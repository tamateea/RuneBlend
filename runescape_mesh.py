from runeblend.byte_buffer import ByteBuffer


def to_signed_byte(value):
    value %= 256
    if value > 127:
        value -= 256
    return value


class RunescapeMesh:
    def __init__(self):

        # vars for rs3 models, mostly unused.
        self.texture_scale_x = None
        self.texture_scale_y = None
        self.texture_scale_z = None
        self.texture_rotation = None
        self.texture_direction = None
        self.texture_speed = None
        self.texture_u_trans = None
        self.texture_v_trans = None
        self.uv_map_vertex_offset = None
        self.uv_face_indices_a = None
        self.uv_face_indices_b = None
        self.uv_face_indices_c = None
        self.uv_coord_u = None
        self.uv_coord_v = None
        self.uv_coords_count = 0
        self.highest_vertex = 0
        self.emitters = None
        self.effectors = None
        self.billboards = None

        self.model_version = None
        self.texture_coord_indices = None
        self.texture_ids = None
        self.skeletal_bones = None
        self.skeletal_weights = None
        self.model_type = ""

        self.vertex_count = 0
        self.vertices_x = []
        self.vertices_y = []
        self.vertices_z = []
        self.face_count = 0
        self.face_indices_a = []  # indices
        self.face_indices_b = []
        self.face_indices_c = []
        self.face_draw_types = []
        self.face_priorities = []
        self.face_alphas = []
        self.face_colors = []
        self.model_priority = 0
        self.vertex_groups = []  # vskin
        self.face_groups = []  # tskin
        self.textured_face_count = 0
        self.texture_coords_p = []  # p
        self.texture_coords_m = []  # m
        self.texture_coords_n = []  # n
        self.texture_types = []
        self.grouped_vertices = []
        self.grouped_faces = []
        self.bone_groups = None

    @staticmethod
    def decode(self, data):
        last = to_signed_byte(data[-1])
        second_last = to_signed_byte(data[-2])
        if data[0] == 1:
            return self.decode_rs3(data)
        elif last == -3 and second_last == -1:
            return self.decode_type_three(data)
        elif last == -2 and second_last == -1:
            return self.decode_type_two(data)
        elif last == -1 and second_last == -1:
            return self.decode_new(data)
        else:
            return self.decode_old(data)

    def decode_old(self, data):
        self.model_type = "old"

        buffer_indices = ByteBuffer(data)
        buffer_face_properties = ByteBuffer(data)
        buffer_face_priorities = ByteBuffer(data)
        buffer_face_alphas = ByteBuffer(data)
        buffer_face_groups = ByteBuffer(data)

        buffer_indices.set_pos(len(data) - 18)
        vertex_count = buffer_indices.read_unsigned_short()
        face_count = buffer_indices.read_unsigned_short()
        textured_face_count = buffer_indices.read_unsigned_byte()

        self.vertex_count = vertex_count
        self.face_count = face_count
        self.textured_face_count = textured_face_count

        face_properties_flag = buffer_indices.read_unsigned_byte()
        priority_flag = buffer_indices.read_unsigned_byte()
        alpha_flag = buffer_indices.read_unsigned_byte()
        face_group_flag = buffer_indices.read_unsigned_byte()
        vertex_group_offset = buffer_indices.read_unsigned_byte()

        vertices_x_length = buffer_indices.read_unsigned_short()
        vertices_y_length = buffer_indices.read_unsigned_short()
        vertices_z_length = buffer_indices.read_unsigned_short()
        face_indices_length = buffer_indices.read_unsigned_short()

        pos = 0

        vertex_flags_offset = pos
        pos += vertex_count

        face_indices_flag_offset = pos
        pos += face_count

        face_priority_offset = pos
        if priority_flag == 255:
            pos += face_count

        face_group_offset = pos
        if face_group_flag == 1:
            pos += face_count

        face_properties_offset = pos
        if face_properties_flag == 1:
            pos += face_count

        vertex_groups_offset = pos
        if vertex_group_offset == 1:
            pos += vertex_count

        alpha_offset = pos
        if alpha_flag == 1:
            pos += face_count

        face_indices_offset = pos
        pos += face_indices_length

        face_colors_offset = pos
        pos += face_count * 2

        texture_vertices_offset = pos
        pos += textured_face_count * 6

        vertices_x_offset = pos
        pos += vertices_x_length

        vertices_y_offset = pos
        pos += vertices_y_length

        vertices_z_offset = pos

        self.vertices_x = [0] * vertex_count
        self.vertices_y = [0] * vertex_count
        self.vertices_z = [0] * vertex_count
        self.face_indices_a = [0] * face_count
        self.face_indices_b = [0] * face_count
        self.face_indices_c = [0] * face_count

        if textured_face_count > 0:
            self.texture_types = [0] * textured_face_count
            self.texture_coords_p = [0] * textured_face_count
            self.texture_coords_m = [0] * textured_face_count
            self.texture_coords_n = [0] * textured_face_count

        if vertex_group_offset == 1:
            self.vertex_groups = [0] * vertex_count

        if face_properties_flag == 1:
            self.face_draw_types = [0] * face_count

        if priority_flag == 255:
            self.face_priorities = [0] * face_count
        else:
            self.model_priority = priority_flag

        if alpha_flag == 1:
            self.face_alphas = [0] * face_count

        if face_group_flag == 1:
            self.face_groups = [0] * face_count

        self.face_colors = [0] * face_count
        buffer_indices.set_pos(vertex_flags_offset)
        buffer_face_properties.set_pos(vertices_x_offset)
        buffer_face_priorities.set_pos(vertices_y_offset)
        buffer_face_alphas.set_pos(vertices_z_offset)
        buffer_face_groups.set_pos(vertex_groups_offset)
        x = y = z = 0
        for vertex in range(vertex_count):
            position_flag = buffer_indices.read_unsigned_byte()
            dx = dy = dz = 0
            if position_flag & 1:
                dx = buffer_face_properties.readSignedSmart

            if position_flag & 2:
                dy = buffer_face_priorities.readSignedSmart

            if position_flag & 4:
                dz = buffer_face_alphas.readSignedSmart
            self.vertices_x[vertex] = x + dx
            self.vertices_y[vertex] = y + dy
            self.vertices_z[vertex] = z + dz
            x = self.vertices_x[vertex]
            y = self.vertices_y[vertex]
            z = self.vertices_z[vertex]
            if self.vertex_groups:
                self.vertex_groups[vertex] = buffer_face_groups.read_unsigned_byte()

        buffer_indices.set_pos(face_colors_offset)
        buffer_face_properties.set_pos(face_properties_offset)
        buffer_face_priorities.set_pos(face_priority_offset)
        buffer_face_alphas.set_pos(alpha_offset)
        buffer_face_groups.set_pos(face_group_offset)

        for face in range(face_count):
            color = buffer_indices.read_unsigned_short()
            self.face_colors[face] = color

            if face_properties_flag == 1:
                self.face_draw_types[face] = buffer_face_properties.read_unsigned_byte()
            if priority_flag == 255:
                self.face_priorities[face] = buffer_face_priorities.read_signed_byte()

            if alpha_flag == 1:
                self.face_alphas[face] = buffer_face_alphas.read_unsigned_byte()

            if face_group_flag == 1:
                self.face_groups[face] = buffer_face_groups.read_unsigned_byte()

        buffer_indices.set_pos(face_indices_offset)
        buffer_face_properties.set_pos(face_indices_flag_offset)
        a = b = c = last = 0
        for face in range(face_count):
            opcode = buffer_face_properties.read_unsigned_byte()
            if opcode == 1:
                a = buffer_indices.readSignedSmart + last
                last = a
                b = buffer_indices.readSignedSmart + last
                last = b
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 2:
                b = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 3:
                a = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 4:
                temp = a
                a = b
                b = temp
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

        buffer_indices.set_pos(texture_vertices_offset)
        for face in range(textured_face_count):
            self.texture_types[face] = 0
            self.texture_coords_p[face] = buffer_indices.read_unsigned_short()
            self.texture_coords_m[face] = buffer_indices.read_unsigned_short()
            self.texture_coords_n[face] = buffer_indices.read_unsigned_short()
        self.convert_textures()

    def decode_type_two(self, data):
        self.model_type = "type 2"
        buffer_indices = ByteBuffer(data)
        buffer_face_properties = ByteBuffer(data)
        buffer_face_priorities = ByteBuffer(data)
        buffer_face_alphas = ByteBuffer(data)
        buffer_face_groups = ByteBuffer(data)

        buffer_indices.set_pos(len(data) - 23)
        vertex_count = buffer_indices.read_unsigned_short()
        face_count = buffer_indices.read_unsigned_short()
        textured_face_count = buffer_indices.read_unsigned_byte()

        self.vertex_count = vertex_count
        self.face_count = face_count
        self.textured_face_count = textured_face_count

        face_properties_flag = buffer_indices.read_unsigned_byte()
        priority_flag = buffer_indices.read_unsigned_byte()
        alpha_flag = buffer_indices.read_unsigned_byte()
        face_group_flag = buffer_indices.read_unsigned_byte()
        vertex_group_offset = buffer_indices.read_unsigned_byte()
        skeletal_flag = buffer_indices.read_unsigned_byte()

        vertices_x_length = buffer_indices.read_unsigned_short()
        vertices_y_length = buffer_indices.read_unsigned_short()
        vertices_z_length = buffer_indices.read_unsigned_short()
        face_indices_length = buffer_indices.read_unsigned_short()
        skeletal_length = buffer_indices.read_unsigned_short()

        vertex_flags_offset = 0
        pos = vertex_flags_offset + vertex_count
        face_indices_flag_offset = pos
        pos += face_count
        face_priority_offset = pos
        if priority_flag == 255:
            pos += face_count

        face_group_offset = pos
        if face_group_flag == 1:
            pos += face_count

        face_properties_offset = pos
        if face_properties_flag == 1:
            pos += face_count

        vertex_groups_offset = pos
        pos += skeletal_length
        alpha_offset = pos

        if alpha_flag == 1:
            pos += face_count

        face_indices_offset = pos
        pos += face_indices_length

        face_colors_offset = pos
        pos += face_count * 2

        texture_vertices_offset = pos
        pos += textured_face_count * 6

        vertices_x_offset = pos
        pos += vertices_x_length

        vertices_y_offset = pos
        pos += vertices_y_length

        vertices_z_offset = pos

        self.vertices_x = [0] * vertex_count
        self.vertices_y = [0] * vertex_count
        self.vertices_z = [0] * vertex_count
        self.face_indices_a = [0] * face_count
        self.face_indices_b = [0] * face_count
        self.face_indices_c = [0] * face_count

        if textured_face_count > 0:
            self.texture_types = [0] * textured_face_count
            self.texture_coords_p = [0] * textured_face_count
            self.texture_coords_m = [0] * textured_face_count
            self.texture_coords_n = [0] * textured_face_count

        if vertex_group_offset == 1:
            self.vertex_groups = [0] * vertex_count

        if face_properties_flag == 1:
            self.face_draw_types = [0] * face_count
            self.texture_coord_indices = [0] * face_count
            self.texture_ids = [0] * face_count

        if priority_flag == 255:
            self.face_priorities = [0] * face_count
        else:
            self.model_priority = priority_flag

        if alpha_flag == 1:
            self.face_alphas = [0] * face_count

        if face_group_flag == 1:
            self.face_groups = [0] * face_count

        if skeletal_flag == 1:
            self.skeletal_bones = [[] for _ in range(vertex_count)]
            self.skeletal_weights = [[] for _ in range(vertex_count)]

        self.face_colors = [0] * face_count

        buffer_indices.set_pos(vertex_flags_offset)
        buffer_face_properties.set_pos(vertices_x_offset)
        buffer_face_priorities.set_pos(vertices_y_offset)
        buffer_face_alphas.set_pos(vertices_z_offset)
        buffer_face_groups.set_pos(vertex_groups_offset)
        x = y = z = 0
        for vertex in range(vertex_count):
            position_flag = buffer_indices.read_unsigned_byte()
            dx = dy = dz = 0
            if position_flag & 1:
                dx = buffer_face_properties.readSignedSmart

            if position_flag & 2:
                dy = buffer_face_priorities.readSignedSmart

            if position_flag & 4:
                dz = buffer_face_alphas.readSignedSmart

            self.vertices_x[vertex] = x + dx
            self.vertices_y[vertex] = y + dy
            self.vertices_z[vertex] = z + dz
            x = self.vertices_x[vertex]
            y = self.vertices_y[vertex]
            z = self.vertices_z[vertex]

            if vertex_group_offset == 1:
                self.vertex_groups[vertex] = buffer_face_groups.read_unsigned_byte()

        if skeletal_flag == 1:
            for vertex in range(vertex_count):
                bone_count = buffer_face_groups.read_unsigned_byte()
                self.skeletal_bones[vertex] = [0] * bone_count
                self.skeletal_weights[vertex] = [0] * bone_count

                for bone in range(bone_count):
                    self.skeletal_bones[vertex][bone] = buffer_face_groups.read_unsigned_byte()
                    self.skeletal_weights[vertex][bone] = buffer_face_groups.read_unsigned_byte()

        buffer_indices.set_pos(face_colors_offset)
        buffer_face_properties.set_pos(face_properties_offset)
        buffer_face_priorities.set_pos(face_priority_offset)
        buffer_face_alphas.set_pos(alpha_offset)
        buffer_face_groups.set_pos(face_group_offset)

        for face in range(face_count):
            self.face_colors[face] = buffer_indices.read_unsigned_short()

            if face_properties_flag == 1:
                flag = buffer_face_properties.read_unsigned_byte()

                if flag & 1 == 1:
                    self.face_draw_types[face] = 1
                    face_draw_types = True
                else:
                    self.face_draw_types[face] = 0

                if flag & 2 == 2:
                    self.texture_coord_indices[face] = flag >> 2
                    self.texture_ids[face] = self.face_colors[face]
                    self.face_colors[face] = 127

                    if self.texture_ids[face] != -1:
                        has_texture_type1 = True

                    if self.texture_coord_indices[face] != -1:
                        has_texture_type2 = True
                else:
                    self.texture_coord_indices[face] = -1
                    self.texture_ids[face] = -1

            if priority_flag == 255:
                self.face_priorities[face] = buffer_face_priorities.read_signed_byte()

            if alpha_flag == 1:
                self.face_alphas[face] = buffer_face_alphas.read_unsigned_byte()

            if face_group_flag == 1:
                self.face_groups[face] = buffer_face_groups.read_unsigned_byte()

        buffer_indices.set_pos(face_indices_offset)
        buffer_face_properties.set_pos(face_indices_flag_offset)
        a = b = c = last = 0
        for face in range(face_count):
            orientation = buffer_face_properties.read_unsigned_byte()

            if orientation == 1:
                a = buffer_indices.readSignedSmart + last
                b = buffer_indices.readSignedSmart + a
                c = buffer_indices.readSignedSmart + b
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 2:
                b = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 3:
                a = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 4:
                tmp = a
                a = b
                b = tmp
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

        buffer_indices.set_pos(texture_vertices_offset)

        for face in range(textured_face_count):
            self.texture_types[face] = 0
            self.texture_coords_p[face] = buffer_indices.read_unsigned_short()
            self.texture_coords_m[face] = buffer_indices.read_unsigned_short()
            self.texture_coords_n[face] = buffer_indices.read_unsigned_short()



    def decode_new(self, data):
        self.model_type = "new"

        buffer_indices = ByteBuffer(data)
        buffer_face_properties = ByteBuffer(data)
        buffer_face_priorities = ByteBuffer(data)
        buffer_face_alphas = ByteBuffer(data)
        buffer_face_groups = ByteBuffer(data)
        buffer_texture_ids = ByteBuffer(data)
        buffer_texture_coords = ByteBuffer(data)

        buffer_indices.set_pos(len(data) - 23)
        vertexCount = buffer_indices.read_unsigned_short()
        face_count = buffer_indices.read_unsigned_short()
        textured_face_count = buffer_indices.read_unsigned_byte()

        face_type_flag = buffer_indices.read_unsigned_byte()
        hasVersion = (face_type_flag & 0x8) == 8

        has_extended_vertex_groups = (face_type_flag & 0x10) == 16
        has_extended_face_groups = (face_type_flag & 0x20) == 32

        if hasVersion:
            buffer_indices.dec_position(7)
            self.model_version = buffer_indices.read_unsigned_byte()
            buffer_indices.inc_position(6)

        priority_flag = buffer_indices.read_unsigned_byte()
        face_alpha_flag = buffer_indices.read_unsigned_byte()
        face_group_flag = buffer_indices.read_unsigned_byte()
        texture_flag = buffer_indices.read_unsigned_byte()
        vertex_group_flag = buffer_indices.read_unsigned_byte()

        vertices_x_length = buffer_indices.read_unsigned_short()
        vertices_y_length = buffer_indices.read_unsigned_short()
        vertices_z_length = buffer_indices.read_unsigned_short()
        face_indices_length = buffer_indices.read_unsigned_short()
        texture_coordinate_indices_length = buffer_indices.read_unsigned_short()

        if has_extended_vertex_groups:
            buffer_indices.read_unsigned_short()

        if has_extended_face_groups:
            buffer_indices.read_unsigned_short()

        simple_texture_count = 0
        complex_texture_count = 0
        cube_texture_count = 0
        if textured_face_count > 0:
            self.texture_types = [0] * textured_face_count
            buffer_indices.set_pos(0)
            for face in range(textured_face_count):
                texture_type = self.texture_types[face] = buffer_indices.read_signed_byte()

                if texture_type == 0:
                    simple_texture_count += 1

                if 1 <= texture_type <= 3:
                    complex_texture_count += 1

                if texture_type == 2:
                    cube_texture_count += 1

        pos = textured_face_count

        vertex_flags_offset = pos
        pos += vertexCount

        face_type_offset = pos
        if face_type_flag == 1:
            pos += face_count

        face_indices_flags_offset = pos
        pos += face_count

        priorities_offset = pos
        if priority_flag == 255:
            pos += face_count

        face_labels_offset = pos
        if face_group_flag == 1:
            pos += face_count

        vertexLabelsOffset = pos
        if vertex_group_flag == 1:
            pos += vertexCount

        alpha_offset = pos
        if face_alpha_flag == 1:
            pos += face_count

        face_indices_offset = pos
        pos += face_indices_length

        texture_ids_offset = pos
        if texture_flag == 1:
            pos += face_count * 2

        texture_coordinate_indices_offset = pos
        pos += texture_coordinate_indices_length

        face_colors_offset = pos
        pos += face_count * 2

        vertices_x_offset = pos
        pos += vertices_x_length

        vertices_y_offset = pos
        pos += vertices_y_length

        vertices_z_offset = pos
        pos += vertices_z_length

        texture_vertices_offset = pos
        pos += simple_texture_count * 6

        not_sure = pos
        pos += complex_texture_count * 6

        face_priorities_offset = pos
        pos += complex_texture_count * 6

        face_alphas_offset = pos
        pos += complex_texture_count * 2

        face_groups_offset = pos
        pos += complex_texture_count

        unused5Offset = pos
        pos += complex_texture_count * 2 + cube_texture_count * 2


        self.vertex_count = vertexCount
        self.face_count = face_count
        self.textured_face_count = textured_face_count


        self.vertices_x = [0] * vertexCount
        self.vertices_y = [0] * vertexCount
        self.vertices_z = [0] * vertexCount
        self.face_indices_a = [0] * face_count
        self.face_indices_b = [0] * face_count
        self.face_indices_c = [0] * face_count

        if vertex_group_flag == 1:
            self.vertex_groups = [0] * vertexCount

        if face_type_flag == 1:
            self.face_draw_types = [0] * face_count

        if priority_flag == 255:
            self.face_priorities = [0] * face_count
        else:
            self.model_priority = priority_flag

        if face_alpha_flag == 1:
            self.face_alphas = [0] * face_count

        if face_group_flag == 1:
            self.face_groups = [0] * face_count
        if texture_flag == 1:
            self.texture_ids = [0] * face_count

        if texture_flag == 1 and textured_face_count > 0:
            self.texture_coord_indices = [0] * face_count

        self.face_colors = [0] * face_count
        if textured_face_count > 0:
            self.texture_coords_p = [0] * textured_face_count
            self.texture_coords_m = [0] * textured_face_count
            self.texture_coords_n = [0] * textured_face_count

        buffer_indices.set_pos(vertex_flags_offset)
        buffer_face_properties.set_pos(vertices_x_offset)
        buffer_face_priorities.set_pos(vertices_y_offset)
        buffer_face_alphas.set_pos(vertices_z_offset)
        buffer_face_groups.set_pos(vertexLabelsOffset)
        x = y = z = 0
        for vertex in range(vertexCount):
            position_flag = buffer_indices.read_unsigned_byte()
            dx = dy = dz = 0
            if position_flag & 1:
                dx = buffer_face_properties.readSignedSmart

            if position_flag & 2:
                dy = buffer_face_priorities.readSignedSmart

            if position_flag & 4:
                dz = buffer_face_alphas.readSignedSmart
            self.vertices_x[vertex] = x + dx
            self.vertices_y[vertex] = y + dy
            self.vertices_z[vertex] = z + dz
            x = self.vertices_x[vertex]
            y = self.vertices_y[vertex]
            z = self.vertices_z[vertex]
            if self.vertex_groups:
                self.vertex_groups[vertex] = buffer_face_groups.read_unsigned_byte()

        buffer_indices.set_pos(face_colors_offset)
        buffer_face_properties.set_pos(face_type_offset)
        buffer_face_priorities.set_pos(priorities_offset)
        buffer_face_alphas.set_pos(alpha_offset)
        buffer_face_groups.set_pos(face_labels_offset)
        buffer_texture_ids.set_pos(texture_ids_offset)
        buffer_texture_coords.set_pos(texture_coordinate_indices_offset)
        for face in range(face_count):
            self.face_colors[face] = buffer_indices.read_unsigned_short()

            if face_type_flag == 1:
                self.face_draw_types[face] = buffer_face_properties.read_signed_byte()
            if priority_flag == 255:
                self.face_priorities[face] = buffer_face_priorities.read_signed_byte()
            if face_alpha_flag == 1:
                self.face_alphas[face] = buffer_face_alphas.read_unsigned_byte()
            if face_group_flag == 1:
                self.face_groups[face] = buffer_face_groups.read_unsigned_byte()

            if texture_flag == 1:
                self.texture_ids[face] = buffer_texture_ids.read_unsigned_short() - 1

            if self.texture_coord_indices and self.texture_ids[face] != -1:
                self.texture_coord_indices[face] = buffer_texture_coords.read_unsigned_byte() - 1

        buffer_indices.set_pos(face_indices_offset)
        buffer_face_properties.set_pos(face_indices_flags_offset)
        a = b = c = last = 0
        for face in range(face_count):
            opcode = buffer_face_properties.read_unsigned_byte()
            if opcode == 1:
                a = buffer_indices.readSignedSmart + last
                last = a
                b = buffer_indices.readSignedSmart + last
                last = b
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 2:
                b = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 3:
                a = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
            if opcode == 4:
                temp = a
                a = b
                b = temp
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

        buffer_indices.set_pos(texture_vertices_offset)
        buffer_face_properties.set_pos(not_sure)
        buffer_face_priorities.set_pos(face_priorities_offset)
        buffer_face_alphas.set_pos(face_alphas_offset)
        buffer_face_groups.set_pos(face_groups_offset)
        buffer_texture_ids.set_pos(unused5Offset)
        for face in range(textured_face_count):
            opcode = self.texture_types[face] & 0xFF
            if opcode == 0:
                self.texture_coords_p[face] = buffer_indices.read_unsigned_short()
                self.texture_coords_m[face] = buffer_indices.read_unsigned_short()
                self.texture_coords_n[face] = buffer_indices.read_unsigned_short()

    def decode_type_three(self, data):
        self.model_type = "type 3"


        buffer_indices = ByteBuffer(data)
        buffer_face_properties = ByteBuffer(data)
        buffer_face_priorities = ByteBuffer(data)
        buffer_face_alphas = ByteBuffer(data)
        buffer_face_groups = ByteBuffer(data)
        buffer_texture_ids = ByteBuffer(data)
        buffer_texture_coords = ByteBuffer(data)

        buffer_indices.set_pos(len(data) - 26)
        vertex_count = buffer_indices.read_unsigned_short()
        face_count = buffer_indices.read_unsigned_short()
        textured_face_count = buffer_indices.read_unsigned_byte()

        self.vertex_count = vertex_count
        self.face_count = face_count
        self.textured_face_count = textured_face_count

        face_type_flag = buffer_indices.read_unsigned_byte()
        priority_flag = buffer_indices.read_unsigned_byte()
        alpha_flag = buffer_indices.read_unsigned_byte()
        face_label_flag = buffer_indices.read_unsigned_byte()
        texture_flag = buffer_indices.read_unsigned_byte()
        vertex_label_flag = buffer_indices.read_unsigned_byte()
        skeletal_flag = buffer_indices.read_unsigned_byte()

        vertices_x_length = buffer_indices.read_unsigned_short()
        vertices_y_length = buffer_indices.read_unsigned_short()
        vertices_z_length = buffer_indices.read_unsigned_short()
        face_indices_length = buffer_indices.read_unsigned_short()
        texture_coordinate_indices_length = buffer_indices.read_unsigned_short()
        skeletal_length = buffer_indices.read_unsigned_short()

        simple_texture_count = 0
        complex_texture_count = 0
        cube_texture_count = 0
        if textured_face_count > 0:
            self.texture_types = [0] * textured_face_count
            buffer_indices.set_pos(0)
            for face in range(textured_face_count):
                texture_type = self.texture_types[face] = buffer_indices.read_signed_byte()

                if texture_type == 0:
                    simple_texture_count += 1

                if 1 <= texture_type <= 3:
                    complex_texture_count += 1

                if texture_type == 2:
                    cube_texture_count += 1

        pos = textured_face_count + vertex_count

        face_type_offset = pos
        if face_type_flag == 1:
            pos += face_count

        face_indices_flag_offset = pos
        pos += face_count

        priorities_offset = pos
        if priority_flag == 255:
            pos += face_count

        face_labels_offset = pos
        if face_label_flag == 1:
            pos += face_count

        vertex_labels_offset = pos
        pos += skeletal_length

        alpha_offset = pos
        if alpha_flag == 1:
            pos += face_count

        face_indices_offset = pos
        pos += face_indices_length

        texture_ids_offset = pos
        if texture_flag == 1:
            pos += face_count * 2

        texture_coord_indices_offset = pos
        pos += texture_coordinate_indices_length

        not_sure_offset = pos
        pos += face_count * 2

        vertices_x_offset = pos
        pos += vertices_x_length

        vertices_y_offset = pos
        pos += vertices_y_length

        vertices_z_offset = pos
        pos += vertices_z_length

        texture_vertices_offset = pos
        pos += simple_texture_count * 6

        not_sure = pos
        pos += complex_texture_count * 6

        face_priorities_offset = pos
        pos += complex_texture_count * 6

        face_alphas_offset = pos
        pos += complex_texture_count * 2

        face_groups_offset = pos
        pos += complex_texture_count

        unused5_offset = pos
        pos = pos + complex_texture_count * 2 + cube_texture_count * 2

        self.vertex_count = vertex_count
        self.face_count = face_count
        self.textured_face_count = textured_face_count

        self.vertices_x = [0] * vertex_count
        self.vertices_y = [0] * vertex_count
        self.vertices_z = [0] * vertex_count
        self.face_indices_a = [0] * face_count
        self.face_indices_b = [0] * face_count
        self.face_indices_c = [0] * face_count

        if vertex_label_flag == 1:
            self.vertex_groups = [0] * vertex_count

        if face_type_flag == 1:
            self.face_draw_types = [0] * face_count

        if priority_flag == 255:
            self.face_priorities = [0] * face_count
        else:
            self.model_priority = priority_flag

        if alpha_flag == 1:
            self.face_alphas = [0] * face_count

        if face_label_flag == 1:
            self.face_groups = [0] * face_count

        if texture_flag == 1:
            self.texture_ids = [0] * face_count

        if texture_flag == 1 and textured_face_count > 0:
            self.texture_coord_indices = [0] * face_count

        if skeletal_flag == 1:
            self.skeletal_bones = [[] for _ in range(vertex_count)]
            self.skeletal_weights = [[] for _ in range(vertex_count)]

        self.face_colors = [0] * face_count
        if textured_face_count > 0:
            self.texture_coords_p = [0] * textured_face_count
            self.texture_coords_m = [0] * textured_face_count
            self.texture_coords_n = [0] * textured_face_count

        buffer_indices.set_pos(textured_face_count)
        buffer_face_properties.set_pos(vertices_x_offset)
        buffer_face_priorities.set_pos(vertices_y_offset)
        buffer_face_alphas.set_pos(vertices_z_offset)
        buffer_face_groups.set_pos(vertex_labels_offset)
        x = y = z = 0
        for vertex in range(vertex_count):
            position_flag = buffer_indices.read_unsigned_byte()
            dx = dy = dz = 0
            if position_flag & 1:
                dx = buffer_face_properties.readSignedSmart

            if position_flag & 2:
                dy = buffer_face_priorities.readSignedSmart

            if position_flag & 4:
                dz = buffer_face_alphas.readSignedSmart
            self.vertices_x[vertex] = x + dx
            self.vertices_y[vertex] = y + dy
            self.vertices_z[vertex] = z + dz
            x = self.vertices_x[vertex]
            y = self.vertices_y[vertex]
            z = self.vertices_z[vertex]
            if vertex_label_flag == 1:
                self.vertex_groups[vertex] = buffer_face_groups.read_unsigned_byte()

        if skeletal_flag == 1:
            for vertex in range(vertex_count):
                joint_count = buffer_face_groups.read_unsigned_byte()
                self.skeletal_bones[vertex] = [0] * joint_count
                self.skeletal_weights[vertex] = [0] * joint_count

                for joint in range(joint_count):
                    bone_index = buffer_face_groups.read_unsigned_byte()
                    scale = buffer_face_groups.read_unsigned_byte()
                    self.skeletal_bones[vertex][joint] = bone_index
                    self.skeletal_weights[vertex][joint] = scale

        buffer_indices.set_pos(not_sure_offset)
        buffer_face_properties.set_pos(face_type_offset)
        buffer_face_priorities.set_pos(priorities_offset)
        buffer_face_alphas.set_pos(alpha_offset)
        buffer_face_groups.set_pos(face_labels_offset)
        buffer_texture_ids.set_pos(texture_ids_offset)
        buffer_texture_coords.set_pos(texture_coord_indices_offset)

        for face in range(face_count):
            self.face_colors[face] = buffer_indices.read_unsigned_short()

            if face_type_flag == 1:
                self.face_draw_types[face] = buffer_face_properties.read_signed_byte()

            if priority_flag == 255:
                self.face_priorities[face] = buffer_face_priorities.read_signed_byte()

            if alpha_flag == 1:
                self.face_alphas[face] = buffer_face_alphas.read_unsigned_byte()

            if face_label_flag == 1:
                self.face_groups[face] = buffer_face_groups.read_unsigned_byte()

            if texture_flag == 1:
                self.texture_ids[face] = buffer_texture_ids.read_unsigned_short() - 1

            if self.texture_coord_indices is not None and self.texture_ids[face] != -1:
                self.texture_coord_indices[face] = buffer_texture_coords.read_unsigned_byte() - 1

        buffer_indices.set_pos(face_indices_offset)
        buffer_face_properties.set_pos(face_indices_flag_offset)
        a = b = c = last = 0
        for face in range(face_count):
            orientation = buffer_face_properties.read_unsigned_byte()

            if orientation == 1:
                a = buffer_indices.readSignedSmart + last
                b = buffer_indices.readSignedSmart + a
                c = buffer_indices.readSignedSmart + b
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 2:
                b = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 3:
                a = c
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

            if orientation == 4:
                temp = a
                a = b
                b = temp
                c = buffer_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c

        buffer_indices.set_pos(texture_vertices_offset)
        buffer_face_properties.set_pos(not_sure)
        buffer_face_priorities.set_pos(face_priorities_offset)
        buffer_face_alphas.set_pos(face_alphas_offset)
        buffer_face_groups.set_pos(face_groups_offset)
        buffer_texture_ids.set_pos(texture_coord_indices_offset)

        for face in range(textured_face_count):
            texture_type = self.texture_types[face] & 255

            if texture_type == 0:
                self.texture_coords_p[face] = buffer_indices.read_unsigned_short()
                self.texture_coords_m[face] = buffer_indices.read_unsigned_short()
                self.texture_coords_n[face] = buffer_indices.read_unsigned_short()
        self.convert_textures()

    def convert_textures(self):

        if self.face_draw_types is None or len(self.face_draw_types) < self.face_count:
            return

        if self.textured_face_count == 0:
            return

        if self.texture_coord_indices is None:
            self.texture_coord_indices = [0] * self.face_count

        if self.texture_ids is None:
            self.texture_ids = [0] * self.face_count

        for i in range(self.face_count):
            if self.face_draw_types is not None and self.face_draw_types[i] >= 2:
                texture_index = self.face_draw_types[i] >> 2
                self.texture_coord_indices[i] = texture_index
                self.texture_ids[i] = self.face_colors[i]
            else:
                self.texture_coord_indices[i] = -1
                self. texture_ids[i] = -1

    def is_skeletal(self):
        return self.skeletal_bones is not None

    def create_groups(self):
        if len(self.vertex_groups) > 0:
            vertex_group_count = [0] * 256
            count = 0

            for v in range(self.vertex_count):
                group = self.vertex_groups[v]
                vertex_group_count[group] += 1
                if group > count:
                    count = group

            self.grouped_vertices = [[] for _ in range(count + 1)]

            for group in range(count + 1):
                self.grouped_vertices[group] = [0] * vertex_group_count[group]
                vertex_group_count[group] = 0

            for v in range(self.vertex_count):
                group = self.vertex_groups[v]
                self.grouped_vertices[group][vertex_group_count[group]] = v
                vertex_group_count[group] += 1

        if len(self.face_groups) > 0:
            face_group_count = [0] * 256
            count = 0

            for f in range(self.face_count):
                group = self.face_groups[f]
                face_group_count[group] += 1
                if group > count:
                    count = group

            self.grouped_faces = [[] for _ in range(count + 1)]

            for group in range(count + 1):
                self.grouped_faces[group] = [0] * face_group_count[group]
                face_group_count[group] = 0

            for face in range(self.face_count):
                group = self.face_groups[face]
                self.grouped_faces[group][face_group_count[group]] = face
                face_group_count[group] += 1

        bones = self.skeletal_bones

        if bones is not None:
            self.bone_groups = {}
            for vertex in range(len(bones)):
                for joint in range(len(bones[vertex])):
                    bone_index = bones[vertex][joint]
                    if bone_index not in self.bone_groups:
                        self.bone_groups[bone_index] = []
                    self.bone_groups[bone_index].append(vertex)

    def decode_rs3(self, data):
        buffer_pmn = ByteBuffer(data)
        buffer_scaled_pmn = ByteBuffer(data)
        buffer_texture_scale = ByteBuffer(data)
        buffer_texture_rotation = ByteBuffer(data)
        buffer_texture_direction = ByteBuffer(data)
        buffer_texture_speed = ByteBuffer(data)
        buffer_texture_coordinates = ByteBuffer(data)
        int_0 = buffer_pmn.read_unsigned_byte()
        if int_0 != 1:
            return
        buffer_pmn.read_unsigned_byte()
        self.model_version = buffer_pmn.read_unsigned_byte()
        buffer_pmn.set_pos(len(data) - 26)
        self.vertex_count = buffer_pmn.read_unsigned_short()
        self.face_count = buffer_pmn.read_unsigned_short()
        self.textured_face_count = buffer_pmn.read_unsigned_short()
        flags = buffer_pmn.read_unsigned_byte()
        has_face_info = (flags & 0x1) == 1
        has_particles = (flags & 0x2) == 2
        has_billboards = (flags & 0x4) == 4
        has_extended_vertex_labels = (flags & 0x10) == 16
        has_extended_face_groups = (flags & 0x20) == 32
        has_extended_billboards = (flags & 0x40) == 64
        has_uv_coords = (flags & 0x80) == 128
        model_priority = buffer_pmn.read_unsigned_byte()
        face_alpha_flag = buffer_pmn.read_unsigned_byte()
        face_group_flag = buffer_pmn.read_unsigned_byte()
        texture_flag = buffer_pmn.read_unsigned_byte()
        vertex_label_flag = buffer_pmn.read_unsigned_byte()
        vertices_x_length = buffer_pmn.read_unsigned_short()
        vertices_y_length = buffer_pmn.read_unsigned_short()
        vertices_z_length = buffer_pmn.read_unsigned_short()
        face_indices_length = buffer_pmn.read_unsigned_short()
        texture_tri_indices_length = buffer_pmn.read_unsigned_short()
        vertex_labels_length = buffer_pmn.read_unsigned_short()
        face_labels_length = buffer_pmn.read_unsigned_short()
        if not has_extended_vertex_labels:
            if vertex_label_flag == 1:
                vertex_labels_length = self.vertex_count
            else:
                vertex_labels_length = 0

        if not has_extended_face_groups:
            if face_group_flag == 1:
                face_labels_length = self.face_count
            else:
                face_labels_length = 0

        simple_texture_count = 0
        complex_texture_count = 0
        cube_texture_count = 0
        if self.textured_face_count > 0:
            self.texture_types = [0] * self.textured_face_count
            buffer_pmn.set_pos(3)
            for particle_offset in range(self.textured_face_count):
                texture_type = self.texture_types[particle_offset] = buffer_pmn.read_signed_byte()
                if texture_type == 0:
                    simple_texture_count += 1
                if 1 <= texture_type <= 3:
                    complex_texture_count += 1
                if texture_type == 2:
                    cube_texture_count += 1

        pos = 3 + self.textured_face_count
        position_flags_offset = pos
        pos += self.vertex_count
        face_info_offset = pos
        if has_face_info:
            pos += self.face_count
        face_index_flag_offset = pos
        pos += self.face_count
        face_priorities_offset = pos
        if model_priority == 255:
            pos += self.face_count
        face_labels_offset = pos
        pos += face_labels_length
        vertex_labels_offset = pos
        pos += vertex_labels_length
        face_alpha_offset = pos
        if face_alpha_flag == 1:
            pos += self.face_count
        faces_indices_offset = pos
        pos += face_indices_length
        face_texture_ids_offset = pos
        if texture_flag == 1:
            pos += self.face_count * 2
        texture_coordinate_indices_offset = pos
        pos += texture_tri_indices_length
        face_colors_offset = pos
        pos += self.face_count * 2
        vertices_x_offset = pos
        pos += vertices_x_length
        vertices_y_offset = pos
        pos += vertices_y_length
        vertices_z_offset = pos
        pos += vertices_z_length
        texture_vertices_offset = pos
        pos += simple_texture_count * 6
        complex_texture_offset = pos
        pos += complex_texture_count * 6
        particle_version = 6
        if self.model_version == 14:
            particle_version = 7
        elif self.model_version >= 15:
            particle_version = 9
        texture_scale_offset = pos
        pos += complex_texture_count * particle_version
        texture_rotation_offset = pos
        pos += complex_texture_count
        texture_direction_offset = pos
        pos += complex_texture_count
        texture_speed_offset = pos
        pos += complex_texture_count + cube_texture_count * 2
        uv_face_index_offset = len(data)
        uv_vertex_offset = len(data)
        uv_u_coord_offset = len(data)
        uv_v_coord_offset = len(data)
        if has_uv_coords:
            uv_buffer = ByteBuffer(data)
            uv_buffer.set_pos(len(data) - 26)
            uv_buffer.dec_position(data[uv_buffer.get_pos() - 1])
            self.uv_coords_count = uv_buffer.read_unsigned_short()
            uv_data_size = uv_buffer.read_unsigned_short()
            uv_index_size = uv_buffer.read_unsigned_short()
            uv_face_index_offset = pos + uv_data_size
            uv_vertex_offset = uv_face_index_offset + uv_index_size
            uv_u_coord_offset = uv_vertex_offset + self.vertex_count
            uv_v_coord_offset = uv_u_coord_offset + self.uv_coords_count * 2

        self.vertices_x = [0] * self.vertex_count
        self.vertices_y = [0] * self.vertex_count
        self.vertices_z = [0] * self.vertex_count
        self.face_indices_a = [0] * self.face_count
        self.face_indices_b = [0] * self.face_count
        self.face_indices_c = [0] * self.face_count
        if vertex_label_flag == 1:
            self.vertex_groups = [0] * self.vertex_count

        if has_face_info:
            self.face_draw_types = [0] * self.face_count

        if model_priority == 255:
            self.face_priorities = [0] * self.face_count
        else:
            self.model_priority = model_priority

        if face_alpha_flag == 1:
            self.face_alphas = [0] * self.face_count

        if face_group_flag == 1:
            self.face_groups = [0] * self.face_count

        if texture_flag == 1:
            self.texture_ids = [0] * self.face_count

        if texture_flag == 1 and (self.textured_face_count > 0 or self.uv_coords_count > 0):
            self.texture_coord_indices = [0] * self.face_count

        self.face_colors = [0] * self.face_count
        if self.textured_face_count > 0:
            self.texture_coords_p = [0] * self.textured_face_count
            self.texture_coords_m = [0] * self.textured_face_count
            self.texture_coords_n = [0] * self.textured_face_count
            if complex_texture_count > 0:
                self.texture_scale_x = [0] * complex_texture_count
                self.texture_scale_y = [0] * complex_texture_count
                self.texture_scale_z = [0] * complex_texture_count
                self.texture_rotation = [0] * complex_texture_count
                self.texture_direction = [0] * complex_texture_count
                self.texture_speed = [0] * complex_texture_count

            if cube_texture_count > 0:
                self.texture_u_trans = [0] * cube_texture_count
                self.texture_v_trans = [0] * cube_texture_count

        buffer_pmn.set_pos(position_flags_offset)
        buffer_scaled_pmn.set_pos(vertices_x_offset)
        buffer_texture_scale.set_pos(vertices_y_offset)
        buffer_texture_rotation.set_pos(vertices_z_offset)
        buffer_texture_direction.set_pos(vertex_labels_offset)

        x = 0
        y = 0
        z = 0

        for vertex in range(self.vertex_count):
            position_flag = buffer_pmn.read_unsigned_byte()
            dx = 0
            dy = 0
            dz = 0
            if position_flag & 0x1 != 0:
                dx = buffer_scaled_pmn.readSignedSmart
            if position_flag & 0x2 != 0:
                dy = buffer_texture_scale.readSignedSmart
            if position_flag & 0x4 != 0:
                dz = buffer_texture_rotation.readSignedSmart

            self.vertices_x[vertex] = x + dx
            self.vertices_y[vertex] = y + dy
            self.vertices_z[vertex] = z + dz
            x = self.vertices_x[vertex]
            y = self.vertices_y[vertex]
            z = self.vertices_z[vertex]
            if vertex_label_flag == 1:
                if has_extended_vertex_labels:
                    self.vertex_groups[vertex] = buffer_texture_direction.read_signed_smart_minus_one()
                else:
                    self.vertex_groups[vertex] = buffer_texture_direction.read_unsigned_byte()
                    if self.vertex_groups[vertex] == 255:
                        self.vertex_groups[vertex] = -1

        if self.uv_coords_count > 0:
            buffer_pmn.set_pos(uv_vertex_offset)
            buffer_scaled_pmn.set_pos(uv_u_coord_offset)
            buffer_texture_scale.set_pos(uv_v_coord_offset)
            self.uv_map_vertex_offset = [0] * self.vertex_count
            vertex = 0
            for offset in range(self.vertex_count):
                self.uv_map_vertex_offset[vertex] = offset
                offset += buffer_pmn.read_unsigned_byte()
            self.uv_face_indices_a = [0] * self.face_count
            self.uv_face_indices_b = [0] * self.face_count
            self.uv_face_indices_c = [0] * self.face_count
            self.uv_coord_u = [0.0] * self.uv_coords_count
            self.uv_coord_v = [0.0] * self.uv_coords_count
            for mapping in range(self.uv_coords_count):
                self.uv_coord_u[mapping] = buffer_scaled_pmn.read_signed_byte() / 4096.0
                self.uv_coord_v[mapping] = buffer_texture_scale.read_signed_byte() / 4096.0

        buffer_pmn.set_pos(face_colors_offset)
        buffer_scaled_pmn.set_pos(face_info_offset)
        buffer_texture_scale.set_pos(face_priorities_offset)
        buffer_texture_rotation.set_pos(face_alpha_offset)
        buffer_texture_direction.set_pos(face_labels_offset)
        buffer_texture_speed.set_pos(face_texture_ids_offset)
        buffer_texture_coordinates.set_pos(texture_coordinate_indices_offset)

        for face in range(self.face_count):
            self.face_colors[face] = buffer_pmn.read_unsigned_short()
            if has_face_info:
                self.face_draw_types[face] = buffer_scaled_pmn.read_signed_byte()
            if model_priority == 255:
                self.face_priorities[face] = buffer_texture_scale.read_signed_byte()
            if face_alpha_flag == 1:
                self.face_alphas[face] = buffer_texture_rotation.read_signed_byte()
            if face_group_flag == 1:
                if has_extended_face_groups:
                    self.face_groups[face] = buffer_texture_direction.read_signed_smart_minus_one()
                else:
                    self.face_groups[face] = buffer_texture_direction.read_unsigned_byte()
                    if self.face_groups[face] == 255:
                        self.face_groups[face] = -1
            if texture_flag == 1:
                self.texture_ids[face] = buffer_texture_speed.read_unsigned_short() - 1
            if self.texture_coord_indices is not None:
                if self.texture_ids[face] != -1:
                    if self.model_version >= 16:
                        self.texture_coord_indices[face] = buffer_texture_coordinates.readUnsignedSmart() - 1
                    else:
                        self.texture_coord_indices[face] = buffer_texture_coordinates.read_unsigned_byte() - 1
                else:
                    self.texture_coord_indices[face] = -1

        self.highest_vertex = -1
        buffer_pmn.set_pos(faces_indices_offset)
        buffer_scaled_pmn.set_pos(face_index_flag_offset)
        buffer_texture_scale.set_pos(uv_face_index_offset)
        self.decode_faces(buffer_pmn, buffer_scaled_pmn, buffer_texture_scale)
        buffer_pmn.set_pos(texture_vertices_offset)
        buffer_scaled_pmn.set_pos(complex_texture_offset)
        buffer_texture_scale.set_pos(texture_scale_offset)
        buffer_texture_rotation.set_pos(texture_rotation_offset)
        buffer_texture_direction.set_pos(texture_direction_offset)
        buffer_texture_speed.set_pos(texture_speed_offset)
        self.decode_mapping(buffer_pmn, buffer_scaled_pmn, buffer_texture_scale, buffer_texture_rotation,
                            buffer_texture_direction, buffer_texture_speed)
        buffer_pmn.set_pos(pos)
        if has_particles:
            emitter_count = buffer_pmn.read_unsigned_byte()
            if emitter_count > 0:
                self.emitters = []
                for index in range(emitter_count):
                    emitter = buffer_pmn.read_unsigned_short()
                    face = buffer_pmn.read_unsigned_short()
                    if model_priority == 255:
                        priority = self.face_priorities[face]
                    else:
                        priority = model_priority
                    self.emitters.append(
                        ModelEmitter(emitter, face, self.face_indices_a[face], self.face_indices_b[face],
                                     self.face_indices_c[face], priority))
            effector_count = buffer_pmn.read_unsigned_byte()
            if effector_count > 0:
                self.effectors = []
                for effectorIndex in range(effector_count):
                    billboard_id = buffer_pmn.read_unsigned_short()
                    vertex = buffer_pmn.read_unsigned_short()
                    self.effectors.append(ModelEffector(billboard_id, vertex))

        if has_billboards:
            billboard_count = buffer_pmn.read_unsigned_byte()
            if billboard_count > 0:
                self.billboards = []
                for billboardIndex in range(billboard_count):
                    billboard_id = buffer_pmn.read_unsigned_short()
                    face = buffer_pmn.read_unsigned_short()
                    if has_extended_billboards:
                        not_sure = buffer_pmn.read_signed_smart_minus_one()
                    else:
                        not_sure = buffer_pmn.read_unsigned_byte()
                        if not_sure == 255:
                            not_sure = -1
                    scalar = buffer_pmn.read_signed_byte()
                    self.billboards.append(ModelBillboard(billboard_id, face, not_sure, scalar))

    def decode_faces(self, buffer_face_indices, buffer_flag, buffer_uv):
        a = 0
        b = 0
        c = 0
        last = 0

        for face in range(self.face_count):
            flag = buffer_flag.read_unsigned_byte()
            orientation = flag & 0x7
            if orientation == 1:
                self.face_indices_a[face] = a = buffer_face_indices.readSignedSmart + last
                self.face_indices_b[face] = b = buffer_face_indices.readSignedSmart + a
                self.face_indices_c[face] = c = buffer_face_indices.readSignedSmart + b
                last = c
                if a > self.highest_vertex:
                    self.highest_vertex = a
                if b > self.highest_vertex:
                    self.highest_vertex = b
                if c > self.highest_vertex:
                    self.highest_vertex = c
            if orientation == 2:
                b = c
                c = buffer_face_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
                if c > self.highest_vertex:
                    self.highest_vertex = c
            if orientation == 3:
                a = c
                c = buffer_face_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = b
                self.face_indices_c[face] = c
                if c > self.highest_vertex:
                    self.highest_vertex = c
            if orientation == 4:
                tmp = a
                a = b
                b = tmp
                c = buffer_face_indices.readSignedSmart + last
                last = c
                self.face_indices_a[face] = a
                self.face_indices_b[face] = tmp
                self.face_indices_c[face] = c
                if c > self.highest_vertex:
                    self.highest_vertex = c
            if self.uv_coords_count > 0 and (flag & 0x8) != 0:
                self.uv_face_indices_a[face] = buffer_uv.read_unsigned_byte()
                self.uv_face_indices_b[face] = buffer_uv.read_unsigned_byte()
                self.uv_face_indices_c[face] = buffer_uv.read_unsigned_byte()

        self.highest_vertex += 1

    def decode_mapping(self, buffer_pmn, buffer_scaled_pmn, buffer_texture_scale, buffer_texture_rotation,
                       buffer_texture_direction, buffer_texture_speed):
        for textured_face in range(self.textured_face_count):
            mapping = self.texture_types[textured_face] & 0xFF
            if mapping == 0:
                self.texture_coords_p[textured_face] = buffer_pmn.read_unsigned_short()
                self.texture_coords_m[textured_face] = buffer_pmn.read_unsigned_short()
                self.texture_coords_n[textured_face] = buffer_pmn.read_unsigned_short()
            if mapping == 1:
                self.texture_coords_p[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                self.texture_coords_m[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                self.texture_coords_n[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                if self.model_version < 15:
                    self.texture_scale_x[textured_face] = buffer_texture_scale.read_unsigned_short()
                    if self.model_version < 14:
                        self.texture_scale_y[textured_face] = buffer_texture_scale.read_unsigned_short()
                    else:
                        self.texture_scale_y[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_z[textured_face] = buffer_texture_scale.read_unsigned_short()
                else:
                    self.texture_scale_x[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_y[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_z[textured_face] = buffer_texture_scale.read24_bit_int()
                self.texture_rotation[textured_face] = buffer_texture_rotation.read_signed_byte()
                self.texture_direction[textured_face] = buffer_texture_direction.read_signed_byte()
                self.texture_speed[textured_face] = buffer_texture_speed.read_signed_byte()
            if mapping == 2:
                self.texture_coords_p[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                self.texture_coords_m[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                self.texture_coords_n[textured_face] = buffer_scaled_pmn.read_unsigned_short()
                if self.model_version < 15:
                    self.texture_scale_x[textured_face] = buffer_texture_scale.read_unsigned_short()
                    if self.model_version < 14:
                        self.texture_scale_y[textured_face] = buffer_texture_scale.read_unsigned_short()
                    else:
                        self.texture_scale_y[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_z[textured_face] = buffer_texture_scale.read_unsigned_short()
                else:
                    self.texture_scale_x[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_y[textured_face] = buffer_texture_scale.read24_bit_int()
                    self.texture_scale_z[textured_face] = buffer_texture_scale.read24_bit_int()
                self.texture_rotation[textured_face] = buffer_texture_rotation.read_signed_byte()
                self.texture_direction[textured_face] = buffer_texture_direction.read_signed_byte()
                self.texture_speed[textured_face] = buffer_texture_speed.read_signed_byte()
                self.texture_u_trans[textured_face] = buffer_texture_speed.read_signed_byte()
                self.texture_v_trans[textured_face] = buffer_texture_speed.read_signed_byte()


class ModelEmitter:
    def __init__(self, id, face, vertex_a, vertex_b, vertex_c, priority):
        self.id = id
        self.face = face
        self.vertex_a = vertex_a
        self.vertex_b = vertex_b
        self.vertex_c = vertex_c
        self.priority = priority
        self.x3 = 0
        self.y3 = 0
        self.y2 = 0
        self.x1 = 0
        self.z1 = 0
        self.x2 = 0
        self.y1 = 0
        self.z2 = 0
        self.z3 = 0

    def transform(self, face, a, b, c):
        return ModelEmitter(self.id, face, a, b, c, self.priority)


class ModelEffector:
    def __init__(self, id, vertex):
        self.id = id
        self.vertex = vertex
        self.x = 0
        self.z = 0
        self.y = 0

    def transform(self, vertex):
        return ModelEffector(self.id, vertex)


class ModelBillboard:
    def __init__(self, id, face, not_sure, scalar):
        self.id = id
        self.face = face
        self.not_sure = not_sure
        self.scalar = scalar

    def by_face(self, face):
        return ModelBillboard(self.id, face, self.not_sure, self.scalar)
