from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
BLEND_PATH = ROOT / "models" / "sky_island_lowpoly.blend"


def make_material(name, color, roughness=0.86, emission_strength=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = color
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


FIRE_MATS = {
    "flame_deep": make_material("Cartoon fire warm red orange", (0.94, 0.22, 0.06, 1.0), emission_strength=0.15),
    "flame_mid": make_material("Cartoon fire soft orange", (1.0, 0.48, 0.12, 1.0), emission_strength=0.18),
    "flame_light": make_material("Cartoon fire peach yellow", (1.0, 0.73, 0.30, 1.0), emission_strength=0.12),
    "wood_bark": make_material("Cartoon campfire terracotta bark", (0.58, 0.25, 0.10, 1.0)),
    "wood_cut": make_material("Cartoon campfire warm cut wood", (0.82, 0.47, 0.20, 1.0)),
    "wood_crack": make_material("Cartoon campfire carved wood lines", (0.36, 0.14, 0.06, 1.0)),
    "stone_light": make_material("Cartoon campfire light warm stone", (0.86, 0.78, 0.65, 1.0)),
    "stone_mid": make_material("Cartoon campfire warm gray stone", (0.58, 0.52, 0.44, 1.0)),
    "stone_shadow": make_material("Cartoon campfire muted stone shadow", (0.38, 0.33, 0.28, 1.0)),
    "ash": make_material("Cartoon campfire warm ash base", (0.31, 0.23, 0.17, 1.0)),
}


def flat(obj):
    if obj.type == "MESH" and hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = False


def style_flame(obj):
    if not obj.get("cartoon_fire_flame_halved"):
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        zs = [v.co.z for v in obj.data.vertices]
        center_x = (min(xs) + max(xs)) * 0.5
        center_y = (min(ys) + max(ys)) * 0.5
        base_z = min(zs)
        for vertex in obj.data.vertices:
            vertex.co.x = center_x + (vertex.co.x - center_x) * 0.5
            vertex.co.y = center_y + (vertex.co.y - center_y) * 0.5
            vertex.co.z = base_z + (vertex.co.z - base_z) * 0.5
        obj.data.update()
        obj["cartoon_fire_flame_halved"] = True

    obj.data.materials.clear()
    obj.data.materials.append(FIRE_MATS["flame_deep"])
    obj.data.materials.append(FIRE_MATS["flame_mid"])
    obj.data.materials.append(FIRE_MATS["flame_light"])

    z_values = [v.co.z for v in obj.data.vertices]
    min_z = min(z_values)
    max_z = max(z_values)
    span = max(max_z - min_z, 0.0001)
    for poly in obj.data.polygons:
        center_z = sum(obj.data.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
        t = (center_z - min_z) / span
        if t > 0.62 or poly.index % 7 == 0:
            poly.material_index = 2
        elif t > 0.28 or poly.index % 3 == 0:
            poly.material_index = 1
        else:
            poly.material_index = 0
    flat(obj)


def style_logs(obj):
    obj.data.materials.clear()
    obj.data.materials.append(FIRE_MATS["wood_bark"])
    obj.data.materials.append(FIRE_MATS["wood_cut"])
    obj.data.materials.append(FIRE_MATS["wood_crack"])
    for poly in obj.data.polygons:
        poly.material_index = min(poly.material_index, len(obj.data.materials) - 1)
    flat(obj)


def style_stone_ring(obj):
    obj.data.materials.clear()
    obj.data.materials.append(FIRE_MATS["stone_light"])
    obj.data.materials.append(FIRE_MATS["stone_mid"])
    obj.data.materials.append(FIRE_MATS["stone_shadow"])
    for poly in obj.data.polygons:
        poly.material_index = poly.index % 3
    flat(obj)


def style_ash_base(obj):
    obj.data.materials.clear()
    obj.data.materials.append(FIRE_MATS["ash"])
    for poly in obj.data.polygons:
        poly.material_index = 0
    flat(obj)


def main():
    styled = []
    for obj in bpy.data.objects:
        if obj.name.startswith("fire imported Campfire_0"):
            style_flame(obj)
            styled.append(obj.name)
        elif obj.name.startswith("fire imported Campfire_1"):
            style_logs(obj)
            styled.append(obj.name)
        elif obj.name.startswith("fire imported plate_0"):
            style_stone_ring(obj)
            styled.append(obj.name)
        elif obj.name.startswith("fire imported plate_1"):
            style_ash_base(obj)
            styled.append(obj.name)

    if not styled:
        raise RuntimeError("No imported fire objects found to style")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("Styled fire objects:")
    for name in styled:
        print(f"- {name}")


if __name__ == "__main__":
    main()
