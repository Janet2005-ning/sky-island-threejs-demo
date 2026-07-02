# 3D Model and Asset List

## Preferred Delivery Format

- Best format for the web: `GLB`
- Acceptable backup: `GLTF + textures`
- Avoid as primary format: `OBJ`, unless no other export is possible
- Optional source backup: `.blend`

## Scene Models

| Asset | Priority | Recommended File | Notes |
| --- | --- | --- | --- |
| Full scene blockout | Required | `sky_island_scene.glb` | Can include all islands and props for first pass |
| Main island | Required | `main_island.glb` | Largest central island with grass top and orange cliff |
| Left island | Required | `left_island.glb` | Separate small island with pot/flower feature |
| Right connector island | Required | `right_connector_island.glb` | Smaller low island between main and far-right island |
| Far-right island | Required | `right_bridge_island.glb` | Island with orange U-shaped bridge |
| Stone ring | Required | `stone_ring.glb` | Separate object if it needs click/highlight later |
| Pot | Required | `pot.glb` | Orange clay pot, one or more variants |
| Bridge / path pieces | Required | `bridge_pieces.glb` | Needed for expression path feedback |
| Expression blocks | Required | `expression_blocks.glb` | Claim, Evidence, Reasoning as separate named objects |
| Flowers and grass | Nice to have | `plants.glb` | Can be simplified or instanced in Three.js |
| Clouds | Nice to have | `clouds.glb` | Can also be procedural geometry |
| Reward card | Required | `reward_card.glb` | Or use HTML/Three.js plane card |
| VR hands | Required for VR feel | `hands.glb` | Left and right hand, simple stylized shapes are enough |

## Object Naming Rules

Use clear object names in Blender before export:

- `Main_Island`
- `Left_Island`
- `Right_Connector_Island`
- `Right_Bridge_Island`
- `Stone_Ring`
- `Pot_01`
- `Pot_02`
- `Block_Claim`
- `Block_Evidence`
- `Block_Reasoning`
- `Reward_Card`
- `Hand_Left`
- `Hand_Right`

## Material Palette

| Surface | Color Direction |
| --- | --- |
| Grass | warm yellow / golden grass |
| Cliff | orange clay / terracotta |
| Stone | pale peach / warm beige |
| Pot | saturated orange-red clay |
| Bridge | deeper orange wood/toy plastic |
| Plants | olive green leaves |
| Flowers | blue, white, pink accents |
| Clouds | cream peach |
| UI glow | cyan and gold |

## Texture Needs

For low-poly style, simple materials are acceptable. If using texture maps:

- `*_basecolor.png`: most important
- `*_normal.png`: optional
- `*_roughness.png`: optional
- `*_emissive.png`: optional for glowing UI or crystals

Recommended size:

- 1024px for small props
- 2048px for major island surfaces
- Keep final web model package under roughly 50 MB if possible

## Blender Export Checklist

- Apply transforms before export.
- Keep origin points sensible, especially for clickable objects.
- Delete hidden test objects.
- Use real object names, not `Cube.001`.
- Export as `glTF 2.0`.
- Format: `GLB`.
- Include materials and textures.
- If there are animations, include animations in export.
