from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "assets" / "seated_cartoon_animals_preview.png"


def main():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(OUTPUT)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.45

    bpy.ops.object.camera_add(location=(0.45, -4.05, 1.72))
    camera = bpy.context.object
    camera.name = "Temporary seated animals preview camera"
    target = Vector((-1.96, -4.05, 1.22))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 35
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = (target - camera.location).length
    camera.data.dof.aperture_fstop = 9
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(-0.2, -4.05, 3.0))
    light = bpy.context.object
    light.name = "Temporary seated animals preview fill"
    light.data.energy = 45
    light.data.shape = "DISK"
    light.data.size = 4.0
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered seated cartoon animal preview: {OUTPUT}")


if __name__ == "__main__":
    main()
