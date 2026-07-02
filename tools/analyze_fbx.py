import json
import struct
import sys
import zlib
from pathlib import Path


class FbxBinaryReader:
    def __init__(self, data):
        self.data = data
        self.position = 27
        self.version = struct.unpack_from("<I", data, 23)[0]

    def read_node(self):
        data = self.data
        position = self.position
        wide = self.version >= 7500
        if wide:
            end, property_count, _ = struct.unpack_from("<QQQ", data, position)
            position += 24
        else:
            end, property_count, _ = struct.unpack_from("<III", data, position)
            position += 12
        name_length = data[position]
        position += 1
        if end == 0:
            self.position = position
            return None

        name = data[position : position + name_length].decode("utf-8", "replace")
        position += name_length
        properties = []
        for _ in range(property_count):
            property_type = chr(data[position])
            position += 1
            if property_type == "Y":
                value = struct.unpack_from("<h", data, position)[0]
                position += 2
            elif property_type == "C":
                value = bool(data[position])
                position += 1
            elif property_type == "I":
                value = struct.unpack_from("<i", data, position)[0]
                position += 4
            elif property_type == "F":
                value = struct.unpack_from("<f", data, position)[0]
                position += 4
            elif property_type == "D":
                value = struct.unpack_from("<d", data, position)[0]
                position += 8
            elif property_type == "L":
                value = struct.unpack_from("<q", data, position)[0]
                position += 8
            elif property_type in "SR":
                length = struct.unpack_from("<I", data, position)[0]
                position += 4
                raw = data[position : position + length]
                position += length
                value = raw.decode("utf-8", "replace") if property_type == "S" else {"raw_bytes": length}
            elif property_type in "fdilbc":
                length, encoding, compressed_length = struct.unpack_from("<III", data, position)
                position += 12
                raw = data[position : position + compressed_length]
                position += compressed_length
                if encoding == 1:
                    raw = zlib.decompress(raw)
                value = {
                    "array_type": property_type,
                    "length": length,
                    "raw": raw,
                    "format": {"f": "f", "d": "d", "i": "i", "l": "q", "b": "?", "c": "b"}[property_type],
                }
            else:
                raise ValueError(f"Unsupported FBX property type {property_type!r} in {name!r}")
            properties.append(value)

        self.position = position
        children = []
        null_record_length = 25 if wide else 13
        while self.position < end - null_record_length:
            child = self.read_node()
            if child is None:
                break
            children.append(child)
        self.position = end
        return {"name": name, "properties": properties, "children": children}


def walk(node):
    yield node
    for child in node["children"]:
        yield from walk(child)


def analyze(path):
    data = path.read_bytes()
    if not data.startswith(b"Kaydara FBX Binary"):
        raise ValueError("Only binary FBX files are supported")
    reader = FbxBinaryReader(data)
    roots = []
    while reader.position < len(data) - 160:
        node = reader.read_node()
        if node is None:
            break
        roots.append(node)
    nodes = [node for root in roots for node in walk(root)]

    geometries = []
    for node in nodes:
        if node["name"] != "Geometry":
            continue
        geometry = {"name": "", "vertices": 0, "polygon_indices": 0, "polygons": 0, "triangles": 0}
        if len(node["properties"]) > 1 and isinstance(node["properties"][1], str):
            geometry["name"] = node["properties"][1]
        for child in node["children"]:
            if not child["properties"] or not isinstance(child["properties"][0], dict):
                continue
            array = child["properties"][0]
            if child["name"] == "Vertices":
                geometry["vertices"] = array["length"] // 3
            elif child["name"] == "PolygonVertexIndex":
                geometry["polygon_indices"] = array["length"]
                values = struct.unpack("<" + array["format"] * array["length"], array["raw"])
                polygon_lengths = []
                polygon_length = 0
                for value in values:
                    polygon_length += 1
                    if value < 0:
                        polygon_lengths.append(polygon_length)
                        polygon_length = 0
                geometry["polygons"] = len(polygon_lengths)
                geometry["triangles"] = sum(max(0, length - 2) for length in polygon_lengths)
        if geometry["vertices"] or geometry["polygon_indices"]:
            geometries.append(geometry)

    embedded_media_bytes = 0
    for node in nodes:
        if node["name"] != "Video":
            continue
        for child in node["children"]:
            if child["name"] == "Content" and child["properties"]:
                content = child["properties"][0]
                if isinstance(content, dict):
                    embedded_media_bytes += content.get("raw_bytes", content.get("length", 0))
                elif isinstance(content, str):
                    embedded_media_bytes += len(content)

    return {
        "file": path.name,
        "bytes": len(data),
        "fbx_version": reader.version,
        "vertices": sum(item["vertices"] for item in geometries),
        "polygon_indices": sum(item["polygon_indices"] for item in geometries),
        "polygons": sum(item["polygons"] for item in geometries),
        "triangles": sum(item["triangles"] for item in geometries),
        "geometries": len(geometries),
        "models": sum(node["name"] == "Model" for node in nodes),
        "materials": sum(node["name"] == "Material" for node in nodes),
        "textures": sum(node["name"] == "Texture" for node in nodes),
        "embedded_media_bytes": embedded_media_bytes,
        "deformers": sum(node["name"] == "Deformer" for node in nodes),
        "animation_stacks": sum(node["name"] == "AnimationStack" for node in nodes),
        "top_geometries": sorted(geometries, key=lambda item: item["triangles"], reverse=True)[:8],
    }


if __name__ == "__main__":
    print(json.dumps([analyze(Path(item)) for item in sys.argv[1:]], indent=2, ensure_ascii=False))
