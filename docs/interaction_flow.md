# VR Web Demo Interaction Flow

## Project

- Name: VR classroom expression training demo
- Platform: desktop web
- Interaction style: mouse simulates VR head direction and hand interaction
- Final use: record the browser interaction, then polish in AE or editing software

## Core Goal

The player enters a toy-like floating island training space and completes a short expression-building task. The demo should feel like a VR game preview even though it runs in a normal browser.

## Player Flow

### Step 01 - Overview Map

- Visual: wide floating-island map with a left island, central main island, and two right-side connected islands.
- Player action: move mouse to look around the scene.
- Trigger: left-click the main island area.
- Feedback: camera flies along a smooth arc into first-person view.
- Next: first-person training view.

### Step 02 - First-Person Arrival

- Visual: player stands near the main island; stone ring, pots, flowers, and bridge pieces are visible.
- Player action: move mouse to look around.
- Feedback: simulated VR hands appear at the lower screen area and subtly follow the cursor.
- Next: expression block selection.

### Step 03 - Choose Expression Blocks

- Visual: Claim, Evidence, and Reasoning blocks appear as floating toy objects.
- Player action: hover over a block.
- Feedback: block highlights with cyan glow; hand pose changes to ready-to-grab.
- Trigger: click the correct block.
- Feedback: block pops upward, then flies into the bridge/path slot.
- Next: repeat until the required sequence is complete.

### Step 04 - Correct / Incorrect Feedback

- Correct sequence: Claim -> Evidence -> Reasoning.
- Correct feedback: selected block snaps into place, bridge slot glows gold.
- Incorrect feedback: block shakes, red-orange warning flash appears, block returns to hover position.

### Step 05 - Completion

- Completion condition: all required blocks are placed in the correct order.
- Visual: bridge or path lights up; island elements glow softly.
- Feedback: reward card appears, for example "Deep Builder".
- End state: camera pulls back slightly for a clean hero shot suitable for recording.

## Interactive Objects

| Object | Default State | Hover State | Click State | Completion State |
| --- | --- | --- | --- | --- |
| Main island | visible from overview | subtle outline | starts camera flight | becomes first-person stage |
| Claim block | floating | cyan glow | flies to slot 1 | gold locked state |
| Evidence block | floating | cyan glow | flies to slot 2 | gold locked state |
| Reasoning block | floating | cyan glow | flies to slot 3 | gold locked state |
| Pot | decorative | slight glow | small wobble / particles | unchanged |
| Reward card | hidden | none | appears after completion | floats in front of player |
| VR hands | lower screen | aim pose | grab/click pose | relaxed pose |

## Camera List

| Camera | Purpose | Trigger | Motion |
| --- | --- | --- | --- |
| Overview camera | show full island map | page load | mouse orbit only |
| Fly-in camera | transition into VR training | click main island | 2 second curved one-shot move |
| First-person camera | simulate VR headset view | after fly-in | mouse-look with limited head movement |
| Completion camera | record-friendly ending shot | task complete | slight pullback and center on reward |

## UI Text

- Overview hint: `Left-click to enter the island`
- First-person hint: `Choose the expression blocks in order`
- Correct feedback: `Great structure`
- Incorrect feedback: `Try a clearer order`
- Completion text: `Frame Card unlocked: Deep Builder`

## Recording Notes

- Keep debug UI hidden for final capture.
- Use a 16:9 browser window for the main recording.
- Record several takes: full flow, close-up interactions, and transition shots.
