import math
import os

import bpy
from mathutils import Matrix, Vector


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_BLEND = os.path.join(
    os.path.dirname(PROJECT_DIR),
    "Forest Nature",
    "forest_nature_set_all_in.blend",
)
TARGET_BLEND = os.path.join(PROJECT_DIR, "models", "sky_island_lowpoly.blend")

SOURCE_OBJECT_NAME = "Log_small_regular"
SURFACE_NAME = "Right high stair terrace grass cap"
COLLECTION_NAME = "Imported light brown log benches"
OBJECT_PREFIX = "log bench imported"
MATERIAL_PREFIX = "Log bench light brown"

PLACEMENTS = [
    {"location": (-1.68, -5.03), "rotation": 8.0, "length": 1.25},
    {"location": (-1.55, -3.02), "rotation": -6.0, "length": 1.25},
    {"location": (-0.35, -4.05), "rotation": 83.0, "length": 1.25},
]


def mesh_bounds(mesh):
    points = [vertex.co for vertex in mesh.vertices]
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


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = next(
        node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"
    )
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.9
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.18
    return material


def remove_previous_import():
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


if not os.path.exists(SOURCE_BLEND):
    raise RuntimeError(f"Forest source blend not found: {SOURCE_BLEND}")

remove_previous_import()

with bpy.data.libraries.load(SOURCE_BLEND, link=False) as (data_from, data_to):
    if SOURCE_OBJECT_NAME not in data_from.objects:
        raise RuntimeError(f"Missing forest source object: {SOURCE_OBJECT_NAME}")
    data_to.objects = [SOURCE_OBJECT_NAME]

source = data_to.objects[0]
if source is None or source.type != "MESH":
    raise RuntimeError(f"Forest source object is not a mesh: {SOURCE_OBJECT_NAME}")

mesh = source.data.copy()
mesh.name = "Light brown low poly log bench Mesh"
mesh.transform(source.matrix_world)

minimum, maximum = mesh_bounds(mesh)
center = (minimum + maximum) * 0.5
length = maximum.x - minimum.x
normalize = Matrix.Scale(1.0 / max(length, 0.001), 4) @ Matrix.Translation(
    (-center.x, -center.y, -minimum.z)
)
mesh.transform(normalize)
mesh.update()

side_material = make_material(
    f"{MATERIAL_PREFIX} side",
    (0.61, 0.38, 0.20, 1.0),
)
top_material = make_material(
    f"{MATERIAL_PREFIX} top",
    (0.72, 0.49, 0.27, 1.0),
)
end_material = make_material(
    f"{MATERIAL_PREFIX} cut end",
    (0.82, 0.62, 0.38, 1.0),
)
shadow_material = make_material(
    f"{MATERIAL_PREFIX} shadow",
    (0.43, 0.25, 0.13, 1.0),
)

mesh.materials.clear()
for material in (side_material, top_material, end_material, shadow_material):
    mesh.materials.append(material)

for polygon in mesh.polygons:
    polygon.use_smooth = False
    normal = polygon.normal
    if abs(normal.x) > 0.64:
        polygon.material_index = 2
    elif normal.z > 0.38:
        polygon.material_index = 1
    elif normal.z < -0.28:
        polygon.material_index = 3
    else:
        polygon.material_index = 0

bpy.data.objects.remove(source, do_unlink=True)

collection = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(collection)
surface_z = world_top(SURFACE_NAME) + 0.008

created = []
for index, placement in enumerate(PLACEMENTS, start=1):
    obj = bpy.data.objects.new(f"{OBJECT_PREFIX} {index:02d}", mesh)
    collection.objects.link(obj)
    x, y = placement["location"]
    obj.location = (x, y, surface_z)
    obj.rotation_euler.z = math.radians(placement["rotation"])
    scale = placement["length"]
    obj.scale = (scale, scale, scale)
    obj["forest_source"] = SOURCE_BLEND
    obj["forest_source_object"] = SOURCE_OBJECT_NAME
    obj["target_length"] = scale
    obj["placement_surface"] = SURFACE_NAME
    created.append(obj)

bpy.context.scene["log_bench_count"] = len(created)
bpy.context.scene["log_bench_source"] = SOURCE_BLEND
bpy.ops.wm.save_as_mainfile(filepath=TARGET_BLEND)

print(f"Saved light brown log benches into: {TARGET_BLEND}")
for obj in created:
    print(
        f"{obj.name}: location={tuple(round(value, 3) for value in obj.location)}, "
        f"dimensions={tuple(round(value, 3) for value in obj.dimensions)}, "
        f"rotation_z={round(math.degrees(obj.rotation_euler.z), 1)}"
    )
