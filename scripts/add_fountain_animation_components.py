import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"
COLLECTION_NAME = "Fountain_Animation"

POND_CENTER = Vector((4.02, -3.73, 0.245))
LOTUS_CENTER = Vector((4.02, -3.66, 0.31))


def remove_existing_collection():
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def make_material(name, color, alpha=1.0, roughness=0.55, metallic=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*color, alpha)
    material["fountain_material"] = True
    material["web_alpha"] = alpha

    shader = next(
        (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
        None,
    )
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Alpha"].default_value = alpha

    if alpha < 1.0:
        try:
            material.surface_render_method = "DITHERED"
        except (AttributeError, TypeError):
            pass
        material.use_transparency_overlap = False
    return material


def link_object(collection, obj):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def make_empty(collection, name, location=(0, 0, 0), parent=None, role=None):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.empty_display_type = "PLAIN_AXES"
    obj.location = location
    obj.parent = parent
    if role:
        obj["fx_role"] = role
    return obj


def make_mesh(collection, name, vertices, faces, material, location=(0, 0, 0), parent=None, role=None):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    obj.parent = parent
    obj.data.materials.append(material)
    if role:
        obj["fx_role"] = role
    return obj


def make_ellipse_disc(collection, name, center, radius_x, radius_y, thickness, sides, material, parent, role):
    vertices = []
    half = thickness * 0.5
    for z in (-half, half):
        for i in range(sides):
            angle = math.tau * i / sides
            vertices.append((math.cos(angle) * radius_x, math.sin(angle) * radius_y, z))

    faces = []
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple(range(sides, sides * 2)))
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((i, j, sides + j, sides + i))

    return make_mesh(
        collection,
        name,
        vertices,
        faces,
        material,
        center,
        parent,
        role,
    )


def make_lily_pad(collection, name, center, radius, rotation, material, parent, role="lily_pad"):
    sides = 16
    notch = math.radians(42)
    angles = [notch * 0.5 + (math.tau - notch) * i / (sides - 1) + rotation for i in range(sides)]
    half = 0.014
    vertices = [(0, 0, half)]
    vertices.extend((math.cos(a) * radius, math.sin(a) * radius, half) for a in angles)
    bottom_center = len(vertices)
    vertices.append((0, 0, -half))
    bottom_start = len(vertices)
    vertices.extend((math.cos(a) * radius, math.sin(a) * radius, -half) for a in angles)

    faces = []
    for i in range(sides - 1):
        faces.append((0, 1 + i, 2 + i))
        faces.append((bottom_center, bottom_start + i + 1, bottom_start + i))
        faces.append((1 + i, bottom_start + i, bottom_start + i + 1, 2 + i))
    faces.append((0, bottom_center, bottom_start, 1))
    faces.append((0, 1 + sides - 1, bottom_start + sides - 1, bottom_center))

    obj = make_mesh(collection, name, vertices, faces, material, center, parent, role)
    obj["lily_index"] = int(name.rsplit("_", 1)[-1]) if name.rsplit("_", 1)[-1].isdigit() else 0
    return obj


def create_cylinder_between(collection, name, start, end, radius, material, parent, role):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    length = direction.length
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=radius,
        depth=length * 1.06,
        location=(start + end) * 0.5,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(material)
    obj["fx_role"] = role
    link_object(collection, obj)
    obj.parent = parent
    return obj


def create_stream(collection, name, points, radii, material, root):
    group = make_empty(collection, name, parent=root, role="water_stream")
    group["segment_count"] = len(points) - 1
    for index in range(len(points) - 1):
        create_cylinder_between(
            collection,
            f"{name}_Segment_{index + 1:02d}",
            points[index],
            points[index + 1],
            radii[index],
            material,
            group,
            "water_stream_segment",
        )
    return group


def create_torus(collection, name, center, major_radius, minor_radius, material, parent, role):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=16,
        minor_segments=6,
        location=center,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    obj["fx_role"] = role
    link_object(collection, obj)
    obj.parent = parent
    return obj


def create_petal_layer(collection, name, center, count, inner_radius, outer_radius, width, lift, tip_z, material, root, role):
    layer = make_empty(collection, name, location=center, parent=root, role=role)
    vertices = []
    faces = []

    for index in range(count):
        angle = math.tau * index / count + (math.pi / count if count % 2 == 0 else 0)
        tangent = Vector((-math.sin(angle), math.cos(angle), 0))
        radial = Vector((math.cos(angle), math.sin(angle), 0))
        base = radial * inner_radius
        middle = radial * ((inner_radius + outer_radius) * 0.52)
        tip = radial * outer_radius + Vector((0, 0, tip_z))
        ridge = middle + Vector((0, 0, lift + 0.035))
        base_index = len(vertices)
        vertices.extend(
            [
                tuple(base - tangent * width * 0.34),
                tuple(base + tangent * width * 0.34),
                tuple(middle + tangent * width * 0.5 + Vector((0, 0, lift))),
                tuple(tip),
                tuple(middle - tangent * width * 0.5 + Vector((0, 0, lift))),
                tuple(ridge),
            ]
        )
        faces.extend(
            [
                (base_index, base_index + 1, base_index + 5),
                (base_index + 1, base_index + 2, base_index + 5),
                (base_index + 2, base_index + 3, base_index + 5),
                (base_index + 3, base_index + 4, base_index + 5),
                (base_index + 4, base_index, base_index + 5),
                (base_index + 4, base_index + 3, base_index + 2, base_index + 1, base_index),
            ]
        )

    mesh_obj = make_mesh(
        collection,
        f"{name}_Petals",
        vertices,
        faces,
        material,
        parent=layer,
        role=f"{role}_petals",
    )
    mesh_obj["petal_count"] = count
    return layer


def create_ico(collection, name, location, scale, material, parent, role, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    obj["fx_role"] = role
    link_object(collection, obj)
    obj.parent = parent
    return obj


def create_lotus(collection, materials, root):
    bud = make_empty(collection, "FX_Lotus_Bud", location=LOTUS_CENTER, parent=root, role="lotus_bud")
    create_ico(
        collection,
        "FX_Lotus_Bud_Petals",
        (0, 0, 0.19),
        (0.16, 0.16, 0.25),
        materials["pink_mid"],
        bud,
        "lotus_bud_petals",
        subdivisions=2,
    )
    create_ico(
        collection,
        "FX_Lotus_Bud_Tip",
        (0, 0, 0.36),
        (0.065, 0.065, 0.11),
        materials["pink_light"],
        bud,
        "lotus_bud_tip",
        subdivisions=1,
    )

    create_petal_layer(
        collection,
        "FX_Lotus_Bloom_Outer",
        LOTUS_CENTER + Vector((0, 0, 0.03)),
        10,
        0.055,
        0.38,
        0.15,
        0.045,
        0.015,
        materials["pink_light"],
        root,
        "lotus_outer",
    )
    create_petal_layer(
        collection,
        "FX_Lotus_Bloom_Middle",
        LOTUS_CENTER + Vector((0, 0, 0.07)),
        8,
        0.04,
        0.29,
        0.13,
        0.075,
        0.07,
        materials["pink_mid"],
        root,
        "lotus_middle",
    )
    create_petal_layer(
        collection,
        "FX_Lotus_Bloom_Inner",
        LOTUS_CENTER + Vector((0, 0, 0.11)),
        7,
        0.025,
        0.20,
        0.095,
        0.10,
        0.13,
        materials["pink_deep"],
        root,
        "lotus_inner",
    )

    center_group = make_empty(
        collection,
        "FX_Lotus_Bloom_Center",
        location=LOTUS_CENTER + Vector((0, 0, 0.18)),
        parent=root,
        role="lotus_center",
    )
    for index in range(9):
        angle = math.tau * index / 9
        radius = 0.075 if index else 0.0
        create_ico(
            collection,
            f"FX_Lotus_Bloom_Seed_{index + 1:02d}",
            (math.cos(angle) * radius, math.sin(angle) * radius, 0.025 + 0.025 * (index % 2)),
            (0.036, 0.036, 0.055),
            materials["lotus_gold"],
            center_group,
            "lotus_seed",
            subdivisions=1,
        )


def mark_default_hidden(collection, root):
    root["web_animated_component"] = True
    root["default_hidden"] = True
    for obj in collection.objects:
        obj["web_animated_component"] = True
        obj["default_hidden"] = True
        obj.hide_render = True
        obj.hide_set(True)
    collection.hide_render = True
    collection.hide_viewport = True


def main():
    remove_existing_collection()
    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)

    materials = {
        "water": make_material("FX Water Turquoise", (0.03, 0.64, 0.83), 0.82, 0.16, 0.05),
        "water_light": make_material("FX Water Highlight", (0.46, 0.94, 1.0), 0.88, 0.12, 0.02),
        "lily": make_material("FX Lily Leaf Green", (0.31, 0.58, 0.10), 1.0, 0.7),
        "lily_light": make_material("FX Lily Leaf Light", (0.48, 0.72, 0.16), 1.0, 0.7),
        "pink_light": make_material("FX Lotus Petal Light", (1.0, 0.60, 0.68), 1.0, 0.58),
        "pink_mid": make_material("FX Lotus Petal Mid", (0.96, 0.38, 0.52), 1.0, 0.58),
        "pink_deep": make_material("FX Lotus Petal Deep", (0.78, 0.18, 0.38), 1.0, 0.58),
        "lotus_gold": make_material("FX Lotus Golden Center", (1.0, 0.62, 0.06), 1.0, 0.52),
    }

    root = make_empty(collection, "FX_Fountain_Animation", role="fountain_root")

    create_stream(
        collection,
        "FX_Water_Stream_Upper",
        [
            (3.70, -4.06, 1.47),
            (3.77, -4.07, 1.39),
            (3.84, -4.09, 1.29),
            (3.91, -4.11, 1.18),
            (3.99, -4.13, 1.09),
            (4.06, -4.145, 1.035),
        ],
        [0.038, 0.041, 0.043, 0.041, 0.036],
        materials["water"],
        root,
    )
    create_stream(
        collection,
        "FX_Water_Stream_Lower",
        [
            (4.07, -4.13, 0.985),
            (4.085, -4.09, 0.87),
            (4.095, -4.04, 0.72),
            (4.10, -3.99, 0.55),
            (4.105, -3.94, 0.39),
            (4.105, -3.91, 0.285),
        ],
        [0.043, 0.048, 0.052, 0.049, 0.041],
        materials["water"],
        root,
    )

    water = make_ellipse_disc(
        collection,
        "FX_Pond_Water",
        POND_CENTER,
        0.86,
        0.57,
        0.025,
        28,
        materials["water"],
        root,
        "pond_water",
    )
    water["fill_origin"] = [POND_CENTER.x, POND_CENTER.y, POND_CENTER.z]

    create_torus(
        collection,
        "FX_Water_Ripple_Inner",
        (4.105, -3.91, 0.273),
        0.075,
        0.012,
        materials["water_light"],
        root,
        "water_ripple",
    )
    create_torus(
        collection,
        "FX_Water_Ripple_Outer",
        (4.105, -3.91, 0.275),
        0.15,
        0.009,
        materials["water_light"],
        root,
        "water_ripple",
    )

    pad_specs = [
        ((3.44, -3.54, 0.285), 0.15, 0.35),
        ((3.68, -3.86, 0.288), 0.18, 1.10),
        ((3.76, -3.34, 0.286), 0.125, 2.20),
        ((4.31, -3.43, 0.288), 0.17, 2.70),
        ((4.50, -3.76, 0.287), 0.13, 0.20),
        ((4.33, -3.98, 0.286), 0.115, 1.80),
        ((3.52, -4.06, 0.286), 0.11, 2.95),
    ]
    for index, (position, radius, rotation) in enumerate(pad_specs, start=1):
        make_lily_pad(
            collection,
            f"FX_LilyPad_{index:02d}",
            position,
            radius,
            rotation,
            materials["lily_light"] if index % 3 == 0 else materials["lily"],
            root,
        )

    make_lily_pad(
        collection,
        "FX_Lotus_Platform_00",
        (LOTUS_CENTER.x, LOTUS_CENTER.y, 0.292),
        0.255,
        -0.15,
        materials["lily"],
        root,
        role="lotus_platform",
    )
    create_lotus(collection, materials, root)

    mark_default_hidden(collection, root)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"Added hidden fountain animation components to: {BLEND_PATH}")
    print(f"Collection: {COLLECTION_NAME}; objects: {len(collection.objects)}")


if __name__ == "__main__":
    main()
