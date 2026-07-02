import colorsys
import glob
import math
import os

import bpy
from mathutils import Matrix, Vector


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_CANDIDATES = glob.glob(
    os.path.join(os.path.dirname(PROJECT_DIR), "I216-*", "I216-*_BLEND.blend")
)
if len(SOURCE_CANDIDATES) != 1:
    raise RuntimeError(f"Expected one I216 garden blend, found: {SOURCE_CANDIDATES}")

SOURCE_BLEND = SOURCE_CANDIDATES[0]
TARGET_BLEND = os.path.join(PROJECT_DIR, "models", "sky_island_lowpoly.blend")

COLLECTION_NAME = "Imported bright garden plants"
LEGACY_COLLECTION_NAME = "Imported sparse garden plants"
OBJECT_PREFIX = "garden decoration imported"
LEGACY_OBJECT_PREFIX = "garden plant imported"
BRIGHT_MATERIAL_NAME = "Garden bright cartoon palette"
BRIGHT_IMAGE_NAME = "GardenPaletteBright"
FLAT_MATERIAL_PREFIX = "Garden flat bright"

# Each asset may be one source mesh or a tree assembled from several source
# roots. Grouping the source parts is essential: the tree pack stores trunks
# and crowns as separate objects under one global root.
ASSET_GROUPS = {
    "flower_white": ["White-Poppy"],
    "flower_purple": ["Purple-Poppy"],
    "flower_daisy_bush": ["Daizy-Bush"],
    "flower_red_bush": ["Red-Fw-Bush"],
    "flower_purple_bush": ["Darknight-Bush"],
    "tree_green_branch": ["Cylinder.007", "Sphere.013", "Sphere.014", "Sphere.015"],
    "tree_coral_crown": ["Cylinder.020", "Sphere.035", "Sphere.036", "Sphere.037"],
    "tree_slender_green": ["Cylinder.025", "Sphere.059", "Sphere.060", "Sphere.061"],
}

# Tree heights exceed the approximately 1.54-unit central rock-and-pot group.
# Flowers are about half the width/visual mass of one 0.55-0.65-unit shrine rock.
PLACEMENTS = [
    {
        "asset": "tree_coral_crown",
        "kind": "tree",
        "surface": "Main playable floating island grass cap",
        "location": (1.85, -4.85),
        "height": 1.95,
        "rotation": 24.0,
    },
    {
        "asset": "tree_green_branch",
        "kind": "tree",
        "surface": "Separate clean small island grass cap",
        "location": (10.2, -4.25),
        "height": 1.85,
        "rotation": -28.0,
    },
    {
        "asset": "tree_slender_green",
        "kind": "tree",
        "surface": "Right high stair terrace grass cap",
        "location": (-2.7, -4.65),
        "height": 1.75,
        "rotation": 16.0,
    },
    {
        "asset": "flower_daisy_bush",
        "kind": "flower",
        "surface": "Main playable floating island grass cap",
        "location": (2.4, -2.75),
        "height": 0.34,
        "rotation": 14.0,
    },
    {
        "asset": "flower_purple",
        "kind": "flower",
        "surface": "Main playable floating island grass cap",
        "location": (5.25, -2.95),
        "height": 0.36,
        "rotation": -22.0,
    },
    {
        "asset": "flower_white",
        "kind": "flower",
        "surface": "Main playable floating island grass cap",
        "location": (5.15, -5.1),
        "height": 0.36,
        "rotation": 38.0,
    },
    {
        "asset": "flower_red_bush",
        "kind": "flower",
        "surface": "Right lower stair terrace grass cap",
        "location": (1.25, -3.55),
        "height": 0.32,
        "rotation": -12.0,
    },
    {
        "asset": "flower_white",
        "kind": "flower",
        "surface": "Right middle stair terrace grass cap",
        "location": (-0.45, -4.65),
        "height": 0.36,
        "rotation": 26.0,
    },
    {
        "asset": "flower_daisy_bush",
        "kind": "flower",
        "surface": "Right high stair terrace grass cap",
        "location": (-1.0, -3.45),
        "height": 0.33,
        "rotation": 7.0,
    },
    {
        "asset": "flower_purple",
        "kind": "flower",
        "surface": "Separate clean small island grass cap",
        "location": (9.6, -3.55),
        "height": 0.36,
        "rotation": -31.0,
    },
    {
        "asset": "flower_purple_bush",
        "kind": "flower",
        "surface": "Separate clean small island grass cap",
        "location": (10.65, -4.75),
        "height": 0.32,
        "rotation": 33.0,
    },
]


def child_object_name(root_name):
    return f"{root_name}_Color-palette_0"


def mesh_bounds(meshes):
    points = [vertex.co for mesh in meshes for vertex in mesh.vertices]
    minimum = Vector(
        (
            min(point.x for point in points),
            min(point.y for point in points),
            min(point.z for point in points),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in points),
            max(point.y for point in points),
            max(point.z for point in points),
        )
    )
    return minimum, maximum


def world_top(object_name):
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise RuntimeError(f"Missing placement surface: {object_name}")
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def brighten_palette_pixel(red, green, blue, alpha):
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)

    if value < 0.08:
        return (0.24, 0.13, 0.06, alpha)

    if saturation < 0.12:
        if value > 0.58:
            return (0.94, 0.89, 0.76, alpha)
        warm_value = min(0.72, max(0.48, 0.42 + value * 0.30))
        return (warm_value, warm_value * 0.92, warm_value * 0.80, alpha)

    if 0.04 <= hue <= 0.14 and value < 0.72:
        # Tree trunks and flower-bed rims become warm honey brown.
        return (*colorsys.hsv_to_rgb(0.075, 0.62, min(0.52, 0.36 + value * 0.18)), alpha)

    if 0.14 < hue < 0.48:
        # Deep source greens are shifted toward the island's yellow-green cap.
        return (*colorsys.hsv_to_rgb(0.27, 0.72, min(0.56, 0.46 + value * 0.10)), alpha)

    if 0.66 <= hue <= 0.92:
        # Purple flowers stay distinct but become readable pastel violet.
        return (*colorsys.hsv_to_rgb(0.78, 0.70, min(0.76, 0.64 + value * 0.13)), alpha)

    if hue <= 0.14 or hue >= 0.94:
        # Red and pink crowns become the same warm coral family as the islands.
        return (*colorsys.hsv_to_rgb(0.035, 0.70, min(0.78, 0.66 + value * 0.13)), alpha)

    return (
        min(0.86, red * 0.78 + 0.18),
        min(0.86, green * 0.78 + 0.18),
        min(0.84, blue * 0.78 + 0.16),
        alpha,
    )


def source_palette(source_material):
    image_node = next(
        node
        for node in source_material.node_tree.nodes
        if node.type == "TEX_IMAGE" and node.image is not None
    )
    image = image_node.image
    return image.size[0], image.size[1], list(image.pixels[:])


def flat_material(color, material_cache):
    key = tuple(int(round(max(0.0, min(1.0, component)) * 15.0)) for component in color[:3])
    material = material_cache.get(key)
    if material is not None:
        return material

    quantized = tuple(component / 15.0 for component in key) + (1.0,)
    material = bpy.data.materials.new(
        f"{FLAT_MATERIAL_PREFIX} {key[0]:02d}-{key[1]:02d}-{key[2]:02d}"
    )
    material.diffuse_color = quantized
    material.use_nodes = True
    bsdf = next(
        node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"
    )
    bsdf.inputs["Base Color"].default_value = quantized
    bsdf.inputs["Roughness"].default_value = 0.88
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.22
    material_cache[key] = material
    return material


def assign_flat_palette_materials(mesh, palette, material_cache):
    width, height, pixels = palette
    uv_layer = mesh.uv_layers.active
    if uv_layer is None:
        fallback = flat_material((0.78, 0.9, 0.38, 1.0), material_cache)
        mesh.materials.clear()
        mesh.materials.append(fallback)
        return

    mesh.materials.clear()
    slot_indices = {}
    for polygon in mesh.polygons:
        loop_uvs = [uv_layer.data[index].uv for index in polygon.loop_indices]
        u = sum(uv.x for uv in loop_uvs) / len(loop_uvs)
        v = sum(uv.y for uv in loop_uvs) / len(loop_uvs)
        u = max(0.0, min(0.999999, u - math.floor(u) if u < 0.0 or u > 1.0 else u))
        v = max(0.0, min(0.999999, v - math.floor(v) if v < 0.0 or v > 1.0 else v))
        x = min(width - 1, int(u * width))
        y = min(height - 1, int(v * height))
        pixel_index = (y * width + x) * 4
        color = brighten_palette_pixel(*pixels[pixel_index : pixel_index + 4])
        material = flat_material(color, material_cache)
        if material not in slot_indices:
            slot_indices[material] = len(mesh.materials)
            mesh.materials.append(material)
        polygon.material_index = slot_indices[material]


def remove_old_decorations():
    for collection_name in (COLLECTION_NAME, LEGACY_COLLECTION_NAME):
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            continue
        for obj in list(collection.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)

    for obj in list(bpy.data.objects):
        if obj.name.startswith((OBJECT_PREFIX, LEGACY_OBJECT_PREFIX)):
            bpy.data.objects.remove(obj, do_unlink=True)

    for material in list(bpy.data.materials):
        if material.name.startswith(FLAT_MATERIAL_PREFIX) or material.name == BRIGHT_MATERIAL_NAME:
            bpy.data.materials.remove(material, do_unlink=True)
    old_image = bpy.data.images.get(BRIGHT_IMAGE_NAME)
    if old_image is not None:
        bpy.data.images.remove(old_image, do_unlink=True)


remove_old_decorations()

preexisting_objects = set(bpy.data.objects)
root_names = sorted({root for roots in ASSET_GROUPS.values() for root in roots})
requested_names = sorted(set(root_names + [child_object_name(root) for root in root_names]))

with bpy.data.libraries.load(SOURCE_BLEND, link=False) as (data_from, data_to):
    missing = [name for name in requested_names if name not in data_from.objects]
    if missing:
        raise RuntimeError(f"Missing garden source objects: {missing}")
    data_to.objects = requested_names

loaded_by_name = {
    obj.name: obj for obj in data_to.objects if obj is not None
}

# Library-loaded hierarchy transforms are not evaluated reliably while the
# source objects are completely unlinked. Link the temporary hierarchy once,
# update the view layer, then capture the same world matrices seen in Blender.
temporary_collection = bpy.data.collections.new("Temporary garden source hierarchy")
bpy.context.scene.collection.children.link(temporary_collection)
temporary_source_objects = [
    obj for obj in bpy.data.objects if obj not in preexisting_objects
]
for obj in temporary_source_objects:
    if not obj.users_collection:
        temporary_collection.objects.link(obj)
bpy.context.view_layer.update()

sample_source = loaded_by_name[child_object_name(root_names[0])]
palette = source_palette(sample_source.data.materials[0])
material_cache = {}

templates = {}
for asset_key, group_roots in ASSET_GROUPS.items():
    meshes = []
    for root_name in group_roots:
        source = loaded_by_name[child_object_name(root_name)]
        if source is None or source.type != "MESH":
            raise RuntimeError(f"Garden source object is not a mesh: {root_name}")
        mesh = source.data.copy()
        mesh.name = f"Garden {asset_key} normalized part Mesh"
        mesh.transform(source.matrix_world)
        meshes.append(mesh)

    minimum, maximum = mesh_bounds(meshes)
    center = (minimum + maximum) * 0.5
    height = maximum.z - minimum.z
    normalize = Matrix.Scale(1.0 / max(height, 0.001), 4) @ Matrix.Translation(
        (-center.x, -center.y, -minimum.z)
    )

    for mesh in meshes:
        mesh.transform(normalize)
        assign_flat_palette_materials(mesh, palette, material_cache)
        for polygon in mesh.polygons:
            polygon.use_smooth = False
    templates[asset_key] = meshes

# The loaded source objects and dependency empties are no longer needed. The
# normalized mesh copies retain the bright material and packed palette image.
for obj in [obj for obj in bpy.data.objects if obj not in preexisting_objects]:
    bpy.data.objects.remove(obj, do_unlink=True)
if temporary_collection.name in bpy.data.collections:
    bpy.data.collections.remove(temporary_collection)

collection = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(collection)

created_roots = []
for index, placement in enumerate(PLACEMENTS, start=1):
    asset_key = placement["asset"]
    parent = bpy.data.objects.new(
        f"{OBJECT_PREFIX} {index:02d} {placement['kind']} {asset_key}",
        None,
    )
    parent.empty_display_type = "PLAIN_AXES"
    collection.objects.link(parent)

    x, y = placement["location"]
    parent.location = (x, y, world_top(placement["surface"]) + 0.006)
    parent.rotation_euler.z = math.radians(placement["rotation"])
    target_height = placement["height"]
    parent.scale = (target_height, target_height, target_height)
    parent["garden_source_roots"] = ",".join(ASSET_GROUPS[asset_key])
    parent["garden_surface"] = placement["surface"]
    parent["garden_kind"] = placement["kind"]
    parent["target_height"] = target_height
    created_roots.append(parent)

    for part_index, mesh in enumerate(templates[asset_key], start=1):
        obj = bpy.data.objects.new(f"{parent.name} part {part_index:02d}", mesh)
        collection.objects.link(obj)
        obj.parent = parent
        obj.location = (0.0, 0.0, 0.0)

bpy.context.scene["bright_garden_source"] = SOURCE_BLEND
bpy.context.scene["bright_garden_tree_count"] = sum(
    placement["kind"] == "tree" for placement in PLACEMENTS
)
bpy.context.scene["bright_garden_flower_count"] = sum(
    placement["kind"] == "flower" for placement in PLACEMENTS
)
bpy.ops.wm.save_as_mainfile(filepath=TARGET_BLEND)

print(f"Saved bright garden decorations into: {TARGET_BLEND}")
print(f"Tree count: {bpy.context.scene['bright_garden_tree_count']}")
print(f"Flower count: {bpy.context.scene['bright_garden_flower_count']}")
for parent in created_roots:
    print(
        f"{parent.name}: location={tuple(round(value, 3) for value in parent.location)}, "
        f"target_height={parent['target_height']}"
    )
