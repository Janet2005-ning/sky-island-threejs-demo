"""Convert one low-poly FBX character into a web-ready GLB asset.

Usage:
  blender --background --factory-startup --python tools/prepare_low_animal.py -- \
    --input "../low cat.fbx" --output "public/models/animals/low_cat.glb" --name cat
"""

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--texture-size", type=int, default=1024)
    return parser.parse_args(arguments)


def linked_image(socket):
    if not socket or not socket.is_linked:
        return None
    pending = [link.from_node for link in socket.links]
    visited = set()
    while pending:
        node = pending.pop()
        if node in visited:
            continue
        visited.add(node)
        if node.type == "TEX_IMAGE" and node.image:
            return node.image
        for input_socket in node.inputs:
            pending.extend(link.from_node for link in input_socket.links)
    return None


def disconnect(socket):
    if not socket:
        return
    for link in list(socket.links):
        socket.id_data.links.remove(link)


def standardize_material(material, texture_size):
    material.use_nodes = True
    material.diffuse_color[3] = 1.0
    nodes = material.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not principled:
        return None

    base_color = principled.inputs.get("Base Color")
    base_image = linked_image(base_color)
    if base_image:
        width, height = base_image.size
        longest = max(width, height)
        if longest > texture_size:
            scale = texture_size / longest
            base_image.scale(max(1, round(width * scale)), max(1, round(height * scale)))
        base_image.colorspace_settings.name = "sRGB"

    settings = {
        "Metallic": 0.0,
        "Roughness": 0.82,
        "Specular IOR Level": 0.24,
        "Coat Weight": 0.0,
        "Emission Strength": 0.0,
    }
    for socket_name, value in settings.items():
        socket = principled.inputs.get(socket_name)
        if socket:
            disconnect(socket)
            socket.default_value = value

    normal = principled.inputs.get("Normal")
    disconnect(normal)
    for node in list(nodes):
        if node.type == "TEX_IMAGE" and node.image is not base_image:
            nodes.remove(node)
    return base_image


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("The FBX contains no mesh bounds")
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def main():
    args = parse_args()
    source = Path(args.input).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(source), use_anim=False)

    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT", "ARMATURE"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    imported = list(bpy.context.scene.objects)
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError(f"No mesh found in {source}")

    root = bpy.data.objects.new(f"LOW_{args.name.upper()}_ASSET_ROOT", None)
    bpy.context.scene.collection.objects.link(root)
    root["source_fbx"] = source.name
    root["character_id"] = args.name.lower()
    root["web_material"] = "sky_island_matte"

    for obj in imported:
        if obj.parent is not None:
            continue
        matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = matrix

    minimum, maximum = world_bounds(meshes)
    center = (minimum + maximum) * 0.5
    # Blender is Z-up. Center the character on X/Y and place its feet at Z=0;
    # the glTF exporter then converts the asset to Three.js' Y-up convention.
    root.location = Vector((-center.x, -center.y, -minimum.z))
    bpy.context.view_layer.update()

    used_images = set()
    triangle_count = 0
    vertex_count = 0
    for obj in meshes:
        obj.name = f"LOW_{args.name.upper()}_MESH"
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
            triangle_count += max(0, len(polygon.vertices) - 2)
        vertex_count += len(obj.data.vertices)
        for material in obj.data.materials:
            if not material:
                continue
            material.name = f"LOW_{args.name.upper()}_MAT"
            image = standardize_material(material, args.texture_size)
            if image:
                used_images.add(image)

    minimum_after, maximum_after = world_bounds(meshes)
    dimensions = maximum_after - minimum_after

    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_image_format="JPEG",
        export_image_quality=82,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_skins=False,
        export_morph=False,
        export_extras=True,
        export_yup=True,
        export_apply=True,
        export_unused_images=False,
        export_unused_textures=False,
    )

    report = {
        "character": args.name.lower(),
        "source": str(source),
        "output": str(output),
        "vertices": vertex_count,
        "triangles": triangle_count,
        "dimensions": [round(value, 6) for value in dimensions],
        "bounds_min": [round(value, 6) for value in minimum_after],
        "bounds_max": [round(value, 6) for value in maximum_after],
        "base_images": [
            {"name": image.name, "size": list(image.size)} for image in sorted(used_images, key=lambda item: item.name)
        ],
        "output_bytes": output.stat().st_size,
    }
    print("LOW_ANIMAL_REPORT=" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
