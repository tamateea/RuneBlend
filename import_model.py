import bpy
import numpy
from runeblend.runescape_mesh import RunescapeMesh
from runeblend.materials import Materials
import numpy as np


def read_mesh(filepath):
    try:
        with open(filepath, "rb") as file:
            data = file.read()

        mesh = RunescapeMesh()
        mesh.decode(mesh, data)
        return mesh
    except IOError:
        print("Error: Failed to read file.")


def apply_uv_texture(rs_mesh, blender_mesh):
    if rs_mesh.face_indices_a and rs_mesh.face_indices_b and rs_mesh.face_indices_c:
        uv_layer = blender_mesh.uv_layers.new()
        uv_data = [(0.0, 0.0)] * (rs_mesh.face_count * 3)

        # Create uv coordinate for each color or generate uv coordinates from pmn mappings
        i = 0
        for face in range(rs_mesh.face_count):
            if rs_mesh.texture_ids is not None and rs_mesh.texture_ids[face] != -1:
                uv_coordinates = get_uv_from_pmn(rs_mesh, face)
                for uv_coord in zip(uv_coordinates[0], uv_coordinates[1]):
                    uv_data[i] = uv_coord
                    i += 1
            else:
                face_color = rs_mesh.face_colors[face]
                uv_coordinates = get_uv_coordinates(face_color)
                for _ in range(3):
                    uv_data[i] = uv_coordinates
                    i += 1

        # Set UV coordinates for the mesh
        for polygon in blender_mesh.polygons:
            for loop_index in polygon.loop_indices:
                uv_layer.data[loop_index].uv = uv_data[loop_index]


def create_blender_mesh(rs_mesh):
    # Create a new mesh
    blender_mesh = bpy.data.meshes.new("Mesh")

    # since it's runescapes XYZ is different, and y axis inverted
    vertices = [
        ((rs_mesh.vertices_x[i] * 0.0078125), rs_mesh.vertices_z[i] * 0.0078125, (-rs_mesh.vertices_y[i] * 0.0078125))
        for i in range(rs_mesh.vertex_count)]
    # Set faces
    faces = [(rs_mesh.face_indices_a[i], rs_mesh.face_indices_b[i], rs_mesh.face_indices_c[i]) for i in
             range(rs_mesh.face_count)]
    # Set the mesh data
    blender_mesh.from_pydata(vertices, [], faces)
    blender_mesh.update()

    # Set the uv data for each face
    apply_uv_texture(rs_mesh, blender_mesh)

    rs_mesh.create_groups()

    # Create a new object for the mesh
    obj = bpy.data.objects.new("runescape_object", blender_mesh)

    vertex_group_labels = set(rs_mesh.vertex_groups)  # Get unique vertex labels

    skeletal = rs_mesh.is_skeletal()

    if not skeletal:
        for label in vertex_group_labels:
            vertex_group = obj.vertex_groups.new(name=f"{label}")
            vertex_indices = [i for i, value in enumerate(rs_mesh.vertex_groups) if value == label]
            weight = label / 100.0
            vertex_group.add(vertex_indices, weight, 'REPLACE')

            # Set the same weight for all vertices in the group
            for vertex_index in vertex_indices:
                vertex_group.add([vertex_index], weight, 'REPLACE')
    else:
        create_skeletal_groups(obj, rs_mesh)

    Materials.create_or_get_palette_material(obj)

    for face in range(rs_mesh.face_count):
        if rs_mesh.face_alphas is not None and len(rs_mesh.face_alphas) > 0 and rs_mesh.face_alphas[face] != 0:
            alpha = rs_mesh.face_alphas[face]
            mat = Materials.create_or_get_alpha_palette_material(obj, alpha)
            obj.data.polygons[face].material_index = obj.data.materials.find(mat.name)
        elif rs_mesh.texture_ids is not None and rs_mesh.texture_ids[face] != -1:
            texture_id = rs_mesh.texture_ids[face]
            mat = Materials.create_or_get_runescape_texture_material(obj, texture_id)
            obj.data.polygons[face].material_index = obj.data.materials.find(mat.name)
        else:
            obj.data.polygons[face].material_index = obj.data.materials.find("palette")

    # Link the object to the scene collection
    scene = bpy.context.scene
    scene.collection.objects.link(obj)

    # Set the viewport shading mode to palette_material preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    # Set the active object and select it
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(True)

    if rs_mesh.face_priorities:
        attribute_values = numpy.zeros(rs_mesh.face_count, dtype=numpy.int8)
        for i in range(rs_mesh.face_count):
            attribute_values[i] = rs_mesh.face_priorities[i]
        attribute = blender_mesh.attributes.new(name='pri', type='INT8', domain='FACE')
        attribute.data.foreach_set("value", attribute_values)

    return obj


def create_skeletal_groups(obj, mesh):
    for vertex_index in range(mesh.vertex_count):
        bone_ids = mesh.skeletal_bones[vertex_index]
        weights = mesh.skeletal_weights[vertex_index]

        for i in range(len(bone_ids)):
            bone_id = bone_ids[i]
            weight = weights[i]
            vertex_group_name = f"Bone_{bone_id}"
            vertex_group = obj.vertex_groups.get(vertex_group_name)
            if not vertex_group:
                vertex_group = obj.vertex_groups.new(name=vertex_group_name)
            vertex_group.add([vertex_index], weight / 255, 'ADD')


def get_hsl_from_coord(u, v):
    width = 128
    height = 512

    # Convert u and v to pixel coordinates
    pixel_x = int(u * width)
    pixel_y = int(v * height)

    # Calculate the index from pixel coordinates
    index = pixel_y * width + pixel_x
    return index


def get_uv_coordinates(index):
    u = (index % 128) / 128
    v = 1.0 - (index / 128) / 512

    return u, v


def get_uv_from_pmn(rs_mesh, i):
    def cross_product(p1, p2):
        return np.cross(p1, p2)

    def dot_product(p1, p2):
        return np.dot(p1, p2)

    coordinate = rs_mesh.texture_coord_indices[i]
    faceA = rs_mesh.face_indices_a[i]
    faceB = rs_mesh.face_indices_b[i]
    faceC = rs_mesh.face_indices_c[i]

    a = np.array([rs_mesh.vertices_x[faceA], rs_mesh.vertices_y[faceA], rs_mesh.vertices_z[faceA]])
    b = np.array([rs_mesh.vertices_x[faceB], rs_mesh.vertices_y[faceB], rs_mesh.vertices_z[faceB]])
    c = np.array([rs_mesh.vertices_x[faceC], rs_mesh.vertices_y[faceC], rs_mesh.vertices_z[faceC]])

    p = np.array([rs_mesh.vertices_x[rs_mesh.texture_coords_p[coordinate]],
                  rs_mesh.vertices_y[rs_mesh.texture_coords_p[coordinate]],
                  rs_mesh.vertices_z[rs_mesh.texture_coords_p[coordinate]]])
    m = np.array([rs_mesh.vertices_x[rs_mesh.texture_coords_m[coordinate]],
                  rs_mesh.vertices_y[rs_mesh.texture_coords_m[coordinate]],
                  rs_mesh.vertices_z[rs_mesh.texture_coords_m[coordinate]]])
    n = np.array([rs_mesh.vertices_x[rs_mesh.texture_coords_n[coordinate]],
                  rs_mesh.vertices_y[rs_mesh.texture_coords_n[coordinate]],
                  rs_mesh.vertices_z[rs_mesh.texture_coords_n[coordinate]]])

    pM = m - p
    pN = n - p
    pA = a - p
    pB = b - p
    pC = c - p

    pMxPn = cross_product(pM, pN)

    uCoordinate = cross_product(pN, pMxPn)
    mU = 1.0 / dot_product(uCoordinate, pM)

    uA = dot_product(uCoordinate, pA) * mU
    uB = dot_product(uCoordinate, pB) * mU
    uC = dot_product(uCoordinate, pC) * mU

    vCoordinate = cross_product(pM, pMxPn)
    mV = 1.0 / dot_product(vCoordinate, pN)
    vA = dot_product(vCoordinate, pA) * mV
    vB = dot_product(vCoordinate, pB) * mV
    vC = dot_product(vCoordinate, pC) * mV

    u = np.array([float(uA), float(uB), float(uC)])
    v = np.array([float(vA), float(vB), float(vC)])
    return u, v


def load(self):
    mesh = read_mesh(self.filepath)
    create_blender_mesh(mesh)
    return {"FINISHED"}
