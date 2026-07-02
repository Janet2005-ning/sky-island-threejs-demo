import math

import bpy


EXPECTED = {
    "BEAR": {
        "bench": "log bench imported 01",
        "offset": -0.215,
        "features": ("FACE_TEXTURE", "PENCIL_YELLOW", "ARM_PENCIL"),
    },
    "CAT": {
        "bench": "log bench imported 01",
        "offset": 0.215,
        "features": ("FACE_TEXTURE", "PURPLE_DRESS", "ARM_WAVE"),
    },
    "DUCK": {
        "bench": "log bench imported 02",
        "offset": -0.215,
        "features": ("FACE_TEXTURE", "WING_L", "WING_R"),
    },
    "FROG": {
        "bench": "log bench imported 02",
        "offset": 0.215,
        "features": ("FACE_TEXTURE", "BOOK_COVER", "BOOK_PAGES"),
    },
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    collection = bpy.data.collections.get("Seated cartoon animals")
    require(collection is not None, "Missing seated cartoon animal collection")

    reports = []
    for character, expected in EXPECTED.items():
        root = bpy.data.objects.get(f"ANIMAL_{character}_ROOT")
        require(root is not None, f"Missing {character} root")
        bench = bpy.data.objects.get(expected["bench"])
        require(bench is not None, f"Missing seat bench for {character}")
        require(root.get("seat_bench") == expected["bench"], f"Wrong bench for {character}")
        require(math.isclose(root.get("seat_offset"), expected["offset"], abs_tol=1e-6), f"Wrong seat offset for {character}")
        require(root.get("pose") == "seated_facing_campfire", f"Wrong pose for {character}")

        seat_top = bench.location.z + bench.dimensions.z
        require(abs(root.location.z - (seat_top + 0.006)) < 0.002, f"{character} is not seated on bench top")
        require(len(root.children) >= 9, f"{character} is missing modeled body parts")
        child_names = {child.name for child in root.children}
        for feature in expected["features"]:
            require(any(feature in name for name in child_names), f"{character} missing {feature}")

        face = bpy.data.objects.get(f"ANIMAL_{character}_FACE_TEXTURE")
        require(face is not None and face.type == "MESH", f"Missing face mesh for {character}")
        require(face.data.uv_layers, f"Missing face UVs for {character}")
        require(face.data.materials, f"Missing face material for {character}")
        image_nodes = [node for node in face.data.materials[0].node_tree.nodes if node.type == "TEX_IMAGE"]
        require(len(image_nodes) == 1 and image_nodes[0].image is not None, f"Missing face texture image for {character}")
        require(image_nodes[0].image.packed_file is not None, f"Face texture is not packed for {character}")

        reports.append(
            {
                "character": character.lower(),
                "bench": expected["bench"],
                "offset": expected["offset"],
                "root_z": round(root.location.z, 4),
                "bench_top": round(seat_top, 4),
                "modeled_parts": len(root.children),
                "texture": image_nodes[0].image.name,
            }
        )

    require(bpy.context.scene.get("seated_cartoon_animal_count") == 4, "Scene count metadata is not 4")
    print("SEATED_ANIMALS_VERIFIED")
    for report in reports:
        print(report)


if __name__ == "__main__":
    main()
