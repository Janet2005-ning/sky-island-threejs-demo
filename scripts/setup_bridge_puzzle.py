from math import radians
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"
BRIDGE_PARENT_NAME = "Qiao imported block bridge between left island and main island"
GUIDE_COLLECTION_NAME = "Bridge_Puzzle_Guides"


# The current bridge is already made from twelve separate meshes.  Keep those
# meshes and turn them into stable, clickable puzzle pieces instead of
# replacing the user's hand-adjusted bridge with generated geometry.
PIECES = [
    ("qiao bridge Cube", "桥面主板"),
    ("qiao bridge 柱体.001", "右侧上扶手"),
    ("qiao bridge 柱体.002", "右侧下扶手"),
    ("qiao bridge 柱体.003", "左侧上扶手"),
    ("qiao bridge 柱体.004", "左侧下扶手"),
    ("qiao bridge 立方体", "桥面侧板一"),
    ("qiao bridge 立方体.001", "桥面侧板二"),
    ("qiao bridge 立方体.002", "右桥柱"),
    ("qiao bridge 立方体.003", "左桥柱"),
    ("qiao bridge 立方体.004", "桥头拱块"),
    ("qiao bridge 立方体.005", "右侧桥梁"),
    ("qiao bridge 立方体.006", "左侧桥梁"),
]


# Six visual/material styles.  Only the representative of each group floats in
# the Blender initial state.  When it lands in Three.js every member in the
# group is revealed at its own saved target transform.
BRIDGE_GROUPS = [
    (1, "蓝色桥面", 1, (1,)),
    (2, "红色扶手", 2, (2, 3, 4, 5)),
    (3, "绿色桥面侧板", 6, (6, 7)),
    (4, "粉色桥柱", 8, (8, 9)),
    (5, "黄色桥头拱块", 10, (10,)),
    (6, "橙色桥梁", 11, (11, 12)),
]
GROUP_BY_PIECE = {
    piece_index: (group_id, group_label, representative_index, members)
    for group_id, group_label, representative_index, members in BRIDGE_GROUPS
    for piece_index in members
}


# The six representatives form one horizontal row from the roam spawn point.
# In the exported Three.js scene Blender Z becomes world Y and -Blender Y
# becomes world Z. Poses for non-representatives are retained only for stable
# index alignment because those meshes remain hidden until their group lands.
SCATTER_POSES = [
    ((5.90, -6.35, 2.15), (8, -12, 8)),
    ((5.90, -1.60, 2.15), (-18, 8, 24)),
    ((5.80, -5.00, 3.20), (15, -10, -18)),
    ((7.40, -3.00, 2.60), (-12, 16, -20)),
    ((4.70, -3.00, 2.80), (20, 6, 16)),
    ((5.90, -5.40, 2.15), (-10, 14, 18)),
    ((5.15, -3.35, 2.15), (16, -8, -18)),
    ((5.90, -4.45, 2.15), (-24, 10, 18)),
    ((4.90, -4.60, 2.40), (18, -14, -12)),
    ((5.90, -3.50, 2.15), (-14, 18, 20)),
    ((5.90, -2.55, 2.15), (12, 10, -14)),
    ((5.90, -2.30, 3.55), (-16, -12, 18)),
]


def ensure_guide_collection():
    collection = bpy.data.collections.get(GUIDE_COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(GUIDE_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(collection)
    collection.hide_render = False
    collection.hide_viewport = False
    return collection


def get_piece(index, original_name):
    stable_name = f"BRIDGE_PIECE_{index:02d}"
    return bpy.data.objects.get(stable_name) or bpy.data.objects.get(original_name)


def ensure_target(index, parent, piece, collection):
    target_name = f"BRIDGE_TARGET_{index:02d}"
    target = bpy.data.objects.get(target_name)
    if target is None:
        target = bpy.data.objects.new(target_name, None)
        collection.objects.link(target)
        target.parent = parent
        target.matrix_basis = piece.matrix_basis.copy()
    target.empty_display_type = "CUBE"
    target.empty_display_size = 0.22
    target.show_in_front = True
    target["bridge_target"] = True
    target["bridge_piece_index"] = index
    return target


def scatter_piece(piece, target, world_location, rotation_degrees):
    # Newly created parented empties do not expose their evaluated world scale
    # until the dependency graph has been refreshed.  Without this update every
    # piece would accidentally receive unit world scale and appear ~10x larger.
    bpy.context.view_layer.update()
    target_location, target_rotation, target_scale = target.matrix_world.decompose()
    offset_rotation = Euler(tuple(radians(value) for value in rotation_degrees), "XYZ").to_quaternion()
    scatter_rotation = offset_rotation @ target_rotation
    piece.matrix_world = Matrix.LocRotScale(Vector(world_location), scatter_rotation, target_scale)


def main():
    parent = bpy.data.objects.get(BRIDGE_PARENT_NAME)
    if parent is None:
        parent = bpy.data.objects.get("BRIDGE_PUZZLE_ROOT")
    if parent is None:
        raise RuntimeError(f"Bridge parent not found: {BRIDGE_PARENT_NAME}")

    guide_collection = ensure_guide_collection()
    prepared = []

    for index, ((original_name, label), (world_location, rotation_degrees)) in enumerate(
        zip(PIECES, SCATTER_POSES), start=1
    ):
        piece = get_piece(index, original_name)
        if piece is None or piece.type != "MESH":
            raise RuntimeError(f"Bridge mesh not found: {original_name}")

        target = ensure_target(index, parent, piece, guide_collection)
        piece.name = f"BRIDGE_PIECE_{index:02d}"
        piece.data.name = f"BRIDGE_PIECE_{index:02d}_Mesh"
        piece["bridge_piece"] = True
        piece["bridge_piece_index"] = index
        piece["bridge_piece_label"] = label
        piece["bridge_target_name"] = target.name
        group_id, group_label, representative_index, members = GROUP_BY_PIECE[index]
        is_representative = index == representative_index
        piece["bridge_group_id"] = group_id
        piece["bridge_group_label"] = group_label
        piece["bridge_group_members"] = list(members)
        piece["bridge_group_representative"] = is_representative

        if is_representative:
            piece.hide_set(False)
            piece.hide_viewport = False
            piece.hide_render = False
            scatter_piece(piece, target, world_location, rotation_degrees)
        else:
            piece.matrix_basis = target.matrix_basis.copy()
            piece.hide_set(True)
            piece.hide_viewport = True
            piece.hide_render = True

        prepared.append((piece, target, label, group_id, is_representative))

    parent.name = "BRIDGE_PUZZLE_ROOT"
    parent["bridge_puzzle"] = True
    parent["bridge_piece_count"] = len(prepared)
    parent["bridge_group_count"] = len(BRIDGE_GROUPS)
    bpy.context.scene["bridge_puzzle_piece_count"] = len(prepared)
    bpy.context.scene["bridge_puzzle_group_count"] = len(BRIDGE_GROUPS)
    bpy.context.scene["bridge_puzzle_initial_state"] = "six_style_representatives"

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    print("BRIDGE_PUZZLE_SETUP_START")
    for piece, target, label, group_id, is_representative in prepared:
        displayed_location = piece.matrix_world.translation if is_representative else target.matrix_world.translation
        print(
            piece.name,
            label,
            f"group={group_id}",
            f"representative={is_representative}",
            "initial=",
            tuple(round(value, 4) for value in displayed_location),
            "target=",
            tuple(round(value, 4) for value in target.matrix_world.translation),
        )
    print("BRIDGE_PUZZLE_SETUP_END")
    print(f"Saved bridge puzzle into: {BLEND_PATH}")


if __name__ == "__main__":
    main()
