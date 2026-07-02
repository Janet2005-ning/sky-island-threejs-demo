import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"
GLB_PATH = ROOT / "public" / "models" / "sky_island_lowpoly.glb"
PREVIEW_PATH = ROOT / "public" / "assets" / "sky_island_blender_preview.png"
QIAO_BRIDGE_PATH = ROOT / "models" / "qiao.blend"
MAIN_DECOR_ARROW_ROTATION = math.radians(-25)


COLORS = {
    "grass": (0.83, 0.68, 0.18, 1),
    "grass_light": (0.95, 0.79, 0.28, 1),
    "cliff": (0.77, 0.35, 0.16, 1),
    "cliff_dark": (0.55, 0.23, 0.12, 1),
    "sand": (0.95, 0.66, 0.45, 1),
    "stone": (0.58, 0.48, 0.40, 1),
    "stone_light": (0.90, 0.69, 0.56, 1),
    "pot": (0.82, 0.31, 0.08, 1),
    "pot_dark": (0.52, 0.18, 0.06, 1),
    "wood": (0.84, 0.31, 0.07, 1),
    "wood_dark": (0.48, 0.17, 0.05, 1),
    "leaf": (0.46, 0.55, 0.13, 1),
    "leaf_dark": (0.29, 0.39, 0.10, 1),
    "stem": (0.60, 0.38, 0.20, 1),
    "cotton": (1.00, 0.84, 0.68, 1),
    "flower_white": (1.00, 0.94, 0.82, 1),
    "flower_blue": (0.08, 0.57, 0.85, 1),
    "flower_pink": (0.95, 0.45, 0.44, 1),
    "flower_yellow": (0.98, 0.78, 0.18, 1),
    "crystal": (0.10, 0.78, 0.90, 0.92),
}


def ensure_dirs():
    for path in [BLEND_PATH.parent, GLB_PATH.parent, PREVIEW_PATH.parent]:
        path.mkdir(parents=True, exist_ok=True)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        if block.users == 0:
            bpy.data.materials.remove(block)


def make_material(name, color, roughness=0.82, metallic=0.0, emission=None, alpha=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next(
        (node for node in mat.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"),
        None,
    )
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission[0]
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission[1]
        if alpha is not None and "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    if alpha is not None or color[3] < 1:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
    return mat


MATS = {}


def material(name):
    if not MATS:
        MATS.update(
            {
                "grass": make_material("Lowpoly grass ochre", COLORS["grass"]),
                "grass_light": make_material("Lowpoly sunlit grass", COLORS["grass_light"]),
                "cliff": make_material("Faceted terracotta cliff", COLORS["cliff"]),
                "cliff_dark": make_material("Deep orange cliff facets", COLORS["cliff_dark"]),
                "sand": make_material("Warm plaza sand", COLORS["sand"]),
                "stone": make_material("Warm gray stones", COLORS["stone"]),
                "stone_light": make_material("Peach light stones", COLORS["stone_light"]),
                "pot": make_material("Orange clay pottery", COLORS["pot"]),
                "pot_dark": make_material("Dark pottery rim", COLORS["pot_dark"]),
                "wood": make_material("Painted orange wood", COLORS["wood"]),
                "wood_dark": make_material("Dark plank seams", COLORS["wood_dark"]),
                "leaf": make_material("Olive leaf", COLORS["leaf"]),
                "leaf_dark": make_material("Dark olive leaf", COLORS["leaf_dark"]),
                "stem": make_material("Thin warm stems", COLORS["stem"]),
                "cotton": make_material("Soft cotton blossoms", COLORS["cotton"]),
                "flower_white": make_material("Cream flower petals", COLORS["flower_white"]),
                "flower_blue": make_material("Blue flower petals", COLORS["flower_blue"]),
                "flower_pink": make_material("Pink flower petals", COLORS["flower_pink"]),
                "flower_yellow": make_material("Yellow flower centers", COLORS["flower_yellow"]),
                "crystal": make_material(
                    "Glowing turquoise crystals",
                    COLORS["crystal"],
                    roughness=0.32,
                    emission=((0.02, 0.55, 0.65, 1), 0.45),
                    alpha=0.92,
                ),
            }
        )
    return MATS[name]


def flat(obj):
    if hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = False
    return obj


def link_object(obj, parent=None):
    if parent:
        obj.parent = parent
    return obj


def add_cone(name, radius1, radius2, depth, loc, mat_name, vertices=12, rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name} Mesh"
    obj.scale = scale
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def add_cylinder(name, radius, depth, loc, mat_name, vertices=12, rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name} Mesh"
    obj.scale = scale
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def add_box(name, loc, scale, mat_name, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def add_ico(name, loc, radius, mat_name, scale=(1, 1, 1), subdivisions=1, parent=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def add_torus(name, loc, major, minor, mat_name, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=16, minor_segments=6, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def cylinder_between(name, start, end, radius, mat_name, vertices=7, parent=None):
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    length = direction.length
    midpoint = start_v + direction * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def island_ring(rx, ry, count, seed):
    rng = random.Random(seed)
    ring = []
    for i in range(count):
        angle = (i / count) * math.tau
        wobble = 1 + rng.uniform(-0.10, 0.12)
        ring.append((math.cos(angle) * rx * wobble, math.sin(angle) * ry * wobble))
    return ring


def mesh_from_faces(name, vertices, faces, mat_name, loc=(0, 0, 0), parent=None):
    mesh = bpy.data.meshes.new(f"{name} Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(material(mat_name))
    flat(obj)
    return link_object(obj, parent)


def make_grass_cap(name, ring, loc, mat_name, parent=None):
    top_z = 0.12
    bottom_z = -0.18
    verts = [(0, 0, top_z)]
    verts.extend([(x, y, top_z) for x, y in ring])
    verts.extend([(x * 0.99, y * 0.99, bottom_z) for x, y in ring])
    faces = []
    count = len(ring)
    for i in range(count):
        nxt = 1 + ((i + 1) % count)
        faces.append([0, 1 + i, nxt])
        faces.append([1 + i, count + 1 + i, count + 1 + ((i + 1) % count), nxt])
    return mesh_from_faces(name, verts, faces, mat_name, loc, parent)


def make_cliff(name, ring, loc, height, seed, parent=None):
    rng = random.Random(seed + 100)
    top_z = -0.18
    bottom_z = -height
    verts = []
    count = len(ring)
    for x, y in ring:
        verts.append((x * 0.99, y * 0.99, top_z))
    for i, (x, y) in enumerate(ring):
        tuck = 0.61 + rng.uniform(-0.06, 0.06)
        verts.append((x * tuck, y * tuck, bottom_z + rng.uniform(-0.12, 0.05)))
    faces = []
    for i in range(count):
        faces.append([i, count + i, count + ((i + 1) % count), (i + 1) % count])
    obj = mesh_from_faces(name, verts, faces, "cliff", loc, parent)
    obj.data.materials.append(material("cliff_dark"))
    for i, poly in enumerate(obj.data.polygons):
        if i % 3 == 0:
            poly.material_index = 1
    return obj


def make_underside(name, ring, loc, height, seed, parent=None):
    rng = random.Random(seed + 200)
    top_z = -height
    tip_z = -height - 0.95
    verts = []
    count = len(ring)
    for x, y in ring:
        tuck = 0.58 + rng.uniform(-0.05, 0.05)
        verts.append((x * tuck, y * tuck, top_z + rng.uniform(-0.10, 0.03)))
    verts.append((0, 0, tip_z))
    tip_index = len(verts) - 1
    faces = [[i, (i + 1) % count, tip_index] for i in range(count)]
    obj = mesh_from_faces(name, verts, faces, "cliff_dark", loc, parent)
    obj.data.materials.append(material("cliff"))
    for i, poly in enumerate(obj.data.polygons):
        if i % 4 == 1:
            poly.material_index = 1
    return obj


def make_island(name, loc, rx, ry, height=1.25, seed=1, light=False):
    parent = bpy.data.objects.new(name, None)
    parent.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(parent)
    parent.location = loc
    ring = island_ring(rx, ry, 22, seed)
    make_grass_cap(f"{name} grass cap", ring, (0, 0, 0), "grass_light" if light else "grass", parent)
    make_cliff(f"{name} faceted cliff", ring, (0, 0, 0), height, seed, parent)
    make_underside(f"{name} pointed underside", ring, (0, 0, 0), height, seed, parent)
    return parent


def add_stone_ring(parent, center=(0, 0, 0), rx=1.1, ry=0.76, count=16):
    for i in range(count):
        angle = (i / count) * math.tau
        size = 0.16 + (i % 4) * 0.035
        add_ico(
            f"main plaza peach stone {i:02d}",
            (center[0] + math.cos(angle) * rx, center[1] + math.sin(angle) * ry, center[2]),
            size,
            "stone_light" if i % 3 else "stone",
            scale=(1.25, 0.85, 0.55),
            parent=parent,
        )


def add_plaza(parent):
    add_cylinder(
        "flat warm stone plaza",
        1.0,
        0.08,
        (-0.25, 0.05, 0.18),
        "sand",
        vertices=18,
        scale=(1.15, 0.78, 1),
        parent=parent,
    )
    add_stone_ring(parent, (-0.25, 0.05, 0.27), 1.22, 0.86, 17)


def add_pot(parent, loc, scale=1.0, rot_z=0.0, name="clay pot", tilt=(0, 0), handle=True):
    pot = bpy.data.objects.new(name, None)
    pot.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(pot)
    pot.parent = parent
    pot.location = loc
    pot.rotation_euler = (tilt[0], tilt[1], rot_z)
    pot.scale = (scale, scale, scale)
    add_ico(f"{name} round lowpoly belly", (0, 0, 0.24), 0.36, "pot", scale=(1.0, 0.94, 0.78), subdivisions=2, parent=pot)
    add_cone(f"{name} small dark foot", 0.17, 0.22, 0.08, (0, 0, 0.02), "pot_dark", vertices=12, parent=pot)
    add_cone(f"{name} short open neck", 0.20, 0.30, 0.18, (0, 0, 0.48), "pot", vertices=12, parent=pot)
    add_torus(f"{name} raised open rim", (0, 0, 0.58), 0.27, 0.045, "pot", parent=pot)
    add_cylinder(f"{name} visible dark opening", 0.18, 0.04, (0, 0, 0.565), "pot_dark", vertices=12, parent=pot)
    if handle:
        add_torus(f"{name} side handle", (-0.30, 0, 0.34), 0.14, 0.026, "pot_dark", rot=(math.pi / 2, 0, 0), parent=pot)
    add_box(f"{name} lowpoly highlight", (0.06, -0.2, 0.24), (0.035, 0.025, 0.16), "pot_dark", rot=(0, 0, -0.4), parent=pot)
    crack_lines = [
        ((-0.16, -0.31, 0.20), (-0.04, -0.34, 0.30)),
        ((-0.04, -0.34, 0.30), (0.10, -0.30, 0.23)),
        ((0.12, -0.29, 0.15), (0.22, -0.27, 0.22)),
    ]
    for i, (start, end) in enumerate(crack_lines):
        cylinder_between(f"{name} carved crack {i:02d}", start, end, 0.008, "pot_dark", vertices=5, parent=pot)
    return pot


def tilt_towards(loc, target=(0.0, 0.0), amount=0.42):
    direction = Vector((target[0] - loc[0], target[1] - loc[1], 0.0))
    if direction.length == 0:
        return (0, 0)
    direction.normalize()
    return (-direction.y * amount, direction.x * amount)


def add_flower(parent, loc, scale=1.0, petal_mat="flower_white", name="flower"):
    plant = bpy.data.objects.new(name, None)
    plant.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(plant)
    plant.parent = parent
    plant.location = loc
    plant.scale = (scale, scale, scale)
    for i in range(7):
        angle = (i / 7) * math.tau
        add_cone(
            f"{name} leaf {i:02d}",
            0.035,
            0.0,
            0.24,
            (math.cos(angle) * 0.09, math.sin(angle) * 0.09, 0.08),
            "leaf" if i % 2 else "leaf_dark",
            vertices=6,
            rot=(1.1, 0.15, angle),
            parent=plant,
        )
    cylinder_between(f"{name} tiny stem", (0, 0, 0.08), (0, 0, 0.28), 0.014, "stem", parent=plant)
    for i in range(6):
        angle = (i / 6) * math.tau
        add_ico(
            f"{name} petal {i:02d}",
            (math.cos(angle) * 0.095, math.sin(angle) * 0.095, 0.32),
            0.045,
            petal_mat,
            scale=(1.05, 0.72, 0.55),
            parent=plant,
        )
    add_ico(f"{name} yellow middle", (0, 0, 0.32), 0.042, "flower_yellow", parent=plant)
    return plant


def add_cotton_tree(parent, loc, scale=1.0, name="cotton tree"):
    tree = bpy.data.objects.new(name, None)
    tree.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(tree)
    tree.parent = parent
    tree.location = loc
    tree.scale = (scale, scale, scale)
    cylinder_between(f"{name} trunk", (0, 0, 0), (0, 0, 0.98), 0.035, "stem", parent=tree)
    for i in range(7):
        height = 0.25 + i * 0.105
        side = -1 if i % 2 else 1
        start = (0, 0, height)
        end = (side * (0.18 + i * 0.01), 0.02 * math.sin(i), height + 0.09)
        cylinder_between(f"{name} twig {i:02d}", start, end, 0.018, "stem", parent=tree)
        add_ico(
            f"{name} cotton blossom {i:02d}",
            (end[0] + side * 0.08, end[1], end[2] + 0.035),
            0.09,
            "cotton",
            scale=(1.0, 0.82, 1.2),
            parent=tree,
        )
    return tree


def add_leaf_clump(parent, loc, scale=1.0, name="leaf clump"):
    clump = bpy.data.objects.new(name, None)
    clump.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(clump)
    clump.parent = parent
    clump.location = loc
    clump.scale = (scale, scale, scale)
    for i in range(10):
        angle = (i / 10) * math.tau
        radius = 0.07 + (i % 3) * 0.025
        add_cone(
            f"{name} pointed leaf {i:02d}",
            0.045,
            0.0,
            0.28,
            (math.cos(angle) * radius, math.sin(angle) * radius, 0.11),
            "leaf" if i % 2 else "leaf_dark",
            vertices=6,
            rot=(1.16, 0.22, angle),
            scale=(0.9, 1.0, 1.0),
            parent=clump,
        )
    return clump


def add_bridge_planks(parent, start, end, count, width, name):
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    angle = math.atan2(direction.y, direction.x)
    for i in range(count):
        t = i / max(1, count - 1)
        pos = start_v.lerp(end_v, t)
        pos.z += math.sin(t * math.pi) * 0.08
        add_box(
            f"{name} plank {i:02d}",
            pos,
            (0.12, width, 0.045),
            "wood" if i % 2 else "wood_dark",
            rot=(0, 0, angle),
            parent=parent,
        )


def add_u_bridge(parent, center, scale=1.0, rot_z=0.0, name="horseshoe bridge"):
    bridge = bpy.data.objects.new(name, None)
    bridge.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(bridge)
    bridge.parent = parent
    bridge.location = center
    bridge.rotation_euler[2] = rot_z
    bridge.scale = (scale, scale, scale)
    for i in range(20):
        angle = -math.pi * 0.82 + (i / 19) * math.pi * 1.64
        x = math.cos(angle) * 0.62
        y = math.sin(angle) * 0.45
        plank_rot = angle + math.pi / 2
        add_box(
            f"{name} curved plank {i:02d}",
            (x, y, 0.08 + math.sin(i * 0.7) * 0.01),
            (0.095, 0.24, 0.05),
            "wood",
            rot=(0, 0, plank_rot),
            parent=bridge,
        )
        if i % 3 == 0:
            add_box(
                f"{name} metal peg {i:02d}",
                (x, y, 0.145),
                (0.018, 0.018, 0.012),
                "wood_dark",
                rot=(0, 0, plank_rot),
                parent=bridge,
            )
    return bridge


def add_crystal(parent, loc, scale=1.0, name="turquoise crystal"):
    crystal = add_ico(
        name,
        loc,
        0.24,
        "crystal",
        scale=(0.64 * scale, 0.64 * scale, 1.65 * scale),
        subdivisions=1,
        parent=parent,
    )
    crystal.rotation_euler = (0.2, 0.0, 0.4)
    return crystal


def append_qiao_bridge(parent):
    if not QIAO_BRIDGE_PATH.exists():
        print(f"Skipped qiao bridge: missing {QIAO_BRIDGE_PATH}")
        return None

    with bpy.data.libraries.load(str(QIAO_BRIDGE_PATH), link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)

    imported = [obj for obj in data_to.objects if obj and obj.type == "MESH"]
    bridge_objects = []
    for obj in imported:
        has_material = bool(getattr(obj.data, "materials", None) and len(obj.data.materials))
        if not has_material:
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        bpy.context.collection.objects.link(obj)
        bridge_objects.append(obj)

    if not bridge_objects:
        print(f"Skipped qiao bridge: no materialized mesh objects in {QIAO_BRIDGE_PATH}")
        return None

    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    for obj in bridge_objects:
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ Vector(corner)
            min_v.x = min(min_v.x, world_corner.x)
            min_v.y = min(min_v.y, world_corner.y)
            min_v.z = min(min_v.z, world_corner.z)
            max_v.x = max(max_v.x, world_corner.x)
            max_v.y = max(max_v.y, world_corner.y)
            max_v.z = max(max_v.z, world_corner.z)

    center = (min_v + max_v) * 0.5
    bridge = bpy.data.objects.new("Qiao imported block bridge between left island and main island", None)
    bridge.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(bridge)
    bridge.parent = parent
    bridge.location = (-3.88, 0.70, 0.072)
    bridge.rotation_euler[2] = math.atan2(-1.15, 6.40) - math.pi / 2
    bridge.scale = (0.095, 0.095, 0.095)

    for obj in bridge_objects:
        obj.name = f"qiao bridge {obj.name}"
        obj.location = obj.location - center
        obj.parent = bridge
        flat(obj)

    return bridge


def populate_main(main):
    decor = bpy.data.objects.new("Main island decorations rotated 180 degrees", None)
    decor.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(decor)
    decor.parent = main
    decor.rotation_euler[2] = math.pi + MAIN_DECOR_ARROW_ROTATION

    add_plaza(decor)

    for i, (x, y, z, r) in enumerate(
        [
            (-0.82, -0.54, 0.35, 0.28),
            (-0.52, -0.72, 0.35, 0.30),
            (-0.20, -0.70, 0.34, 0.27),
            (0.12, -0.54, 0.34, 0.28),
            (-0.56, -0.42, 0.56, 0.27),
            (-0.25, -0.48, 0.58, 0.30),
            (0.06, -0.37, 0.52, 0.25),
            (-0.36, -0.48, 0.80, 0.31),
        ]
    ):
        add_ico(f"stacked gray shrine rock {i:02d}", (x, y, z), r, "stone", scale=(1.15, 0.9, 0.7), parent=decor)

    add_pot(
        decor,
        (-0.38, -0.52, 1.02),
        0.86,
        -0.12,
        "upper handled open clay pot",
        tilt=tilt_towards((-0.38, -0.52, 1.02), amount=0.42),
        handle=True,
    )
    add_pot(
        decor,
        (0.44, -0.40, 0.56),
        0.70,
        0.55,
        "lower open clay pot",
        tilt=tilt_towards((0.44, -0.40, 0.56), amount=0.42),
        handle=False,
    )


def populate_secondary(parent, specs, prefix):
    for i, (x, y, petal, scale) in enumerate(specs):
        add_flower(parent, (x, y, 0.18), scale, petal, f"{prefix} flower {i:02d}")


def build_model():
    world = bpy.data.objects.new("Sky Island Game Model", None)
    world.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(world)

    main = make_island("Main playable floating island", (0, 0, 0), 2.85, 1.92, 1.42, seed=8, light=False)
    main.parent = world
    populate_main(main)

    lower_step = make_island(
        "Right lower stair terrace",
        (2.42, -0.02, 0.12),
        1.18,
        0.82,
        0.95,
        seed=18,
        light=True,
    )
    lower_step.parent = world

    middle_step = make_island(
        "Right middle stair terrace",
        (3.58, -0.12, 0.38),
        1.34,
        0.94,
        1.05,
        seed=24,
        light=True,
    )
    middle_step.parent = world

    high_step = make_island(
        "Right high stair terrace",
        (5.08, -0.28, 0.68),
        1.78,
        1.18,
        1.18,
        seed=28,
        light=True,
    )
    high_step.parent = world

    left = make_island("Separate clean small island", (-6.40, 1.15, 0.0), 1.45, 1.08, 1.00, seed=38, light=True)
    left.parent = world

    append_qiao_bridge(world)

    bpy.context.scene.world = bpy.data.worlds.new("Pastel sky world")
    bpy.context.scene.world.color = (0.62, 0.86, 0.89)
    bpy.ops.object.light_add(type="SUN", location=(-3.2, -4.4, 7.5))
    sun = bpy.context.object
    sun.name = "Warm game sun"
    sun.data.energy = 1.75
    sun.data.angle = math.radians(6)
    bpy.ops.object.light_add(type="AREA", location=(2.4, 3.4, 4.2))
    area = bpy.context.object
    area.name = "Soft blue fill light"
    area.data.energy = 170
    area.data.size = 5

    bpy.ops.object.camera_add(location=(7.4, -7.0, 4.6), rotation=(math.radians(61), 0, math.radians(44)))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.name = "Preview camera"
    camera.data.lens = 35
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = 8.5
    camera.data.dof.aperture_fstop = 8

    return world


def render_preview():
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.context.scene.eevee.taa_render_samples = 64
    if hasattr(bpy.context.scene.eevee, "use_gtao"):
        bpy.context.scene.eevee.use_gtao = True
    if hasattr(bpy.context.scene.eevee, "gtao_distance"):
        bpy.context.scene.eevee.gtao_distance = 3
    if hasattr(bpy.context.scene.eevee, "gtao_factor"):
        bpy.context.scene.eevee.gtao_factor = 1.35
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 900
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -0.15
    bpy.context.scene.view_settings.gamma = 1
    bpy.context.scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)


def save_outputs():
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )


def main():
    ensure_dirs()
    clear_scene()
    build_model()
    save_outputs()
    render_preview()
    print(f"Saved Blender file: {BLEND_PATH}")
    print(f"Saved web GLB: {GLB_PATH}")
    print(f"Saved preview: {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
