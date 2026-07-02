import math
import os

import bpy
from mathutils import Matrix, Vector


ASSET_NAMES = [
    "Bush",
    "Daizy-Bush",
    "Darknight-Bush",
    "Long2-Bush",
    "Red-Fw-Bush",
    "White-Poppy",
    "Purple-Poppy",
    "DarkNight-Poppy",
    "Box-Flowers",
    "Pink-Tree",
]

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "public",
    "assets",
    "garden_asset_catalog.png",
)


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.86
    return material


def mesh_bounds(mesh):
    points = [vertex.co for vertex in mesh.vertices]
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def capture_asset_mesh(asset_name):
    root = bpy.data.objects.get(asset_name)
    if root is None:
        raise RuntimeError(f"Missing source asset: {asset_name}")

    meshes = [child for child in root.children_recursive if child.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one mesh below {asset_name}, found {len(meshes)}")

    source = meshes[0]
    mesh = source.data.copy()
    mesh.name = f"Catalog {asset_name} Mesh"
    mesh.transform(source.matrix_world)

    minimum, maximum = mesh_bounds(mesh)
    center = (minimum + maximum) * 0.5
    mesh.transform(Matrix.Translation((-center.x, -center.y, -minimum.z)))

    minimum, maximum = mesh_bounds(mesh)
    size = maximum - minimum
    target_height = 2.25 if asset_name != "Pink-Tree" else 2.65
    scale = target_height / max(size.z, 0.001)
    mesh.transform(Matrix.Scale(scale, 4))
    return mesh, size


captured = []
for asset_name in ASSET_NAMES:
    mesh, original_size = capture_asset_mesh(asset_name)
    captured.append((asset_name, mesh, original_size))

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1500
scene.render.resolution_y = 760
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = OUTPUT_PATH
scene.render.image_settings.color_mode = "RGBA"
scene.world = bpy.data.worlds.new("Catalog World")
scene.world.color = (0.72, 0.9, 0.94)
scene.view_settings.look = "Medium High Contrast"

ground_material = make_material("Catalog Ground", (0.73, 0.82, 0.34, 1.0))
label_material = make_material("Catalog Labels", (0.08, 0.12, 0.13, 1.0))

positions = []
for index, (asset_name, mesh, original_size) in enumerate(captured):
    column = index % 5
    row = index // 5
    x = (column - 2) * 4.25
    y = 2.7 - row * 5.4
    positions.append((x, y))

    obj = bpy.data.objects.new(f"Catalog {asset_name}", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (x, y, 0.04)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.65, depth=0.10, location=(x, y, -0.02))
    base = bpy.context.object
    base.name = f"Catalog base {asset_name}"
    base.data.materials.append(ground_material)

    bpy.ops.object.text_add(location=(x, y - 1.9, 0.08))
    label = bpy.context.object
    label.name = f"Catalog label {asset_name}"
    label.data.body = f"{index + 1}. {asset_name}"
    label.data.align_x = "CENTER"
    label.data.align_y = "CENTER"
    label.data.size = 0.36
    label.data.extrude = 0.008
    label.data.materials.append(label_material)

bpy.ops.object.camera_add(location=(0.0, -24.5, 22.0))
camera = bpy.context.object
camera.name = "Catalog Camera"
look_at(camera, (0.0, 0.0, 0.8))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 21.5
scene.camera = camera

for energy, rotation in ((4.0, (math.radians(24), 0.0, math.radians(-28))), (2.0, (math.radians(58), 0.0, math.radians(135)))):
    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.0, 12.0), rotation=rotation)
    light = bpy.context.object
    light.data.energy = energy * 700
    light.data.shape = "DISK"
    light.data.size = 10.0

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
bpy.ops.render.render(write_still=True)

print(f"Rendered garden catalog: {OUTPUT_PATH}")
for index, (asset_name, _, original_size) in enumerate(captured):
    print(f"{index + 1}. {asset_name}: source dimensions {tuple(round(value, 3) for value in original_size)}")
