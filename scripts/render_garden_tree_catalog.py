import math
import os

import bpy
from mathutils import Matrix, Vector


TREE_GROUPS = [
    ("Tree 06", ["Cylinder.006", "Sphere.011", "Sphere.012"]),
    ("Tree 07", ["Cylinder.007", "Sphere.013", "Sphere.014", "Sphere.015"]),
    ("Tree 20", ["Cylinder.020", "Sphere.035", "Sphere.036", "Sphere.037"]),
    ("Tree 21", ["Cylinder.021", "Sphere.038", "Sphere.039", "Sphere.040"]),
    ("Tree 22", ["Cylinder.022", "Cube.044", "Cube.045", "Cube.046", "Cube.047"]),
    ("Tree 23", ["Cylinder.023", "Cube.048", "Cube.050", "Cube.051", "Cube.052"]),
    ("Tree 24", ["Cylinder.024"] + [f"Sphere.{index:03d}" for index in range(41, 59)]),
    ("Tree 25", ["Cylinder.025", "Sphere.059", "Sphere.060", "Sphere.061"]),
    ("Pink-Tree", ["Pink-Tree"]),
]

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "public",
    "assets",
    "garden_tree_catalog.png",
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


def mesh_points(mesh):
    return [vertex.co for vertex in mesh.vertices]


def group_bounds(meshes):
    points = [point for mesh in meshes for point in mesh_points(mesh)]
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


captured_groups = []
for group_name, root_names in TREE_GROUPS:
    meshes = []
    for root_name in root_names:
        root = bpy.data.objects.get(root_name)
        if root is None:
            raise RuntimeError(f"Missing tree root: {root_name}")
        children = [child for child in root.children_recursive if child.type == "MESH"]
        if len(children) != 1:
            raise RuntimeError(f"Expected one mesh below {root_name}, found {len(children)}")
        source = children[0]
        mesh = source.data.copy()
        mesh.name = f"Catalog {group_name} {root_name} Mesh"
        mesh.transform(source.matrix_world)
        meshes.append(mesh)

    minimum, maximum = group_bounds(meshes)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    transform = Matrix.Scale(2.8 / max(size.z, 0.001), 4) @ Matrix.Translation(
        (-center.x, -center.y, -minimum.z)
    )
    for mesh in meshes:
        mesh.transform(transform)
    captured_groups.append((group_name, meshes, size))

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1500
scene.render.resolution_y = 930
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = OUTPUT_PATH
scene.world = bpy.data.worlds.new("Tree Catalog World")
scene.world.color = (0.72, 0.9, 0.94)
scene.view_settings.look = "Medium High Contrast"

ground_material = make_material("Tree Catalog Ground", (0.73, 0.82, 0.34, 1.0))
label_material = make_material("Tree Catalog Labels", (0.08, 0.12, 0.13, 1.0))

for index, (group_name, meshes, _) in enumerate(captured_groups):
    column = index % 3
    row = index // 3
    x = (column - 1) * 6.2
    y = 5.8 - row * 5.8

    for mesh_index, mesh in enumerate(meshes):
        obj = bpy.data.objects.new(f"Catalog {group_name} part {mesh_index + 1}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (x, y, 0.04)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=2.0, depth=0.10, location=(x, y, -0.02))
    base = bpy.context.object
    base.name = f"Catalog base {group_name}"
    base.data.materials.append(ground_material)

    bpy.ops.object.text_add(location=(x, y - 2.25, 0.08))
    label = bpy.context.object
    label.name = f"Catalog label {group_name}"
    label.data.body = f"{index + 1}. {group_name}"
    label.data.align_x = "CENTER"
    label.data.align_y = "CENTER"
    label.data.size = 0.44
    label.data.extrude = 0.008
    label.data.materials.append(label_material)

bpy.ops.object.camera_add(location=(0.0, -28.0, 26.0))
camera = bpy.context.object
camera.name = "Tree Catalog Camera"
look_at(camera, (0.0, 0.0, 1.1))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 23.5
scene.camera = camera

for energy, rotation in (
    (4.0, (math.radians(24), 0.0, math.radians(-28))),
    (2.0, (math.radians(58), 0.0, math.radians(135))),
):
    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.0, 14.0), rotation=rotation)
    light = bpy.context.object
    light.data.energy = energy * 700
    light.data.shape = "DISK"
    light.data.size = 12.0

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
bpy.ops.render.render(write_still=True)

print(f"Rendered tree catalog: {OUTPUT_PATH}")
for index, (group_name, _, size) in enumerate(captured_groups):
    print(f"{index + 1}. {group_name}: source dimensions {tuple(round(value, 3) for value in size)}")
