from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = ROOT / "textures" / "animal_characters"
KEY_ATLAS_PATH = TEXTURE_DIR / "animal_face_atlas_key.png"
ATLAS_PATH = TEXTURE_DIR / "animal_face_atlas.png"

QUADRANTS = {
    "bear_face.png": (0, 0),
    "cat_face.png": (1, 0),
    "duck_face.png": (0, 1),
    "frog_face.png": (1, 1),
}


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def build_transparent_atlas():
    source = Image.open(KEY_ATLAS_PATH).convert("RGBA")
    key = source.getpixel((5, 5))[:3]
    transparent_distance = 36
    opaque_distance = 90
    output = Image.new("RGBA", source.size)
    keyed_pixels = []
    for red, green, blue, source_alpha in source.getdata():
        distance = max(abs(red - key[0]), abs(green - key[1]), abs(blue - key[2]))
        if distance <= transparent_distance:
            alpha = 0
        elif distance >= opaque_distance:
            alpha = source_alpha
        else:
            progress = (distance - transparent_distance) / (
                opaque_distance - transparent_distance
            )
            alpha = round(source_alpha * smoothstep(progress))
        keyed_pixels.append((red, green, blue, alpha))
    output.putdata(keyed_pixels)
    output.save(ATLAS_PATH, optimize=True)
    print(f"atlas: size={output.size}, key={key}")
    return output


def main():
    atlas = build_transparent_atlas()
    width, height = atlas.size
    if width % 2 or height % 2:
        raise RuntimeError(f"Expected an even 2x2 atlas, got {atlas.size}")

    cell_width = width // 2
    cell_height = height // 2
    for filename, (column, row) in QUADRANTS.items():
        box = (
            column * cell_width,
            row * cell_height,
            (column + 1) * cell_width,
            (row + 1) * cell_height,
        )
        face = atlas.crop(box)
        output = TEXTURE_DIR / filename
        face.save(output, optimize=True)
        alpha_bbox = face.getchannel("A").getbbox()
        print(f"{filename}: size={face.size}, alpha_bbox={alpha_bbox}")


if __name__ == "__main__":
    main()
