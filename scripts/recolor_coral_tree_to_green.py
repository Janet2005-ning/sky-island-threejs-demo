from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"
TREE_ROOT_NAME = "garden decoration imported 01 tree tree_coral_crown"

CANOPY_PARTS = [
    f"{TREE_ROOT_NAME} part 02",
    f"{TREE_ROOT_NAME} part 03",
    f"{TREE_ROOT_NAME} part 04",
]
TRUNK_PART = f"{TREE_ROOT_NAME} part 01"

GREEN_MATERIAL_NAMES = [
    "Garden flat bright 04-08-02",
    "Garden flat bright 05-08-02",
    "Garden flat bright 04-07-02",
]
BROWN_MATERIAL_NAMES = [
    "Garden flat bright 07-05-03",
    "Garden flat bright 06-04-02",
    "Garden flat bright 07-04-02",
]


def require_materials(names):
    materials = []
    for name in names:
        material = bpy.data.materials.get(name)
        if material is None:
            raise RuntimeError(f"Required reference material is missing: {name}")
        materials.append(material)
    return materials


def assign_palette(obj, materials, offset=0):
    if obj is None or obj.type != "MESH":
        raise RuntimeError(f"Required tree mesh is missing: {obj}")

    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)

    for polygon in obj.data.polygons:
        polygon.use_smooth = False
        polygon.material_index = (polygon.index * 5 + offset) % len(materials)


def main():
    tree_root = bpy.data.objects.get(TREE_ROOT_NAME)
    if tree_root is None:
        raise RuntimeError(f"Tree root is missing: {TREE_ROOT_NAME}")

    green_materials = require_materials(GREEN_MATERIAL_NAMES)
    brown_materials = require_materials(BROWN_MATERIAL_NAMES)

    assign_palette(bpy.data.objects.get(TRUNK_PART), brown_materials)
    for index, part_name in enumerate(CANOPY_PARTS):
        assign_palette(bpy.data.objects.get(part_name), green_materials, index)

    tree_root["recolored_green_canopy"] = True
    tree_root["palette_note"] = "Green canopy and warm brown trunk matching other garden trees"
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print(f"Recolored tree and saved: {BLEND_PATH}")


if __name__ == "__main__":
    main()
