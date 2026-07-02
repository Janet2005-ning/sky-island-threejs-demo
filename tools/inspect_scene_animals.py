"""Print the transforms and world bounds of Sky Island animal roots."""

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def arguments():
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    return parser.parse_args(values)


def descendants(root):
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(root):
    points = []
    for obj in descendants(root):
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def main():
    args = arguments()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(args.input).resolve()))
    bpy.context.view_layer.update()
    report = []
    for name in ("ANIMAL_BEAR_ROOT", "ANIMAL_CAT_ROOT", "ANIMAL_DUCK_ROOT", "ANIMAL_FROG_ROOT"):
        root = bpy.data.objects.get(name)
        minimum, maximum = bounds(root)
        report.append(
            {
                "name": name,
                "location": [round(v, 6) for v in root.location],
                "rotation_euler": [round(v, 6) for v in root.rotation_euler],
                "scale": [round(v, 6) for v in root.scale],
                "bounds_min": [round(v, 6) for v in minimum],
                "bounds_max": [round(v, 6) for v in maximum],
                "dimensions": [round(v, 6) for v in maximum - minimum],
            }
        )
    print("SCENE_ANIMAL_REPORT=" + json.dumps(report))


if __name__ == "__main__":
    main()
