import json
import struct
import sys
from pathlib import Path


def analyze(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise ValueError(f"Invalid GLB 2.0 file: {path}")
    offset = 12
    document = None
    binary_bytes = 0
    while offset < len(data):
        chunk_length, chunk_type = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_length]
        offset += chunk_length
        if chunk_type == b"JSON":
            document = json.loads(chunk.rstrip(b" \t\r\n\0"))
        elif chunk_type == b"BIN\0":
            binary_bytes += chunk_length
    if document is None:
        raise ValueError("GLB has no JSON chunk")

    accessors = document.get("accessors", [])
    meshes = document.get("meshes", [])
    nodes = document.get("nodes", [])

    def primitive_triangles(primitive):
        mode = primitive.get("mode", 4)
        index = primitive.get("indices")
        if index is not None:
            count = accessors[index]["count"]
        else:
            count = accessors[primitive["attributes"]["POSITION"]]["count"]
        if mode == 4:
            return count // 3
        if mode in (5, 6):
            return max(0, count - 2)
        return 0

    mesh_triangles = [sum(primitive_triangles(p) for p in mesh.get("primitives", [])) for mesh in meshes]

    children_by_node = {index: node.get("children", []) for index, node in enumerate(nodes)}

    def descendants(index):
        result = [index]
        for child in children_by_node[index]:
            result.extend(descendants(child))
        return result

    animal_roots = []
    for index, node in enumerate(nodes):
        name = node.get("name", "")
        if not (name.startswith("ANIMAL_") and name.endswith("_ROOT")):
            continue
        descendant_nodes = descendants(index)
        mesh_indices = [nodes[item]["mesh"] for item in descendant_nodes if "mesh" in nodes[item]]
        animal_roots.append(
            {
                "name": name,
                "nodes": len(descendant_nodes),
                "meshes": len(mesh_indices),
                "triangles": sum(mesh_triangles[item] for item in mesh_indices),
            }
        )

    image_bytes = 0
    for image in document.get("images", []):
        if "bufferView" in image:
            image_bytes += document["bufferViews"][image["bufferView"]]["byteLength"]

    return {
        "file": path.name,
        "bytes": len(data),
        "binary_bytes": binary_bytes,
        "nodes": len(nodes),
        "meshes": len(meshes),
        "materials": len(document.get("materials", [])),
        "textures": len(document.get("textures", [])),
        "images": len(document.get("images", [])),
        "embedded_image_bytes": image_bytes,
        "triangles": sum(mesh_triangles),
        "animals": animal_roots,
    }


if __name__ == "__main__":
    print(json.dumps([analyze(Path(item)) for item in sys.argv[1:]], indent=2, ensure_ascii=False))
