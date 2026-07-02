from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
GLB_PATH = ROOT / "public" / "models" / "sky_island_lowpoly.glb"
PREVIEW_PATH = ROOT / "public" / "assets" / "sky_island_blender_preview.png"
ANIMATION_COLLECTION_NAME = "Fountain_Animation"
BRIDGE_PIECE_PREFIX = "BRIDGE_PIECE_"


def reveal_animation_components_for_export():
    collection = bpy.data.collections.get(ANIMATION_COLLECTION_NAME)
    if collection is None:
        return None

    state = {
        "collection": collection,
        "hide_viewport": collection.hide_viewport,
        "hide_render": collection.hide_render,
        "objects": [],
    }
    collection.hide_viewport = False
    collection.hide_render = False
    for obj in collection.objects:
        state["objects"].append((obj, obj.hide_get(), obj.hide_viewport, obj.hide_render))
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
    return state


def restore_animation_component_visibility(state):
    if state is None:
        return
    for obj, hidden, hide_viewport, hide_render in state["objects"]:
        obj.hide_set(hidden)
        obj.hide_viewport = hide_viewport
        obj.hide_render = hide_render
    collection = state["collection"]
    collection.hide_viewport = state["hide_viewport"]
    collection.hide_render = state["hide_render"]


def reveal_bridge_pieces_for_export():
    state = []
    for obj in bpy.data.objects:
        if not obj.name.startswith(BRIDGE_PIECE_PREFIX):
            continue
        state.append((obj, obj.hide_get(), obj.hide_viewport, obj.hide_render))
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
    bpy.context.view_layer.update()
    return state


def restore_bridge_piece_visibility(state):
    for obj, hidden, hide_viewport, hide_render in state:
        obj.hide_set(hidden)
        obj.hide_viewport = hide_viewport
        obj.hide_render = hide_render
    bpy.context.view_layer.update()


def scene_mesh_bounds():
    min_v = Vector((1e9, 1e9, 1e9))
    max_v = Vector((-1e9, -1e9, -1e9))
    found_mesh = False
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        found_mesh = True
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ Vector(corner)
            min_v.x = min(min_v.x, world_corner.x)
            min_v.y = min(min_v.y, world_corner.y)
            min_v.z = min(min_v.z, world_corner.z)
            max_v.x = max(max_v.x, world_corner.x)
            max_v.y = max(max_v.y, world_corner.y)
            max_v.z = max(max_v.z, world_corner.z)
    if not found_mesh:
        return Vector((0, 0, 0)), Vector((1, 1, 1))
    return (min_v + max_v) * 0.5, max_v - min_v


def frame_preview_camera(scene):
    center, size = scene_mesh_bounds()
    camera = scene.camera
    if camera is None:
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        scene.camera = camera
    camera.name = "Preview camera"
    direction = Vector((0.76, -0.72, 0.48)).normalized()
    span = max(size.x, size.y, size.z * 1.7, 1.0)
    camera.location = center + direction * (span * 1.45)
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 30
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = (center - camera.location).length
    camera.data.dof.aperture_fstop = 8


def export_glb():
    GLB_PATH.parent.mkdir(parents=True, exist_ok=True)
    animation_state = reveal_animation_components_for_export()
    bridge_state = reveal_bridge_pieces_for_export()
    try:
        bpy.ops.export_scene.gltf(
            filepath=str(GLB_PATH),
            export_format="GLB",
            export_apply=True,
            export_yup=True,
            export_materials="EXPORT",
            export_extras=True,
            export_cameras=False,
            export_lights=False,
        )
    finally:
        restore_bridge_piece_visibility(bridge_state)
        restore_animation_component_visibility(animation_state)


def render_preview():
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
        if hasattr(scene.eevee, "gtao_distance"):
            scene.eevee.gtao_distance = 3
        if hasattr(scene.eevee, "gtao_factor"):
            scene.eevee.gtao_factor = 1.35
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    frame_preview_camera(scene)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.15
    scene.view_settings.gamma = 1
    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)


def main():
    export_glb()
    render_preview()
    print(f"Updated web GLB from saved blend: {GLB_PATH}")
    print(f"Updated preview from saved blend: {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
