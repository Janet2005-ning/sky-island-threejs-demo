from pathlib import Path
import shutil

import bpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIRE_PATH = Path(r"D:\aidocument\fire.blend")
PROJECT_FIRE_PATH = ROOT / "models" / "fire.blend"

FIRE_PARENT_NAME = "Imported fire on right high island"
FIRE_LOCATION = (-1.62, -4.05, 0.82)
FIRE_SCALE = 1.9


def remove_existing_fire():
    to_remove = []
    for obj in bpy.data.objects:
        if obj.name == FIRE_PARENT_NAME or obj.name.startswith("fire imported "):
            to_remove.append(obj)

    for obj in to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)


def append_fire_objects():
    if not SOURCE_FIRE_PATH.exists():
        raise FileNotFoundError(f"Missing source fire blend: {SOURCE_FIRE_PATH}")

    PROJECT_FIRE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SOURCE_FIRE_PATH.resolve() != PROJECT_FIRE_PATH.resolve():
        shutil.copy2(SOURCE_FIRE_PATH, PROJECT_FIRE_PATH)

    with bpy.data.libraries.load(str(PROJECT_FIRE_PATH), link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)

    fire_objects = []
    for obj in data_to.objects:
        if not obj or obj.type != "MESH":
            continue
        bpy.context.collection.objects.link(obj)
        obj.name = f"fire imported {obj.name}"
        if hasattr(obj.data, "polygons"):
            for poly in obj.data.polygons:
                poly.use_smooth = False
        fire_objects.append(obj)

    if not fire_objects:
        raise RuntimeError(f"No mesh objects found in {PROJECT_FIRE_PATH}")

    parent = bpy.data.objects.new(FIRE_PARENT_NAME, None)
    parent.empty_display_type = "PLAIN_AXES"
    bpy.context.collection.objects.link(parent)
    parent.location = FIRE_LOCATION
    parent.scale = (FIRE_SCALE, FIRE_SCALE, FIRE_SCALE)

    for obj in fire_objects:
        obj.parent = parent

    return parent


def main():
    remove_existing_fire()
    parent = append_fire_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "models" / "sky_island_lowpoly.blend"))
    print(f"Added fire model at {tuple(round(v, 3) for v in parent.location)} scale {FIRE_SCALE}")
    print(f"Copied fire source to {PROJECT_FIRE_PATH}")


if __name__ == "__main__":
    main()
