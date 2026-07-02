import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"
TEXTURE_DIR = ROOT / "textures" / "animal_characters"

COLLECTION_NAME = "Seated cartoon animals"
OBJECT_PREFIX = "ANIMAL_"
MATERIAL_PREFIX = "Animal material"

FIRE_CENTER = Vector((-1.62, -4.05, 0.0))
SEATS = (
    ("bear", "log bench imported 01", -0.215),
    ("cat", "log bench imported 01", 0.215),
    ("duck", "log bench imported 02", -0.215),
    ("frog", "log bench imported 02", 0.215),
)


def remove_previous():
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is not None:
        for obj in list(collection.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
    for obj in list(bpy.data.objects):
        if obj.name.startswith(OBJECT_PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
    for material in list(bpy.data.materials):
        if material.name.startswith(MATERIAL_PREFIX):
            bpy.data.materials.remove(material, do_unlink=True)


def solid_material(name, color, roughness=0.76, metallic=0.0):
    material = bpy.data.materials.new(f"{MATERIAL_PREFIX} {name}")
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.22
    return material


def face_material(name, image_path):
    material = bpy.data.materials.new(f"{MATERIAL_PREFIX} {name} face texture")
    material.diffuse_color = (1, 1, 1, 1)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texture = nodes.new("ShaderNodeTexImage")
    image = bpy.data.images.load(str(image_path), check_existing=True)
    image.pack()
    texture.image = image
    texture.interpolation = "Linear"
    bsdf.inputs["Roughness"].default_value = 0.72
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.18
    links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(texture.outputs["Alpha"], bsdf.inputs["Alpha"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    elif hasattr(material, "blend_method"):
        material.blend_method = "BLEND"
    if hasattr(material, "use_transparency_overlap"):
        material.use_transparency_overlap = False
    material.use_backface_culling = False
    return material


def assign_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def smooth_mesh(obj):
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def add_ico(collection, parent, name, location, scale, material, subdivisions=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0)
    obj = bpy.context.object
    obj.name = f"{OBJECT_PREFIX}{name}"
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.scale = scale
    assign_material(obj, material)
    smooth_mesh(obj)
    return obj


def add_cylinder_between(collection, parent, name, start, end, radius, material, vertices=10):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length)
    obj = bpy.context.object
    obj.name = f"{OBJECT_PREFIX}{name}"
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = (start + end) * 0.5
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    assign_material(obj, material)
    smooth_mesh(obj)
    return obj


def add_box(collection, parent, name, location, scale, rotation, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.object
    obj.name = f"{OBJECT_PREFIX}{name}"
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.scale = scale
    obj.rotation_euler = rotation
    assign_material(obj, material)
    if bevel > 0:
        modifier = obj.modifiers.new("Soft low-poly edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def add_cone(collection, parent, name, location, depth, radius1, radius2, material):
    bpy.ops.mesh.primitive_cone_add(
        vertices=14,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
    )
    obj = bpy.context.object
    obj.name = f"{OBJECT_PREFIX}{name}"
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    assign_material(obj, material)
    smooth_mesh(obj)
    return obj


def add_face_plane(collection, parent, name, center_z, width, height, front_y, material):
    half_width = width * 0.5
    half_height = height * 0.5
    vertices = [
        (-half_width, front_y, center_z - half_height),
        (half_width, front_y, center_z - half_height),
        (half_width, front_y, center_z + half_height),
        (-half_width, front_y, center_z + half_height),
    ]
    mesh = bpy.data.meshes.new(f"{OBJECT_PREFIX}{name}_MESH")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.polygons[0].loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv_layer.data[loop].uv = uv
    obj = bpy.data.objects.new(f"{OBJECT_PREFIX}{name}", mesh)
    collection.objects.link(obj)
    obj.parent = parent
    assign_material(obj, material)
    return obj


def add_root(collection, character, bench, offset):
    root = bpy.data.objects.new(f"{OBJECT_PREFIX}{character.upper()}_ROOT", None)
    collection.objects.link(root)
    angle = bench.rotation_euler.z
    root.location = (
        bench.location.x + math.cos(angle) * offset,
        bench.location.y + math.sin(angle) * offset,
        bench.location.z + bench.dimensions.z + 0.006,
    )
    toward_fire = FIRE_CENTER - root.location
    root.rotation_euler.z = math.atan2(toward_fire.x, -toward_fire.y)
    root["character_id"] = character
    root["seat_bench"] = bench.name
    root["seat_offset"] = offset
    root["pose"] = "seated_facing_campfire"
    return root


def seated_legs(collection, root, prefix, body_material, foot_material=None, spread=0.052):
    foot_material = foot_material or body_material
    for side, x in (("L", -spread), ("R", spread)):
        add_cylinder_between(
            collection,
            root,
            f"{prefix}_{side}_THIGH",
            (x, -0.005, 0.075),
            (x * 1.12, -0.072, 0.022),
            0.027,
            body_material,
        )
        add_ico(
            collection,
            root,
            f"{prefix}_{side}_FOOT",
            (x * 1.15, -0.105, 0.005),
            (0.038, 0.057, 0.026),
            foot_material,
            2,
        )


def build_bear(collection, root, materials):
    fur = materials["bear_fur"]
    add_ico(collection, root, "BEAR_BODY", (0, 0.005, 0.145), (0.088, 0.064, 0.115), fur)
    add_ico(collection, root, "BEAR_HEAD_BACK", (0, 0.006, 0.345), (0.105, 0.058, 0.09), fur)
    add_face_plane(collection, root, "BEAR_FACE_TEXTURE", 0.35, 0.255, 0.255, -0.071, materials["bear_face"])
    seated_legs(collection, root, "BEAR", fur, materials["bear_paw"])

    add_cylinder_between(collection, root, "BEAR_ARM_PENCIL", (-0.064, -0.002, 0.205), (-0.125, -0.058, 0.16), 0.027, fur)
    add_ico(collection, root, "BEAR_PAW_PENCIL", (-0.13, -0.064, 0.157), (0.032, 0.027, 0.031), materials["bear_paw"])
    add_cylinder_between(collection, root, "BEAR_ARM_RELAXED", (0.064, 0.0, 0.205), (0.105, -0.035, 0.13), 0.027, fur)
    add_ico(collection, root, "BEAR_PAW_RELAXED", (0.108, -0.04, 0.125), (0.031, 0.027, 0.03), materials["bear_paw"])

    pencil_start = Vector((-0.145, -0.086, 0.12))
    pencil_end = Vector((-0.122, -0.086, 0.255))
    add_cylinder_between(collection, root, "BEAR_PENCIL_YELLOW", pencil_start, pencil_end, 0.012, materials["pencil_yellow"], 8)
    direction = (pencil_end - pencil_start).normalized()
    add_cylinder_between(collection, root, "BEAR_PENCIL_ERASER", pencil_start - direction * 0.021, pencil_start, 0.0125, materials["pencil_pink"], 8)
    add_cone(collection, root, "BEAR_PENCIL_TIP", pencil_end + direction * 0.013, 0.026, 0.012, 0.002, materials["pencil_wood"])


def build_cat(collection, root, materials):
    white = materials["cat_white"]
    add_ico(collection, root, "CAT_BODY", (0, 0.004, 0.15), (0.083, 0.059, 0.105), white)
    add_cone(collection, root, "CAT_PURPLE_DRESS", (0, -0.013, 0.145), 0.18, 0.103, 0.069, materials["cat_dress"])
    add_ico(collection, root, "CAT_HEAD_BACK", (0, 0.006, 0.35), (0.108, 0.058, 0.092), white)
    add_face_plane(collection, root, "CAT_FACE_TEXTURE", 0.355, 0.265, 0.265, -0.071, materials["cat_face"])
    seated_legs(collection, root, "CAT", white, white)

    add_cylinder_between(collection, root, "CAT_ARM_DOWN", (-0.064, -0.008, 0.22), (-0.118, -0.055, 0.145), 0.025, white)
    add_ico(collection, root, "CAT_PAW_DOWN", (-0.122, -0.061, 0.137), (0.029, 0.026, 0.029), white)
    add_cylinder_between(collection, root, "CAT_ARM_WAVE", (0.064, -0.004, 0.22), (0.118, -0.048, 0.31), 0.025, white)
    add_ico(collection, root, "CAT_PAW_WAVE", (0.122, -0.053, 0.326), (0.032, 0.026, 0.036), white)
    for index, z in enumerate((0.125, 0.178), start=1):
        add_ico(collection, root, f"CAT_DRESS_BUTTON_{index}", (0, -0.083, z), (0.015, 0.008, 0.015), materials["cat_button"], 1)
    add_box(collection, root, "CAT_DRESS_HEM", (0, -0.012, 0.058), (0.104, 0.061, 0.006), (0, 0, 0), materials["cat_trim"], 0.004)


def build_duck(collection, root, materials):
    yellow = materials["duck_yellow"]
    orange = materials["duck_orange"]
    add_ico(collection, root, "DUCK_BODY", (0, 0.008, 0.17), (0.105, 0.073, 0.142), yellow)
    add_ico(collection, root, "DUCK_HEAD_BACK", (0, 0.003, 0.34), (0.1, 0.06, 0.105), yellow)
    add_face_plane(collection, root, "DUCK_FACE_TEXTURE", 0.345, 0.245, 0.245, -0.073, materials["duck_face"])
    add_ico(collection, root, "DUCK_WING_L", (-0.105, 0.0, 0.18), (0.035, 0.045, 0.08), yellow)
    add_ico(collection, root, "DUCK_WING_R", (0.105, 0.0, 0.18), (0.035, 0.045, 0.08), yellow)
    seated_legs(collection, root, "DUCK", yellow, orange, 0.05)


def build_frog(collection, root, materials):
    green = materials["frog_green"]
    add_ico(collection, root, "FROG_BODY", (0, 0.005, 0.145), (0.097, 0.067, 0.105), green)
    add_ico(collection, root, "FROG_HEAD_BACK", (0, 0.005, 0.345), (0.112, 0.06, 0.092), green)
    add_face_plane(collection, root, "FROG_FACE_TEXTURE", 0.35, 0.27, 0.25, -0.073, materials["frog_face"])
    seated_legs(collection, root, "FROG", green, green, 0.058)

    add_box(collection, root, "FROG_BOOK_COVER", (-0.035, -0.112, 0.16), (0.075, 0.014, 0.092), (math.radians(-6), 0, math.radians(-8)), materials["book_red"], 0.009)
    add_box(collection, root, "FROG_BOOK_PAGES", (-0.046, -0.129, 0.238), (0.06, 0.009, 0.008), (math.radians(-6), 0, math.radians(-8)), materials["book_pages"], 0.004)
    add_cylinder_between(collection, root, "FROG_ARM_BOOK_L", (-0.068, -0.002, 0.205), (-0.105, -0.122, 0.178), 0.027, green)
    add_cylinder_between(collection, root, "FROG_ARM_BOOK_R", (0.068, -0.002, 0.205), (0.035, -0.124, 0.155), 0.027, green)
    add_ico(collection, root, "FROG_HAND_BOOK_L", (-0.105, -0.126, 0.177), (0.03, 0.025, 0.03), green)
    add_ico(collection, root, "FROG_HAND_BOOK_R", (0.035, -0.128, 0.154), (0.03, 0.025, 0.03), green)


def main():
    if bpy.data.filepath and Path(bpy.data.filepath).resolve() != BLEND_PATH.resolve():
        print(f"Warning: editing {bpy.data.filepath}; target is {BLEND_PATH}")
    remove_previous()

    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)

    materials = {
        "bear_fur": solid_material("bear warm beige fur", (0.68, 0.62, 0.56, 1)),
        "bear_paw": solid_material("bear cream paws", (0.82, 0.77, 0.71, 1)),
        "cat_white": solid_material("cat ivory white", (0.93, 0.91, 0.89, 1)),
        "cat_dress": solid_material("cat lavender dress", (0.62, 0.52, 0.68, 1)),
        "cat_button": solid_material("cat pink buttons", (1.0, 0.55, 0.66, 1)),
        "cat_trim": solid_material("cat cream dress trim", (0.94, 0.89, 0.67, 1)),
        "duck_yellow": solid_material("duck sunshine yellow", (1.0, 0.82, 0.02, 1)),
        "duck_orange": solid_material("duck orange feet", (1.0, 0.45, 0.08, 1)),
        "frog_green": solid_material("frog mint green", (0.46, 0.82, 0.48, 1)),
        "pencil_yellow": solid_material("pencil yellow", (1.0, 0.69, 0.03, 1)),
        "pencil_pink": solid_material("pencil pink eraser", (1.0, 0.28, 0.34, 1)),
        "pencil_wood": solid_material("pencil wood tip", (0.72, 0.46, 0.22, 1)),
        "book_red": solid_material("frog red book cover", (0.88, 0.05, 0.06, 1)),
        "book_pages": solid_material("frog book pages", (0.95, 0.9, 0.72, 1)),
        "bear_face": face_material("bear", TEXTURE_DIR / "bear_face.png"),
        "cat_face": face_material("cat", TEXTURE_DIR / "cat_face.png"),
        "duck_face": face_material("duck", TEXTURE_DIR / "duck_face.png"),
        "frog_face": face_material("frog", TEXTURE_DIR / "frog_face.png"),
    }

    builders = {
        "bear": build_bear,
        "cat": build_cat,
        "duck": build_duck,
        "frog": build_frog,
    }
    roots = []
    for character, bench_name, offset in SEATS:
        bench = bpy.data.objects.get(bench_name)
        if bench is None:
            raise RuntimeError(f"Missing seat bench: {bench_name}")
        root = add_root(collection, character, bench, offset)
        builders[character](collection, root, materials)
        roots.append(root)

    bpy.context.scene["seated_cartoon_animal_count"] = len(roots)
    bpy.context.scene["seated_cartoon_animal_ids"] = ",".join(root["character_id"] for root in roots)
    bpy.context.scene["seated_cartoon_animal_texture_source"] = str(TEXTURE_DIR / "animal_face_atlas_key.png")
    bpy.context.scene["seated_cartoon_animal_layout"] = "two_on_bench_01_two_on_bench_02"
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    print(f"Saved {len(roots)} seated cartoon animals into: {BLEND_PATH}")
    for root in roots:
        print(
            f"{root.name}: location={tuple(round(value, 4) for value in root.location)}, "
            f"rotation_z={round(math.degrees(root.rotation_euler.z), 2)}, "
            f"bench={root['seat_bench']}, offset={root['seat_offset']}"
        )


if __name__ == "__main__":
    main()
