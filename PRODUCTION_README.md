# VR Web Demo Production README

This folder is the working package for the desktop-web VR interaction demo.

## Key Documents

- `docs/10_day_schedule.md`: daily production plan
- `docs/interaction_flow.md`: player flow, camera flow, interaction states
- `docs/model_list.md`: model and texture asset requirements
- `docs/recording_checklist.md`: recording and AE checklist

## Asset Folders

- `references/`: put concept images, screenshots, layout notes, and visual references here
- `models/`: put exported `.glb`, `.gltf`, `.blend`, or backup model files here
- `textures/`: put external texture files here if they are not packed into the GLB

## Recommended Workflow

1. Finish `docs/interaction_flow.md`.
2. Gather visual references in `references/`.
3. Build or generate low-poly models in Blender.
4. Export GLB files into `models/`.
5. Add textures into `textures/` only if they are not packed into GLB.
6. Use Three.js to load models and implement the interaction flow.
7. Record browser interaction.
8. Polish the recorded video in AE or editing software.

## Blender Export Target

Preferred file:

```text
models/sky_island_scene.glb
```

Optional:

```text
models/hands.glb
textures/
```

Do not rely on Blender render images as the main asset. Render images are useful references, but the interactive website needs actual 3D model files.
