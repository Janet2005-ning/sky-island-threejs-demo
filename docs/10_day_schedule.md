# 10 Day Production Schedule

Each day assumes about 10 focused working hours.

## Day 1 - Interaction Flow

- Write the complete game theme and player goal.
- Finish `interaction_flow.md`.
- Define every clickable object and feedback state.
- Decide the final completion moment.

Deliverables:

- `docs/interaction_flow.md`
- first asset checklist
- camera list

## Day 2 - Visual References and Asset Breakdown

- Collect all current 2.5D reference images.
- Mark each scene component: islands, bridge, pots, stones, plants, clouds, hands, UI props.
- Decide which assets must be real models and which can stay procedural.

Deliverables:

- `references/`
- `docs/model_list.md`
- rough scene layout sketch

## Day 3 - Basic 3D Models

- Build or generate low-poly blockout models.
- Focus on proportion and placement, not final detail.
- Finish main island, left island, right islands, bridge, pot, stones.

Deliverables:

- first `.blend`
- first `GLB`

## Day 4 - Materials and GLB Export

- Add base materials in Blender.
- Name objects clearly.
- Clean unused objects.
- Export `sky_island_scene.glb`.

Deliverables:

- `models/sky_island_scene.glb`
- optional `models/hands.glb`
- optional `textures/`

## Day 5 - Three.js Scene Import

- Load GLB models in Three.js.
- Set camera, lighting, shadows, and background.
- Match scene scale and composition.
- Add basic mouse-look.

Deliverable:

- web page shows the full 3D scene.

## Day 6 - Camera Motion

- Implement overview camera.
- Implement first-person camera.
- Add curved one-shot camera transition.
- Tune FOV, speed, and target points.

Deliverable:

- overview to first-person transition is recordable.

## Day 7 - Core Interactions

- Add raycast clicking.
- Add hover highlights.
- Add block selection.
- Add correct/incorrect state logic.
- Add snap-to-slot animation.

Deliverable:

- core mini-game can be completed.

## Day 8 - VR Hands and UI

- Add stylized VR hands.
- Make hands follow mouse movement.
- Add click/grab pose animation.
- Add task hints and success feedback.

Deliverable:

- browser demo feels like a VR interaction preview.

## Day 9 - Testing and Recording Prep

- Test full flow repeatedly.
- Fix camera discomfort, UI blocking, click accuracy, and performance.
- Hide debug UI.
- Prepare recording route.

Deliverable:

- final web version ready to record.

## Day 10 - Recording and AE Polish

- Record full-flow take.
- Record close-up take.
- Record transition-only take.
- Add sound, glow, UI details, subtitles, and timing polish in AE/editing software.

Deliverable:

- final portfolio demo video.
