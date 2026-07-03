import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { createCardRewardSystem } from "./card-reward.js";

const app = document.querySelector("#app");
const loaderStatus = document.querySelector("#loader-status");
const modeLabel = document.querySelector("#mode-label");
const browseButton = document.querySelector("#browse-mode");
const roamButton = document.querySelector("#roam-mode");
const fountainButton = document.querySelector("#fountain-animation");
const resetButton = document.querySelector("#reset-camera");
const movePad = document.querySelector("#move-pad");
const moveButtons = Array.from(document.querySelectorAll("[data-move]"));
const bridgePanel = document.querySelector("#bridge-puzzle-panel");
const bridgeProgress = document.querySelector("#bridge-progress");
const bridgeMessage = document.querySelector("#bridge-message");
const vrHandHud = document.querySelector("#vr-hand-hud");
const vrLeftStatus = document.querySelector("#vr-left-status");
const vrRightStatus = document.querySelector("#vr-right-status");
const fountainStars = document.querySelector("#fountain-stars");
const fountainStarElements = Array.from(document.querySelectorAll(".fountain-star"));
const cardBackpack = document.querySelector("#card-backpack");
const bridgeDebugMode = new URLSearchParams(window.location.search).has("bridge-debug");
const roamDebugMode = new URLSearchParams(window.location.search).has("roam-debug");
const animalPreviewMode = new URLSearchParams(window.location.search).has("animals-preview");
let roamTestButton = null;
let roamBridgeTestButton = null;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xaeeaf0);
scene.fog = new THREE.Fog(0xaeeaf0, 14, 34);

const camera = new THREE.PerspectiveCamera(52, window.innerWidth / window.innerHeight, 0.05, 90);
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  powerPreference: "high-performance",
});
renderer.setSize(window.innerWidth, window.innerHeight);
const recordingFriendlyPixelRatio = Math.min(window.devicePixelRatio, 1);
renderer.setPixelRatio(recordingFriendlyPixelRatio);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.shadowMap.autoUpdate = false;
renderer.shadowMap.needsUpdate = true;
app.appendChild(renderer.domElement);
renderer.domElement.tabIndex = 0;
document.body.dataset.renderPixelRatio = recordingFriendlyPixelRatio.toFixed(2);
document.body.dataset.shadowUpdateMode = "on-demand";

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.enablePan = false;
controls.minDistance = 4.6;
controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.48;
controls.target.set(0.8, 0.2, 0.05);

const clock = new THREE.Clock();
const frameMetrics = {
  samples: [],
  maxSamples: 240,
  framesSincePublish: 0,
};
const modelRoot = new THREE.Group();
const lowAnimalDefinitions = [
  { id: "bear", rootName: "ANIMAL_BEAR_ROOT", url: "/models/animals/low_bear.glb", yaw: 0, tint: [1.08, 1.07, 1.08] },
  { id: "cat", rootName: "ANIMAL_CAT_ROOT", url: "/models/animals/low_cat.glb", yaw: 0, tint: [1.08, 1.07, 1.1] },
  { id: "duck", rootName: "ANIMAL_DUCK_ROOT", url: "/models/animals/low_duck.glb", yaw: 0, tint: [1.28, 1.22, 0.88] },
  { id: "frog", rootName: "ANIMAL_FROG_ROOT", url: "/models/animals/low_frog.glb", yaw: 0, tint: [1.08, 1.18, 1.1] },
];

function getFramePerformance() {
  const sortedFrameTimes = [...frameMetrics.samples].sort((a, b) => a - b);
  const averageFrameMs = frameMetrics.samples.length
    ? frameMetrics.samples.reduce((sum, value) => sum + value, 0) / frameMetrics.samples.length
    : 0;
  return {
    sampleCount: frameMetrics.samples.length,
    averageFps: averageFrameMs ? 1000 / averageFrameMs : 0,
    averageFrameMs,
    p95FrameMs: sortedFrameTimes[Math.floor(sortedFrameTimes.length * 0.95)] || 0,
    maxFrameMs: sortedFrameTimes.at(-1) || 0,
    drawCalls: renderer.info.render.calls,
    triangles: renderer.info.render.triangles,
    geometries: renderer.info.memory.geometries,
    textures: renderer.info.memory.textures,
  };
}
const keys = new Set();
const pressedPadKeys = new Set();
function keyIsActive(code) {
  return keys.has(code) || pressedPadKeys.has(code);
}
const pointerState = {
  active: false,
  id: null,
  button: null,
  x: 0,
  y: 0,
  startX: 0,
  startY: 0,
  moved: false,
};
const player = {
  position: new THREE.Vector3(10.7, 1.05, 3.55),
  yaw: 1.58,
  pitch: 0.1,
  speed: 2.35,
  eyeHeight: 0.92,
  groundY: 0.13,
  groundName: "",
  maxStepHeight: 0.46,
  maxDropHeight: 0.58,
  verticalFollow: 13,
};
const playerForward = new THREE.Vector3();
const playerRight = new THREE.Vector3();
const playerIntent = new THREE.Vector3();

const overviewCameraPreset = {
  position: new THREE.Vector3(4.1, 3.15, -7.35),
  target: new THREE.Vector3(4.1, 0.3, 4.0),
  fov: 50,
};

const roamCameraPreset = {
  position: new THREE.Vector3(10.7, 1.05, 3.55),
  yaw: 1.58,
  pitch: 0.1,
};

let mode = "browse";
let modelLoaded = false;
let modelBounds = new THREE.Box3();
let introDrift = 0;

const fountainSegments = [
  { id: "wake", label: "唤醒泉水", start: 0, end: 0.8 },
  { id: "water-column", label: "流出水柱", start: 0.8, end: 2.2 },
  { id: "water-spread", label: "水柱扩散", start: 2.2, end: 3.35 },
  { id: "pool-rise", label: "池水上涨", start: 3.35, end: 4.8 },
  { id: "lily-growth", label: "荷叶生长", start: 4.8, end: 7.0 },
  { id: "lotus-bud", label: "荷花花苞", start: 7.0, end: 8.6 },
  { id: "lotus-bloom", label: "荷花盛开", start: 8.6, end: 11.4 },
];

const fountainFx = {
  ready: false,
  playing: false,
  complete: false,
  startedInMode: null,
  elapsed: 0,
  duration: fountainSegments.at(-1).end,
  nextSegmentIndex: 0,
  activeSegmentIndex: -1,
  segmentEnd: 0,
  phase: "dry",
  waterProgress: 0,
  root: null,
  streamUpper: null,
  streamLower: null,
  water: null,
  ripples: [],
  pads: [],
  lotusPlatform: null,
  bud: null,
  bloomLayers: [],
  missing: [],
};

const fountainStarProgress = {
  active: false,
  dismissed: false,
  litCount: 0,
};

const fountainFocusPreset = {
  position: new THREE.Vector3(3.05, 3.0, -1.82),
  target: new THREE.Vector3(3.18, 0.56, 3.72),
  fov: 46,
};

const bridgeRaycaster = new THREE.Raycaster();
const bridgePointer = new THREE.Vector2();
const bridgeGroupDefinitions = [
  { id: 1, label: "蓝色桥面", representative: 1, members: [1] },
  { id: 2, label: "红色细长连接条", representative: 2, members: [2, 3, 4, 5] },
  { id: 3, label: "绿色桥面侧板", representative: 6, members: [6, 7] },
  { id: 4, label: "粉色桥柱", representative: 8, members: [8, 9] },
  { id: 5, label: "黄色桥头拱块", representative: 10, members: [10] },
  { id: 6, label: "橙色桥梁", representative: 11, members: [11, 12] },
];
const bridgeSelectionSequence = [1, 3, 4, 5, 6, 2];
const bridgeFloatingScaleFactor = 0.72;
const bridgeHeldApparentScaleFactor = 0.9;
const bridgeRepresentativeWorldStartOverrides = new Map([
  // Keep every group at the yellow arch's low eye-level height. From the
  // small-island roam start, z is the horizontal screen axis, so the pieces
  // form one spaced row while the required click order remains interleaved.
  [2, new THREE.Vector3(7.2, 1.78, 0.85)],
  [10, new THREE.Vector3(7.2, 1.6, 1.93)],
  [1, new THREE.Vector3(7.2, 1.42, 3.01)],
  [11, new THREE.Vector3(7.2, 1.72, 4.09)],
  [6, new THREE.Vector3(7.2, 1.66, 5.17)],
  [8, new THREE.Vector3(7.2, 1.6, 6.25)],
]);
const bridgePuzzle = {
  ready: false,
  pieces: [],
  groups: [],
  targets: new Map(),
  animations: [],
  hovered: null,
  complete: false,
  assembledCount: 0,
  nextSequenceIndex: 0,
  debugAutoSequence: false,
  missing: [],
};
const bridgeFloatRotation = new THREE.Quaternion();
const bridgeRejectRotation = new THREE.Quaternion();
const bridgeUpAxis = new THREE.Vector3(0, 1, 0);
const bridgeForwardAxis = new THREE.Vector3(0, 0, 1);

const vrInteraction = {
  ready: false,
  hands: [],
  fountainProxy: null,
  maxRayDistance: 14,
  rayDirection: new THREE.Vector3(),
  rayEnd: new THREE.Vector3(),
  raySource: new THREE.Vector3(),
  aimBox: new THREE.Box3(),
  aimBoxSize: new THREE.Vector3(),
  aimCandidatePoint: new THREE.Vector3(),
  aimHitPoint: new THREE.Vector3(),
  activeHandId: "",
  rayUpdateElapsed: 0,
  rayUpdateInterval: 1 / 30,
};

const groundCollision = {
  ready: false,
  islandMeshes: [],
  bridgeMeshes: [],
  raycaster: new THREE.Raycaster(),
  origin: new THREE.Vector3(),
  down: new THREE.Vector3(0, -1, 0),
  worldNormal: new THREE.Vector3(),
  lastSample: null,
};
groundCollision.raycaster.near = 0;
groundCollision.raycaster.far = 60;

const roamStairTest = {
  active: false,
  status: "idle",
  targetX: -1.62,
  targetZ: 4.07,
  transitions: [],
  edgeBlocked: null,
};

const roamBridgeTest = {
  active: false,
  status: "idle",
  targetX: 5.0,
  targetZ: 4.0,
  transitions: [],
};

scene.add(camera);
scene.add(modelRoot);
const cardReward = createCardRewardSystem({
  camera,
  backpackElement: cardBackpack,
});
window.__CARD_REWARD_STATE__ = () => cardReward.getState();

function setupLighting() {
  scene.add(new THREE.HemisphereLight(0xe9fcff, 0xe59f63, 2.25));

  const sun = new THREE.DirectionalLight(0xffefd1, 3.6);
  sun.position.set(-4.5, 8, 5.5);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.left = -9;
  sun.shadow.camera.right = 9;
  sun.shadow.camera.top = 7;
  sun.shadow.camera.bottom = -7;
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 24;
  scene.add(sun);

  const fill = new THREE.DirectionalLight(0x78e4ff, 0.9);
  fill.position.set(5, 3, -4);
  scene.add(fill);
}

function requestShadowRefresh() {
  renderer.shadowMap.needsUpdate = true;
}

const vrHandTextureLoader = new THREE.TextureLoader();

function loadVrHandTexture(url, side) {
  const texture = vrHandTextureLoader.load(url);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  texture.repeat.set(0.5, 1);
  texture.offset.set(side === "left" ? 0 : 0.5, 0);
  texture.needsUpdate = true;
  return texture;
}

function createVrHandMaterial(texture, opacity) {
  return new THREE.MeshBasicMaterial({
    map: texture,
    color: 0xffffff,
    transparent: true,
    opacity,
    alphaTest: 0.025,
    depthTest: false,
    depthWrite: false,
    fog: false,
    toneMapped: false,
    side: THREE.DoubleSide,
  });
}

function createVrHand(id, side, button, color, pointerX) {
  const sideSign = side === "left" ? -1 : 1;
  const group = new THREE.Group();
  group.name = `VR_${id.toUpperCase()}_HAND`;
  const basePosition = new THREE.Vector3(sideSign * 0.31, -0.2, -0.75);
  const cardPosition = new THREE.Vector3(sideSign * 0.47, -0.27, -0.67);
  group.position.copy(basePosition);
  camera.add(group);

  const handGeometry = new THREE.PlaneGeometry(0.33, 0.5);
  const openMaterial = createVrHandMaterial(
    loadVrHandTexture("/assets/vr-hands-open.png", side),
    0.72,
  );
  const gripMaterial = createVrHandMaterial(
    loadVrHandTexture("/assets/vr-hands-grip.png", side),
    0,
  );
  const openHand = new THREE.Mesh(handGeometry, openMaterial);
  const gripHand = new THREE.Mesh(handGeometry, gripMaterial);
  [openHand, gripHand].forEach((handPlane, index) => {
    handPlane.name = `VR_${id.toUpperCase()}_${index === 0 ? "OPEN" : "GRIP"}_TEXTURE`;
    handPlane.renderOrder = 96;
    handPlane.frustumCulled = false;
    group.add(handPlane);
  });
  gripHand.visible = false;

  const raySource = new THREE.Object3D();
  raySource.position.set(-sideSign * 0.067, 0.135, -0.025);
  group.add(raySource);

  const holdAnchor = new THREE.Group();
  holdAnchor.name = `VR_${id.toUpperCase()}_HOLD_ANCHOR`;
  holdAnchor.position.set(-sideSign * 0.083, 0.02, 0.045);
  group.add(holdAnchor);

  const rayGeometry = new LineGeometry();
  rayGeometry.setPositions([0, 0, 0, 0, 0, -1]);
  const rayMaterial = new LineMaterial({
    color,
    linewidth: 7,
    transparent: true,
    opacity: 0.9,
    depthTest: false,
    depthWrite: false,
    dashed: false,
    worldUnits: false,
  });
  rayMaterial.resolution.set(window.innerWidth, window.innerHeight);
  const rayLine = new Line2(rayGeometry, rayMaterial);
  rayLine.name = `VR_${id.toUpperCase()}_RAY`;
  rayLine.renderOrder = 95;
  rayLine.frustumCulled = false;
  scene.add(rayLine);

  return {
    id,
    side,
    button,
    color,
    group,
    basePosition,
    cardPosition,
    openHand,
    gripHand,
    openMaterial,
    gripMaterial,
    raySource,
    holdAnchor,
    rayLine,
    rayGeometry,
    rayMaterial,
    raycaster: new THREE.Raycaster(),
    pointer: new THREE.Vector2(pointerX, 0.04),
    pressed: false,
    moved: false,
    movement: 0,
    lastX: 0,
    lastY: 0,
    grip: 0,
    hoveredPiece: null,
    hitType: null,
    heldPiece: null,
    statusElement: vrHandHud?.querySelector(`[data-hand="${id}"]`) || null,
    statusText: id === "left" ? vrLeftStatus : vrRightStatus,
  };
}

function setupVrHands() {
  if (vrInteraction.ready) return;
  vrInteraction.hands = [
    createVrHand("left", "left", 0, 0x00baff, -0.2),
    createVrHand("right", "right", 2, 0x00baff, 0.2),
  ];
  vrInteraction.ready = true;
  setVrHandsVisible(false);
  window.__VR_HAND_STATE__ = getVrHandDebugState;
}

function setVrHandsVisible(visible) {
  vrInteraction.hands.forEach((hand) => {
    hand.group.visible = visible;
    hand.rayLine.visible = visible;
    if (!visible) hand.pressed = false;
  });
  if (!visible) {
    vrInteraction.activeHandId = "";
    pointerState.active = false;
    pointerState.id = null;
    pointerState.button = null;
    pointerState.moved = false;
  }
  document.body.dataset.vrHandsVisible = String(visible);
  document.body.dataset.vrMiddleViewActive = String(visible && pointerState.active);
}

function prepareVrFountainTarget(model) {
  if (vrInteraction.fountainProxy) vrInteraction.fountainProxy.removeFromParent();
  const material = new THREE.MeshBasicMaterial({
    color: 0x66eaff,
    transparent: true,
    opacity: 0,
    depthWrite: false,
    colorWrite: false,
  });
  const proxy = new THREE.Mesh(new THREE.BoxGeometry(2.45, 1.9, 2.15), material);
  proxy.name = "VR_FOUNTAIN_TARGET";
  proxy.position.set(4.02, 0.84, 3.74);
  proxy.userData.vrTarget = "fountain";
  proxy.castShadow = false;
  proxy.receiveShadow = false;
  model.add(proxy);
  vrInteraction.fountainProxy = proxy;
}

function getVrHandByButton(button) {
  return vrInteraction.hands.find((hand) => hand.button === button) || null;
}

function isVrBridgePieceAvailable(piece) {
  const group = piece?.userData.bridgeGroup;
  return Boolean(
    piece &&
      group &&
      !group.assembled &&
      !group.animating &&
      !group.rejecting &&
      !group.heldByHand,
  );
}

function findVrAimHit(hand) {
  let bestType = null;
  let bestPiece = null;
  let bestDistance = Infinity;

  bridgePuzzle.groups.forEach((group) => {
    const piece = group.representative;
    if (!isVrBridgePieceAvailable(piece)) return;
    vrInteraction.aimBox.setFromObject(piece);
    vrInteraction.aimBox.getSize(vrInteraction.aimBoxSize);
    const maxDimension = Math.max(
      vrInteraction.aimBoxSize.x,
      vrInteraction.aimBoxSize.y,
      vrInteraction.aimBoxSize.z,
    );
    const padding = THREE.MathUtils.clamp(maxDimension * 0.09, 0.065, 0.16);
    vrInteraction.aimBox.expandByScalar(padding);
    const point = hand.raycaster.ray.intersectBox(
      vrInteraction.aimBox,
      vrInteraction.aimCandidatePoint,
    );
    if (!point) return;
    const distance = hand.raycaster.ray.origin.distanceTo(point);
    if (distance > vrInteraction.maxRayDistance || distance >= bestDistance) return;
    bestType = "bridge";
    bestPiece = piece;
    bestDistance = distance;
    vrInteraction.aimHitPoint.copy(point);
  });

  if (vrInteraction.fountainProxy) {
    const fountainHit = hand.raycaster.intersectObject(vrInteraction.fountainProxy, false)[0];
    if (fountainHit && fountainHit.distance < bestDistance) {
      bestType = "fountain";
      bestPiece = null;
      bestDistance = fountainHit.distance;
      vrInteraction.aimHitPoint.copy(fountainHit.point);
    }
  }

  const rewardHit = cardReward.findHit(hand.raycaster);
  if (rewardHit && rewardHit.distance < bestDistance) {
    bestType = "reward-card";
    bestPiece = rewardHit.piece;
    bestDistance = rewardHit.distance;
    vrInteraction.aimHitPoint.copy(rewardHit.point);
  }

  return bestType
    ? {
        type: bestType,
        piece: bestPiece,
        distance: bestDistance,
        point: vrInteraction.aimHitPoint,
      }
    : null;
}

function updateVrHandRay(hand, matrixWorldReady = false) {
  if (!hand || mode !== "roam") return;
  if (!matrixWorldReady) scene.updateMatrixWorld(true);
  hand.raySource.getWorldPosition(vrInteraction.raySource);
  hand.raycaster.setFromCamera(hand.pointer, camera);
  hand.raycaster.near = 0;
  hand.raycaster.far = vrInteraction.maxRayDistance;

  const hit = findVrAimHit(hand);
  hand.hoveredPiece = null;
  hand.hitType = null;

  if (hit?.type === "reward-card") {
    hand.hitType = "reward-card";
  } else if (hit?.type === "fountain") {
    hand.hitType = "fountain";
  } else if (hit?.type === "bridge" && isVrBridgePieceAvailable(hit.piece)) {
    hand.hitType = "bridge";
    hand.hoveredPiece = hit.piece;
  }

  if (hit) vrInteraction.rayEnd.copy(hit.point);
  else hand.raycaster.ray.at(vrInteraction.maxRayDistance, vrInteraction.rayEnd);
  hand.rayGeometry.setPositions([
    vrInteraction.raySource.x,
    vrInteraction.raySource.y,
    vrInteraction.raySource.z,
    vrInteraction.rayEnd.x,
    vrInteraction.rayEnd.y,
    vrInteraction.rayEnd.z,
  ]);
  const rayColor = hand.heldPiece
    ? 0x83f0bd
    : hand.hitType === "reward-card"
      ? 0xffd35c
      : hand.hitType === "fountain"
      ? 0x6ee9ff
      : hand.hoveredPiece
        ? 0xffd35c
        : hand.color;
  hand.rayMaterial.color.setHex(rayColor);
  hand.rayMaterial.opacity = hand.pressed ? 1 : 0.94;
  hand.rayMaterial.linewidth = hand.pressed ? 9 : 7;
}

function updateVrHighlights() {
  const highlighted = new Set();
  vrInteraction.hands.forEach((hand) => {
    if (hand.hoveredPiece) highlighted.add(hand.hoveredPiece);
  });
  bridgePuzzle.groups.forEach((group) => {
    if (!group.representative || group.heldByHand) return;
    setBridgePieceHighlight(group.representative, highlighted.has(group.representative));
  });
  cardReward.setHovered(vrInteraction.hands.some((hand) => hand.hitType === "reward-card"));
}

function getVrHandStatus(hand) {
  if (hand.heldPiece) return ["held", `持有${hand.heldPiece.userData.bridgeGroup?.label || "积木"} · 再点归桥`];
  if (hand.hitType === "reward-card") return ["reward-card", "Card01"];
  if (hand.hitType === "fountain") {
    const next = fountainSegments[fountainFx.nextSegmentIndex]?.label || "重新唤醒";
    return ["fountain", `泉水 · 点击${next}`];
  }
  if (hand.hoveredPiece) return ["target", `瞄准${hand.hoveredPiece.userData.bridgeGroup?.label || "积木"} · 点击抓取`];
  if (hand.pressed) return ["idle", "正在控制射线与视角"];
  return ["idle", "按住移动射线"];
}

function updateVrHandHud(hand) {
  const [state, text] = getVrHandStatus(hand);
  const handDatasetPrefix = `vr${hand.id === "left" ? "Left" : "Right"}`;
  const idleRayColor = `#${hand.color.toString(16).padStart(6, "0")}`;
  if (hand.statusElement) hand.statusElement.dataset.state = state;
  if (hand.statusText) hand.statusText.textContent = text;
  document.body.dataset[`${handDatasetPrefix}State`] = state;
  document.body.dataset[`${handDatasetPrefix}Target`] =
    hand.hitType === "reward-card"
      ? "Card01"
      : hand.hitType === "fountain"
        ? "fountain"
        : hand.hoveredPiece?.userData.bridgeGroup?.label || "";
  document.body.dataset[`${handDatasetPrefix}RayColor`] = `#${hand.rayMaterial.color.getHexString()}`;
  document.body.dataset[`${handDatasetPrefix}IdleRayColor`] = idleRayColor;
}

function updateVrHands(delta) {
  if (!vrInteraction.ready) return;
  const visible = mode === "roam";
  vrInteraction.rayUpdateElapsed += delta;
  const shouldRefreshAim = visible && vrInteraction.rayUpdateElapsed >= vrInteraction.rayUpdateInterval;
  if (shouldRefreshAim) {
    vrInteraction.rayUpdateElapsed %= vrInteraction.rayUpdateInterval;
    scene.updateMatrixWorld(true);
  }
  const cardState = cardReward.getState();
  const cardPresentationActive =
    cardState.triggered && !cardState.collected && cardState.phase !== "idle";
  vrInteraction.hands.forEach((hand) => {
    const handTargetPosition = cardPresentationActive ? hand.cardPosition : hand.basePosition;
    hand.group.position.x = THREE.MathUtils.damp(hand.group.position.x, handTargetPosition.x, 12, delta);
    hand.group.position.y = THREE.MathUtils.damp(hand.group.position.y, handTargetPosition.y, 12, delta);
    hand.group.position.z = THREE.MathUtils.damp(hand.group.position.z, handTargetPosition.z, 12, delta);
    const gripTarget = hand.pressed || hand.heldPiece ? 1 : 0;
    hand.grip = THREE.MathUtils.damp(hand.grip, gripTarget, 18, delta);
    const gripOpacity = (hand.heldPiece ? 0.56 : 0.7) * hand.grip;
    hand.openMaterial.opacity = 0.72 * (1 - hand.grip);
    hand.gripMaterial.opacity = gripOpacity;
    hand.openHand.visible = visible && hand.openMaterial.opacity > 0.015;
    hand.gripHand.visible = visible && hand.gripMaterial.opacity > 0.015;
    hand.group.visible = visible;
    hand.rayLine.visible = visible;
    if (shouldRefreshAim) updateVrHandRay(hand, true);
    if (shouldRefreshAim || !visible) updateVrHandHud(hand);
  });
  if (shouldRefreshAim) {
    updateVrHighlights();
    document.body.dataset.vrActiveHand = vrInteraction.activeHandId;
    document.body.dataset.vrViewFollowsRay = "true";
  }
}

function getVrHandDebugState() {
  return {
    ready: vrInteraction.ready,
    visible: mode === "roam",
    activeHand: vrInteraction.activeHandId || null,
    middleViewActive: pointerState.active,
    fountainTargetReady: Boolean(vrInteraction.fountainProxy),
    hands: vrInteraction.hands.map((hand) => ({
      id: hand.id,
      button: hand.button,
      pointer: hand.pointer.toArray().map((value) => Number(value.toFixed(3))),
      pressed: hand.pressed,
      moved: hand.moved,
      movement: Number(hand.movement.toFixed(2)),
      visualState: hand.grip > 0.5 ? "grip" : "open",
      rayColor: `#${hand.rayMaterial.color.getHexString()}`,
      idleRayColor: `#${hand.color.toString(16).padStart(6, "0")}`,
      hitType: hand.hitType,
      hoveredGroup: hand.hoveredPiece?.userData.bridgeGroupId ?? null,
      heldGroup: hand.heldPiece?.userData.bridgeGroupId ?? null,
    })),
  };
}

function clamp01(value) {
  return THREE.MathUtils.clamp(value, 0, 1);
}

function rangeProgress(time, start, end) {
  return clamp01((time - start) / (end - start));
}

function easeInOutCubic(value) {
  const t = clamp01(value);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) * 0.5;
}

function easeOutBack(value) {
  const t = clamp01(value);
  const c1 = 1.35;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

function rememberFxTransform(object) {
  if (!object || object.userData.fxBaseScale) return;
  object.userData.fxBaseScale = object.scale.clone();
  object.userData.fxBasePosition = object.position.clone();
  object.userData.fxBaseRotation = object.rotation.clone();
}

function cloneFxMaterials(root) {
  root.traverse((child) => {
    if (!child.isMesh || !child.material) return;
    const sourceMaterials = Array.isArray(child.material) ? child.material : [child.material];
    const clonedMaterials = sourceMaterials.map((source) => {
      const material = source.clone();
      material.transparent = true;
      material.side = THREE.DoubleSide;
      material.userData.fxBaseOpacity = source.opacity;
      const isWater = child.name.includes("Water") || material.name.includes("Water");
      material.depthWrite = !isWater;
      material.needsUpdate = true;
      return material;
    });
    child.material = Array.isArray(child.material) ? clonedMaterials : clonedMaterials[0];
    child.renderOrder = child.name.includes("Water") ? 4 : 5;
  });
}

function setFxOpacity(object, opacity) {
  if (!object) return;
  const factor = clamp01(opacity);
  object.traverse((child) => {
    if (!child.isMesh || !child.material) return;
    child.userData.fxOpacityFactor = factor;
    const materials = Array.isArray(child.material) ? child.material : [child.material];
    materials.forEach((material) => {
      const baseOpacity = material.userData.fxBaseOpacity ?? 1;
      material.opacity = baseOpacity * factor;
    });
  });
}

function setFxPresence(object, progress, scaleProgress = progress) {
  if (!object) return;
  rememberFxTransform(object);
  const opacity = clamp01(progress);
  object.visible = opacity > 0.002;
  const scale = Math.max(0.001, scaleProgress);
  object.scale.copy(object.userData.fxBaseScale).multiplyScalar(scale);
  setFxOpacity(object, opacity);
}

function setStreamProgress(stream, progress) {
  if (!stream) return;
  const normalized = clamp01(progress);
  stream.visible = normalized > 0.002;
  const segments = stream.children.filter((child) => child.isMesh);
  segments.forEach((segment, index) => {
    const segmentProgress = clamp01(normalized * segments.length - index);
    segment.visible = segmentProgress > 0.002;
    setFxOpacity(segment, segmentProgress);
  });
}

function setFountainButtonState(state, label) {
  if (!fountainButton) return;
  fountainButton.dataset.state = state;
  fountainButton.textContent = state === "complete" ? "✿" : "♒";
  fountainButton.setAttribute("aria-label", label);
}

function getFountainSegmentButtonLabel(index) {
  const segment = fountainSegments[index];
  return segment ? `${index + 1}/7 ${segment.label}` : "已完成 · 重新唤醒";
}

function syncFountainSegmentDataset() {
  const active = fountainSegments[fountainFx.activeSegmentIndex] || null;
  const next = fountainSegments[fountainFx.nextSegmentIndex] || null;
  document.body.dataset.fountainSegmentCount = String(fountainSegments.length);
  document.body.dataset.fountainSegments = JSON.stringify(
    fountainSegments.map(({ id, label, start, end }) => ({ id, label, start, end })),
  );
  document.body.dataset.fountainCompletedSegments = String(fountainFx.nextSegmentIndex);
  document.body.dataset.fountainActiveSegment = active?.label || "";
  document.body.dataset.fountainNextSegment = next?.label || "";
  document.body.dataset.fountainAwaitingInput = String(
    fountainFx.ready && !fountainFx.playing && !fountainFx.complete,
  );
}

function syncFountainStarProgress() {
  const visible =
    mode === "roam" && fountainStarProgress.active && !fountainStarProgress.dismissed;
  fountainStars?.classList.toggle("is-visible", visible);
  fountainStars?.setAttribute("aria-hidden", String(!visible));
  fountainStarElements.forEach((star, index) => {
    star.classList.toggle("is-lit", index < fountainStarProgress.litCount);
  });
  document.body.dataset.fountainStarsVisible = String(visible);
  document.body.dataset.fountainStarsLit = String(fountainStarProgress.litCount);
  document.body.dataset.fountainStarsDismissed = String(fountainStarProgress.dismissed);
}

function registerRoamFountainClick(segmentIndex) {
  if (mode !== "roam") return;
  if (segmentIndex === 0) {
    fountainStarProgress.active = true;
    fountainStarProgress.dismissed = false;
    fountainStarProgress.litCount = 0;
  } else if (!fountainStarProgress.dismissed) {
    fountainStarProgress.active = true;
    fountainStarProgress.litCount = Math.min(fountainStarElements.length, segmentIndex);
  }
  syncFountainStarProgress();
}

function dismissFountainStarsOnStairs() {
  if (
    fountainStarProgress.active &&
    !fountainStarProgress.dismissed &&
    player.groundName.includes("stair_terrace")
  ) {
    fountainStarProgress.active = false;
    fountainStarProgress.dismissed = true;
    syncFountainStarProgress();
  }
}

function resetFountainVisuals() {
  setStreamProgress(fountainFx.streamUpper, 0);
  setStreamProgress(fountainFx.streamLower, 0);
  setFxPresence(fountainFx.water, 0, 0.04);
  fountainFx.ripples.forEach((ripple) => setFxPresence(ripple, 0, 0.2));
  fountainFx.pads.forEach((pad) => setFxPresence(pad, 0, 0.01));
  setFxPresence(fountainFx.lotusPlatform, 0, 0.01);
  setFxPresence(fountainFx.bud, 0, 0.01);
  fountainFx.bloomLayers.forEach((layer) => setFxPresence(layer, 0, 0.01));
  fountainFx.waterProgress = 0;
  fountainFx.phase = "dry";
  document.body.dataset.fountainPhase = "dry";
  document.body.dataset.fountainElapsed = "0.000";
}

function prepareFountainAnimation(model) {
  const find = (name) => model.getObjectByName(name);
  fountainFx.root = find("FX_Fountain_Animation");
  fountainFx.streamUpper = find("FX_Water_Stream_Upper");
  fountainFx.streamLower = find("FX_Water_Stream_Lower");
  fountainFx.water = find("FX_Pond_Water");
  fountainFx.ripples = [find("FX_Water_Ripple_Inner"), find("FX_Water_Ripple_Outer")].filter(Boolean);
  fountainFx.pads = Array.from({ length: 7 }, (_, index) => find(`FX_LilyPad_${String(index + 1).padStart(2, "0")}`)).filter(Boolean);
  fountainFx.lotusPlatform = find("FX_Lotus_Platform_00");
  fountainFx.bud = find("FX_Lotus_Bud");
  fountainFx.bloomLayers = [
    find("FX_Lotus_Bloom_Outer"),
    find("FX_Lotus_Bloom_Middle"),
    find("FX_Lotus_Bloom_Inner"),
    find("FX_Lotus_Bloom_Center"),
  ].filter(Boolean);

  const required = [
    ["root", fountainFx.root],
    ["upper stream", fountainFx.streamUpper],
    ["lower stream", fountainFx.streamLower],
    ["pond water", fountainFx.water],
    ["lotus platform", fountainFx.lotusPlatform],
    ["lotus bud", fountainFx.bud],
  ];
  if (fountainFx.pads.length !== 7) required.push(["seven lily pads", null]);
  if (fountainFx.bloomLayers.length !== 4) required.push(["four lotus layers", null]);
  fountainFx.missing = required.filter(([, object]) => !object).map(([label]) => label);
  fountainFx.ready = fountainFx.missing.length === 0;
  fountainFx.playing = false;
  fountainFx.complete = false;
  fountainFx.elapsed = 0;
  fountainFx.nextSegmentIndex = 0;
  fountainFx.activeSegmentIndex = -1;
  fountainFx.segmentEnd = 0;

  if (fountainFx.root) {
    fountainFx.root.visible = true;
    fountainFx.root.traverse((child) => {
      child.visible = true;
      rememberFxTransform(child);
    });
    cloneFxMaterials(fountainFx.root);
    resetFountainVisuals();
  }

  fountainButton.disabled = !fountainFx.ready;
  setFountainButtonState(
    fountainFx.ready ? "ready" : "error",
    fountainFx.ready ? getFountainSegmentButtonLabel(0) : "泉水组件缺失",
  );
  syncFountainSegmentDataset();
  window.__FOUNTAIN_STATE__ = getFountainDebugState;
  window.__FOUNTAIN_SEEK__ = seekFountainAnimation;

  if (!fountainFx.ready) {
    console.warn("Fountain animation components missing:", fountainFx.missing);
  }
}

function getFountainPhase(time) {
  const active = fountainSegments[fountainFx.activeSegmentIndex];
  if (active) return [active.id, active.label];
  const completedIndex = Math.max(0, fountainFx.nextSegmentIndex - 1);
  const completed = fountainSegments[completedIndex];
  if (time <= 0 || !completed) return ["dry", "唤醒泉水"];
  return [completed.id, completed.label];
}

function applyFountainTimeline(time) {
  const wakeProgress = easeInOutCubic(rangeProgress(time, 0.08, 0.8));
  const columnProgress = easeInOutCubic(rangeProgress(time, 0.8, 2.2));
  const upperStream = THREE.MathUtils.lerp(wakeProgress * 0.28, 1, columnProgress);
  const lowerStream = columnProgress;
  setStreamProgress(fountainFx.streamUpper, upperStream);
  setStreamProgress(fountainFx.streamLower, lowerStream);

  const spreadProgress = easeInOutCubic(rangeProgress(time, 2.2, 3.35));
  const riseProgress = easeInOutCubic(rangeProgress(time, 3.35, 4.8));
  const waterProgress = time < 3.35 ? spreadProgress * 0.45 : 0.45 + riseProgress * 0.55;
  const waterScale = time < 3.35
    ? THREE.MathUtils.lerp(0.04, 0.72, spreadProgress)
    : THREE.MathUtils.lerp(0.72, 1.22, riseProgress);
  fountainFx.waterProgress = waterProgress;
  setFxPresence(fountainFx.water, waterProgress, waterScale);
  fountainFx.ripples.forEach((ripple, index) => {
    const rippleProgress = easeInOutCubic(rangeProgress(time, 2.2 + index * 0.14, 3.08 + index * 0.14));
    setFxPresence(ripple, rippleProgress * waterProgress, 0.32 + rippleProgress * 0.68);
  });

  fountainFx.pads.forEach((pad, index) => {
    const raw = rangeProgress(time, 4.8 + index * 0.25, 5.62 + index * 0.25);
    setFxPresence(pad, raw, easeOutBack(raw));
  });

  const platformRaw = rangeProgress(time, 6.05, 7.0);
  setFxPresence(fountainFx.lotusPlatform, platformRaw, easeOutBack(platformRaw));

  const budIn = rangeProgress(time, 7.0, 8.45);
  const budOut = rangeProgress(time, 8.6, 9.65);
  const budOpacity = budIn * (1 - budOut);
  const budScale = easeOutBack(budIn) * THREE.MathUtils.lerp(0.6, 0.46, budOut);
  setFxPresence(fountainFx.bud, budOpacity, budScale);

  const layerStarts = [8.6, 9.12, 9.65, 10.18];
  fountainFx.bloomLayers.forEach((layer, index) => {
    const raw = rangeProgress(time, layerStarts[index], layerStarts[index] + 1.22);
    const scale = easeOutBack(raw);
    setFxPresence(layer, raw, scale);
    if (layer?.userData.fxBaseRotation) {
      layer.rotation.copy(layer.userData.fxBaseRotation);
      layer.rotation.y += (1 - raw) * (index % 2 ? -0.34 : 0.34);
    }
  });

  const [phase, label] = getFountainPhase(time);
  fountainFx.phase = phase;
  document.body.dataset.fountainPhase = phase;
  document.body.dataset.fountainElapsed = time.toFixed(3);
  if (fountainFx.playing) {
    setFountainButtonState("playing", getFountainSegmentButtonLabel(fountainFx.activeSegmentIndex));
  }
}

function animateFountainSurface(time) {
  if (!fountainFx.ready || fountainFx.waterProgress <= 0.02) return;
  const waterBase = fountainFx.water.userData.fxBasePosition;
  fountainFx.water.position.y = waterBase.y + Math.sin(time * 1.8) * 0.004;

  fountainFx.pads.forEach((pad, index) => {
    if (!pad.visible) return;
    const base = pad.userData.fxBasePosition;
    pad.position.y = base.y + Math.sin(time * 1.45 + index * 0.72) * 0.007;
    pad.rotation.y = pad.userData.fxBaseRotation.y + Math.sin(time * 0.42 + index) * 0.025;
  });

  fountainFx.ripples.forEach((ripple, index) => {
    if (!ripple.visible) return;
    const cycle = (time * 0.58 + index * 0.48) % 1;
    const base = ripple.userData.fxBaseScale;
    ripple.scale.copy(base).multiplyScalar(0.72 + cycle * 0.72);
    setFxOpacity(ripple, fountainFx.waterProgress * (1 - cycle));
  });

  [fountainFx.streamUpper, fountainFx.streamLower].forEach((stream, streamIndex) => {
    if (!stream?.visible) return;
    const segments = stream.children.filter((child) => child.isMesh && child.visible);
    segments.forEach((segment, segmentIndex) => {
      const shimmer = 0.84 + Math.sin(time * 7.5 - segmentIndex * 0.9 + streamIndex) * 0.16;
      segment.traverse((child) => {
        if (!child.isMesh || !child.material) return;
        const materials = Array.isArray(child.material) ? child.material : [child.material];
        materials.forEach((material) => {
          const baseOpacity = material.userData.fxBaseOpacity ?? 1;
          const factor = child.userData.fxOpacityFactor ?? 1;
          material.opacity = baseOpacity * factor * shimmer;
        });
      });
    });
  });
}

function focusFountainCamera() {
  if (mode !== "browse") return;
  camera.position.copy(fountainFocusPreset.position);
  camera.fov = fountainFocusPreset.fov;
  camera.updateProjectionMatrix();
  controls.target.copy(fountainFocusPreset.target);
  controls.update();
}

function startFountainAnimation() {
  if (!fountainFx.ready || fountainFx.playing) return;
  if (fountainFx.complete || fountainFx.nextSegmentIndex >= fountainSegments.length) {
    fountainFx.complete = false;
    fountainFx.elapsed = 0;
    fountainFx.nextSegmentIndex = 0;
    fountainFx.activeSegmentIndex = -1;
    resetFountainVisuals();
  }

  const segmentIndex = fountainFx.nextSegmentIndex;
  const segment = fountainSegments[segmentIndex];
  if (!segment) return;
  registerRoamFountainClick(segmentIndex);
  if (segmentIndex === 0) {
    fountainFx.elapsed = 0;
    resetFountainVisuals();
    focusFountainCamera();
  } else {
    fountainFx.elapsed = Math.max(fountainFx.elapsed, segment.start);
  }

  fountainFx.playing = true;
  fountainFx.complete = false;
  fountainFx.activeSegmentIndex = segmentIndex;
  fountainFx.segmentEnd = segment.end;
  fountainFx.startedInMode = mode;
  document.body.dataset.fountainPlaying = "true";
  document.body.dataset.fountainStartedMode = mode;
  applyFountainTimeline(fountainFx.elapsed);
  setFountainButtonState("playing", getFountainSegmentButtonLabel(segmentIndex));
  syncFountainSegmentDataset();
}

function completeFountainSegment() {
  const completedIndex = fountainFx.activeSegmentIndex;
  const segment = fountainSegments[completedIndex];
  if (!segment) return;
  fountainFx.playing = false;
  fountainFx.elapsed = segment.end;
  applyFountainTimeline(fountainFx.elapsed);
  fountainFx.nextSegmentIndex = completedIndex + 1;
  fountainFx.activeSegmentIndex = -1;
  document.body.dataset.fountainPlaying = "false";
  if (fountainFx.nextSegmentIndex >= fountainSegments.length) {
    fountainFx.complete = true;
    fountainFx.phase = "complete";
    document.body.dataset.fountainPhase = "complete";
    setFountainButtonState("complete", "已完成 · 重新唤醒");
  } else {
    fountainFx.complete = false;
    setFountainButtonState("ready", getFountainSegmentButtonLabel(fountainFx.nextSegmentIndex));
  }
  requestShadowRefresh();
  syncFountainSegmentDataset();
}

function seekFountainAnimation(seconds) {
  if (!fountainFx.ready) return getFountainDebugState();
  fountainFx.playing = false;
  document.body.dataset.fountainPlaying = "false";
  fountainFx.elapsed = THREE.MathUtils.clamp(Number(seconds) || 0, 0, fountainFx.duration);
  fountainFx.complete = fountainFx.elapsed >= fountainFx.duration;
  fountainFx.activeSegmentIndex = -1;
  fountainFx.nextSegmentIndex = fountainSegments.filter(
    (segment) => segment.end <= fountainFx.elapsed + 0.0001,
  ).length;
  fountainFx.segmentEnd = fountainFx.elapsed;
  applyFountainTimeline(fountainFx.elapsed);
  setFountainButtonState(
    fountainFx.complete ? "complete" : "ready",
    fountainFx.complete ? "已完成 · 重新唤醒" : getFountainSegmentButtonLabel(fountainFx.nextSegmentIndex),
  );
  syncFountainSegmentDataset();
  return getFountainDebugState();
}

function updateFountainAnimation(delta, time) {
  if (!fountainFx.ready) return;
  if (fountainFx.playing) {
    fountainFx.elapsed = Math.min(fountainFx.elapsed + delta, fountainFx.segmentEnd);
    applyFountainTimeline(fountainFx.elapsed);
    if (fountainFx.elapsed >= fountainFx.segmentEnd) completeFountainSegment();
  }
  animateFountainSurface(time);
}

function getFountainDebugState() {
  return {
    ready: fountainFx.ready,
    playing: fountainFx.playing,
    complete: fountainFx.complete,
    startedInMode: fountainFx.startedInMode,
    cameraMode: mode,
    elapsed: Number(fountainFx.elapsed.toFixed(3)),
    duration: fountainFx.duration,
    phase: fountainFx.phase,
    segmentCount: fountainSegments.length,
    completedSegmentCount: fountainFx.nextSegmentIndex,
    activeSegment: fountainSegments[fountainFx.activeSegmentIndex]?.label || null,
    nextSegment: fountainSegments[fountainFx.nextSegmentIndex]?.label || null,
    segments: fountainSegments.map((segment) => ({ ...segment })),
    missing: [...fountainFx.missing],
    streamCount: [fountainFx.streamUpper, fountainFx.streamLower].filter(Boolean).length,
    lilyPadCount: fountainFx.pads.length,
    bloomLayerCount: fountainFx.bloomLayers.length,
  };
}

function setBridgePanel(message, state = "ready") {
  if (bridgePanel) bridgePanel.dataset.state = state;
  if (bridgeMessage && message) bridgeMessage.textContent = message;
  if (bridgeProgress) bridgeProgress.textContent = `${bridgePuzzle.assembledCount} / ${bridgePuzzle.groups.length || 6}`;
  document.body.dataset.bridgeState = state;
  document.body.dataset.bridgeComplete = String(bridgePuzzle.complete);
  document.body.dataset.bridgeNextGroup = String(bridgeSelectionSequence[bridgePuzzle.nextSequenceIndex] || "");
}

function publishBridgeFloatingPositions() {
  if (!bridgePuzzle.groups.length) return;
  scene.updateMatrixWorld(true);
  const worldPosition = new THREE.Vector3();
  document.body.dataset.bridgeFloatingPositions = JSON.stringify(
    bridgePuzzle.groups.map((group) => {
      group.representative?.getWorldPosition(worldPosition);
      return {
        id: group.id,
        label: group.label,
        position: worldPosition.toArray().map((value) => Number(value.toFixed(3))),
      };
    }),
  );
}

function getExpectedBridgeGroup() {
  const expectedId = bridgeSelectionSequence[bridgePuzzle.nextSequenceIndex];
  return bridgePuzzle.groups.find((group) => group.id === expectedId) || null;
}

function getBridgeSequencePrompt() {
  const expected = getExpectedBridgeGroup();
  return expected
    ? `顺序：蓝 → 绿 → 粉 → 黄 → 橙 → 红；下一块：${expected.label}`
    : "桥梁搭建完成，现在可以走到对岸";
}

function cloneBridgeMaterials(piece) {
  const cloneMaterial = (material) => {
    const clone = material.clone();
    clone.userData.bridgeBaseEmissive = clone.emissive?.clone() || null;
    clone.userData.bridgeBaseEmissiveIntensity = clone.emissiveIntensity ?? 1;
    return clone;
  };

  if (Array.isArray(piece.material)) piece.material = piece.material.map(cloneMaterial);
  else if (piece.material) piece.material = cloneMaterial(piece.material);
}

function createBridgeErrorOutline(piece) {
  const outlineMaterial = new THREE.MeshBasicMaterial({
    color: 0xff2038,
    side: THREE.BackSide,
    transparent: true,
    opacity: 0,
    depthWrite: false,
    toneMapped: false,
  });
  const outline = new THREE.Mesh(piece.geometry, outlineMaterial);
  outline.name = `${piece.name}_Error_Outline`;
  outline.scale.setScalar(1.065);
  outline.visible = false;
  outline.castShadow = false;
  outline.receiveShadow = false;
  outline.renderOrder = 12;
  piece.add(outline);
  piece.userData.bridgeErrorOutline = outline;
}

function setBridgePieceErrorVisual(piece, active, opacity = 0.9) {
  if (!piece) return;
  const outline = piece.userData.bridgeErrorOutline;
  if (outline) {
    outline.visible = active;
    outline.material.opacity = active ? opacity : 0;
  }
  const materials = Array.isArray(piece.material) ? piece.material : [piece.material];
  materials.filter(Boolean).forEach((material) => {
    if (!material.emissive) return;
    if (active) {
      material.emissive.set(0xff1838);
      material.emissiveIntensity = 1.15;
    } else {
      material.emissive.copy(material.userData.bridgeBaseEmissive || new THREE.Color(0x000000));
      material.emissiveIntensity = material.userData.bridgeBaseEmissiveIntensity ?? 1;
    }
  });
}

function setBridgePieceHighlight(piece, highlighted) {
  if (!piece) return;
  if (piece.userData.bridgeRejecting) return;
  const materials = Array.isArray(piece.material) ? piece.material : [piece.material];
  materials.filter(Boolean).forEach((material) => {
    if (!material.emissive) return;
    const base = material.userData.bridgeBaseEmissive;
    if (highlighted) {
      material.emissive.set(0xffa928);
      material.emissiveIntensity = 0.8;
    } else {
      material.emissive.copy(base || new THREE.Color(0x000000));
      material.emissiveIntensity = material.userData.bridgeBaseEmissiveIntensity ?? 1;
    }
  });
}

function setHoveredBridgePiece(piece) {
  if (bridgePuzzle.hovered === piece) return;
  setBridgePieceHighlight(bridgePuzzle.hovered, false);
  bridgePuzzle.hovered = piece;
  setBridgePieceHighlight(piece, true);
  document.body.dataset.bridgeHover = String(Boolean(piece));
  document.body.dataset.bridgeHoverIndex = piece ? String(piece.userData.bridgeIndex) : "";
  document.body.dataset.bridgeHoverGroup = piece ? String(piece.userData.bridgeGroupId) : "";
}

function prepareBridgePuzzle(model) {
  const piecesByIndex = new Map();
  bridgePuzzle.targets.clear();
  bridgePuzzle.groups = [];
  bridgePuzzle.missing = [];

  model.traverse((object) => {
    const pieceMatch = object.name.match(/^BRIDGE_PIECE_(\d{2})$/);
    const targetMatch = object.name.match(/^BRIDGE_TARGET_(\d{2})$/);
    if (pieceMatch && object.isMesh) piecesByIndex.set(Number(pieceMatch[1]), object);
    if (targetMatch) bridgePuzzle.targets.set(Number(targetMatch[1]), object);
  });

  bridgePuzzle.pieces = Array.from(piecesByIndex.entries())
    .sort(([a], [b]) => a - b)
    .map(([index, piece]) => {
      const target = bridgePuzzle.targets.get(index);
      if (!target) {
        bridgePuzzle.missing.push(`BRIDGE_TARGET_${String(index).padStart(2, "0")}`);
        return null;
      }

      cloneBridgeMaterials(piece);
      piece.userData.bridgeIndex = index;
      piece.userData.bridgeTarget = target;
      const groupDefinition = bridgeGroupDefinitions.find((group) => group.members.includes(index));
      if (!groupDefinition) {
        bridgePuzzle.missing.push(`bridge group for piece ${index}`);
        return null;
      }
      piece.userData.bridgeGroupId = groupDefinition.id;
      piece.userData.bridgeRepresentative = groupDefinition.representative === index;
      const worldStartOverride = bridgeRepresentativeWorldStartOverrides.get(index);
      if (piece.userData.bridgeRepresentative && worldStartOverride) {
        const localStart = worldStartOverride.clone();
        if (piece.parent) piece.parent.worldToLocal(localStart);
        piece.position.copy(localStart);
      }
      if (piece.userData.bridgeRepresentative) createBridgeErrorOutline(piece);
      piece.userData.bridgeStartPosition = piece.position.clone();
      piece.userData.bridgeStartQuaternion = piece.quaternion.clone();
      piece.userData.bridgeFinalSourceScale = piece.scale.clone();
      piece.userData.bridgeStartScale = piece.scale.clone();
      if (piece.userData.bridgeRepresentative) {
        piece.userData.bridgeStartScale.multiplyScalar(bridgeFloatingScaleFactor);
        piece.scale.copy(piece.userData.bridgeStartScale);
      }
      piece.userData.bridgeAssembled = false;
      piece.userData.bridgeAnimating = false;
      piece.userData.bridgeFloatPhase = index * 0.71;

      const parentScale = new THREE.Vector3(1, 1, 1);
      piece.parent?.getWorldScale(parentScale);
      piece.userData.bridgeBobAmplitude = 0.085 / Math.max(Math.abs(parentScale.y), 0.001);
      target.visible = false;
      return piece;
    })
    .filter(Boolean);

  for (let index = 1; index <= 12; index += 1) {
    if (!piecesByIndex.has(index)) bridgePuzzle.missing.push(`BRIDGE_PIECE_${String(index).padStart(2, "0")}`);
  }

  bridgePuzzle.groups = bridgeGroupDefinitions.map((definition) => {
    const members = definition.members
      .map((index) => bridgePuzzle.pieces.find((piece) => piece.userData.bridgeIndex === index))
      .filter(Boolean);
    const representative = members.find((piece) => piece.userData.bridgeIndex === definition.representative);
    if (!representative || members.length !== definition.members.length) {
      bridgePuzzle.missing.push(`bridge group ${definition.id}`);
    }
    const group = {
      ...definition,
      members,
      representative,
      assembled: false,
      animating: false,
      rejecting: false,
      heldByHand: null,
    };
    members.forEach((piece) => {
      piece.userData.bridgeGroup = group;
    });
    return group;
  });

  bridgePuzzle.ready =
    bridgePuzzle.pieces.length === 12 && bridgePuzzle.groups.length === 6 && bridgePuzzle.missing.length === 0;
  resetBridgePuzzle();
  if (bridgePuzzle.ready) {
    setBridgePanel(getBridgeSequencePrompt(), "ready");
  } else {
    setBridgePanel("桥梁积木组件缺失", "error");
    console.warn("Bridge puzzle components missing:", bridgePuzzle.missing);
  }

  window.__BRIDGE_STATE__ = getBridgeDebugState;
  window.__BRIDGE_RESET__ = resetBridgePuzzle;
  window.__BRIDGE_ASSEMBLE__ = (index) => {
    const group = bridgePuzzle.groups.find((item) => item.id === Number(index));
    return group?.representative ? assembleBridgePiece(group.representative) : false;
  };
  window.__BRIDGE_ASSEMBLE_ALL__ = () => {
    startBridgeDebugSequence();
    return getBridgeDebugState();
  };
}

function resetBridgePuzzle() {
  releaseAllVrHeldPieces();
  setHoveredBridgePiece(null);
  bridgePuzzle.animations.length = 0;
  bridgePuzzle.complete = false;
  bridgePuzzle.assembledCount = 0;
  bridgePuzzle.nextSequenceIndex = 0;
  bridgePuzzle.debugAutoSequence = false;
  roamBridgeTest.active = false;
  roamBridgeTest.status = "idle";
  if (roamBridgeTestButton) roamBridgeTestButton.disabled = true;
  bridgePuzzle.groups.forEach((group) => {
    group.assembled = false;
    group.animating = false;
    group.rejecting = false;
    group.heldByHand = null;
  });
  bridgePuzzle.pieces.forEach((piece) => {
    const target = piece.userData.bridgeTarget;
    if (piece.userData.bridgeRepresentative) {
      piece.position.copy(piece.userData.bridgeStartPosition);
      piece.quaternion.copy(piece.userData.bridgeStartQuaternion);
      piece.scale.copy(piece.userData.bridgeStartScale);
      piece.visible = true;
    } else {
      piece.position.copy(target.position);
      piece.quaternion.copy(target.quaternion);
      piece.scale.copy(target.scale);
      piece.visible = false;
    }
    piece.userData.bridgeAssembled = false;
    piece.userData.bridgeAnimating = false;
    piece.userData.bridgeRejecting = false;
    setBridgePieceErrorVisual(piece, false);
    setBridgePieceHighlight(piece, false);
  });
  publishBridgeFloatingPositions();
  setBridgePanel(getBridgeSequencePrompt(), bridgePuzzle.ready ? "ready" : "loading");
  return getBridgeDebugState();
}

function rejectBridgeGroup(group) {
  if (!group || group.assembled || group.animating) return false;
  if (group.rejecting) return true;
  const piece = group.representative;
  const expected = getExpectedBridgeGroup();
  if (!piece || !expected) return false;

  setHoveredBridgePiece(null);
  group.rejecting = true;
  piece.userData.bridgeRejecting = true;
  piece.userData.bridgeRejectStartedAt = performance.now();
  piece.userData.bridgeRejectDuration = 0.68;
  piece.userData.bridgeRejectPosition = piece.position.clone();
  piece.userData.bridgeRejectQuaternion = piece.quaternion.clone();
  const parentScale = new THREE.Vector3(1, 1, 1);
  piece.parent?.getWorldScale(parentScale);
  piece.userData.bridgeRejectAmplitude = 0.11 / Math.max(Math.abs(parentScale.x), 0.001);
  setBridgePieceErrorVisual(piece, true, 1);
  document.body.dataset.bridgeErrorGroup = String(group.id);
  setBridgePanel(`顺序错误：请先选择${expected.label}`, "error");
  return true;
}

function finishBridgeRejection(group) {
  const piece = group.representative;
  group.rejecting = false;
  piece.userData.bridgeRejecting = false;
  setBridgePieceErrorVisual(piece, false);
  document.body.dataset.bridgeErrorGroup = "";
  if (!bridgePuzzle.groups.some((item) => item.rejecting) && bridgePuzzle.animations.length === 0) {
    setBridgePanel(getBridgeSequencePrompt(), "ready");
  }
}

function startBridgeDebugSequence() {
  bridgePuzzle.debugAutoSequence = true;
  const expected = getExpectedBridgeGroup();
  if (expected && !expected.assembled && !expected.animating) {
    assembleBridgePiece(expected.representative);
  }
}

function assembleBridgePiece(piece) {
  const group = piece?.userData.bridgeGroup;
  if (
    !bridgePuzzle.ready ||
    !piece ||
    !piece.userData.bridgeRepresentative ||
    !group ||
    group.assembled ||
    group.animating
  )
    return false;
  if (group.rejecting) return true;
  const expected = getExpectedBridgeGroup();
  if (!expected) return false;
  if (group.id !== expected.id) return rejectBridgeGroup(group);
  const target = piece.userData.bridgeTarget;
  if (!target) return false;

  setHoveredBridgePiece(null);
  group.animating = true;
  piece.userData.bridgeAnimating = true;
  const parentScale = new THREE.Vector3(1, 1, 1);
  piece.parent?.getWorldScale(parentScale);
  bridgePuzzle.animations.push({
    group,
    piece,
    elapsed: 0,
    startedAt: performance.now(),
    duration: 1.05 + (piece.userData.bridgeIndex % 3) * 0.09,
    startPosition: piece.position.clone(),
    startQuaternion: piece.quaternion.clone(),
    startScale: piece.scale.clone(),
    targetPosition: target.position.clone(),
    targetQuaternion: target.quaternion.clone(),
    targetScale: target.scale.clone(),
    arcHeight: 0.46 / Math.max(Math.abs(parentScale.y), 0.001),
  });
  setBridgePanel(`${group.label}正在归位`, "assembling");
  return true;
}

function completeBridgePiece(animation) {
  const { group } = animation;
  group.members.forEach((member) => {
    const target = member.userData.bridgeTarget;
    member.position.copy(target.position);
    member.quaternion.copy(target.quaternion);
    member.scale.copy(target.scale);
    member.visible = true;
    member.userData.bridgeAnimating = false;
    member.userData.bridgeAssembled = true;
  });
  group.animating = false;
  group.assembled = true;
  group.heldByHand = null;
  bridgePuzzle.nextSequenceIndex = Math.min(bridgePuzzle.nextSequenceIndex + 1, bridgeSelectionSequence.length);
  bridgePuzzle.assembledCount = bridgePuzzle.groups.filter((item) => item.assembled).length;
  bridgePuzzle.complete = bridgePuzzle.assembledCount === bridgePuzzle.groups.length;
  requestShadowRefresh();

  if (bridgePuzzle.complete) {
    bridgePuzzle.debugAutoSequence = false;
    if (roamBridgeTestButton) roamBridgeTestButton.disabled = false;
    setBridgePanel("桥梁搭建完成，现在可以走到对岸", "complete");
    publishGroundProbeDebug();
  } else {
    const next = getExpectedBridgeGroup();
    setBridgePanel(
      `${group.label}整组显现；下一块：${next?.label || "完成"}`,
      "ready",
    );
    if (bridgePuzzle.debugAutoSequence) {
      setTimeout(startBridgeDebugSequence, 90);
    }
  }
}

function updateBridgePuzzle(delta, time) {
  const now = performance.now();
  for (let index = bridgePuzzle.animations.length - 1; index >= 0; index -= 1) {
    const animation = bridgePuzzle.animations[index];
    animation.elapsed = Math.min((now - animation.startedAt) / 1000, animation.duration);
    const raw = animation.elapsed / animation.duration;
    const eased = 1 - (1 - raw) ** 3;
    animation.piece.position.lerpVectors(animation.startPosition, animation.targetPosition, eased);
    animation.piece.position.y += Math.sin(Math.PI * raw) * animation.arcHeight;
    animation.piece.quaternion.copy(animation.startQuaternion).slerp(animation.targetQuaternion, eased);
    animation.piece.scale.lerpVectors(animation.startScale, animation.targetScale, eased);
    if (raw >= 1) {
      completeBridgePiece(animation);
      bridgePuzzle.animations.splice(index, 1);
    }
  }

  bridgePuzzle.groups.forEach((group) => {
    if (!group.rejecting) return;
    const piece = group.representative;
    const raw = Math.min(
      (now - piece.userData.bridgeRejectStartedAt) / 1000 / piece.userData.bridgeRejectDuration,
      1,
    );
    const decay = (1 - raw) ** 1.8;
    const wave = Math.sin(raw * Math.PI * 10);
    piece.position.copy(piece.userData.bridgeRejectPosition);
    piece.position.x += wave * piece.userData.bridgeRejectAmplitude * decay;
    bridgeRejectRotation.setFromAxisAngle(bridgeForwardAxis, wave * 0.065 * decay);
    piece.quaternion.copy(piece.userData.bridgeRejectQuaternion).multiply(bridgeRejectRotation);
    const outline = piece.userData.bridgeErrorOutline;
    if (outline) outline.material.opacity = 0.25 + Math.abs(Math.sin(raw * Math.PI * 7)) * 0.75;
    if (raw >= 1) finishBridgeRejection(group);
  });

  bridgePuzzle.groups.forEach((group) => {
    const piece = group.representative;
    if (!piece || group.assembled || group.animating || group.rejecting || group.heldByHand) return;
    const phase = time * 1.35 + piece.userData.bridgeFloatPhase;
    piece.position.copy(piece.userData.bridgeStartPosition);
    piece.position.y += Math.sin(phase) * piece.userData.bridgeBobAmplitude;
    bridgeFloatRotation.setFromAxisAngle(bridgeUpAxis, Math.sin(phase * 0.72) * 0.045);
    piece.quaternion.copy(piece.userData.bridgeStartQuaternion).multiply(bridgeFloatRotation);
  });

  if (vrInteraction.ready || mode !== "roam") setHoveredBridgePiece(null);
  else if (document.pointerLockElement === renderer.domElement) updateBridgeHover(window.innerWidth * 0.5, window.innerHeight * 0.5);
}

function setBridgeRay(clientX, clientY) {
  const rect = renderer.domElement.getBoundingClientRect();
  bridgePointer.set(((clientX - rect.left) / rect.width) * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
  bridgeRaycaster.setFromCamera(bridgePointer, camera);
  scene.updateMatrixWorld(true);
}

function bridgePieceFromObject(object) {
  let candidate = object;
  while (candidate && candidate !== modelRoot) {
    if (candidate.userData.bridgeIndex) return candidate;
    candidate = candidate.parent;
  }
  return null;
}

function updateBridgeHover(clientX, clientY) {
  if (mode !== "roam" || !bridgePuzzle.ready) {
    setHoveredBridgePiece(null);
    return;
  }
  setBridgeRay(clientX, clientY);
  const candidates = bridgePuzzle.groups
    .filter((group) => !group.assembled && !group.animating && !group.rejecting && !group.heldByHand)
    .map((group) => group.representative);
  const hit = bridgeRaycaster.intersectObjects(candidates, false)[0];
  setHoveredBridgePiece(hit ? bridgePieceFromObject(hit.object) : null);
}

function selectBridgePiece(clientX, clientY) {
  if (mode !== "roam" || !bridgePuzzle.ready) return false;
  setBridgeRay(clientX, clientY);
  const candidates = bridgePuzzle.groups
    .filter((group) => !group.assembled && !group.animating && !group.rejecting && !group.heldByHand)
    .map((group) => group.representative);
  const firstHit = bridgeRaycaster.intersectObjects(candidates, false)[0];
  const piece = firstHit ? bridgePieceFromObject(firstHit.object) : null;
  return assembleBridgePiece(piece);
}

function grabVrBridgePiece(hand, piece) {
  if (!hand || hand.heldPiece || !isVrBridgePieceAvailable(piece)) return false;
  const group = piece.userData.bridgeGroup;
  scene.updateMatrixWorld(true);
  const floatingCenter = new THREE.Box3().setFromObject(piece).getCenter(new THREE.Vector3());
  const floatingDistance = Math.max(camera.position.distanceTo(floatingCenter), 0.001);
  const holdWorldPosition = hand.holdAnchor.getWorldPosition(new THREE.Vector3());
  const holdDistance = Math.max(camera.position.distanceTo(holdWorldPosition), 0.001);
  piece.userData.bridgeOriginalParent = piece.parent;
  hand.holdAnchor.attach(piece);
  piece.scale.multiplyScalar(
    bridgeHeldApparentScaleFactor * (holdDistance / floatingDistance),
  );
  piece.position.set(0, 0, 0.02);
  piece.quaternion.identity();
  piece.userData.bridgeHeld = true;
  group.heldByHand = hand.id;
  hand.heldPiece = piece;
  setBridgePieceHighlight(piece, false);
  setBridgePanel(`${group.label}已抓到${hand.id === "left" ? "左手" : "右手"}，再次点击归桥`, "ready");
  return true;
}

function releaseVrHeldPieceToBridge(hand) {
  const piece = hand?.heldPiece;
  const group = piece?.userData.bridgeGroup;
  const originalParent = piece?.userData.bridgeOriginalParent;
  if (!piece || !group || !originalParent) return false;

  scene.updateMatrixWorld(true);
  const expected = getExpectedBridgeGroup();
  originalParent.attach(piece);
  if (!expected || expected.id !== group.id) {
    piece.position.copy(piece.userData.bridgeStartPosition);
    piece.quaternion.copy(piece.userData.bridgeStartQuaternion);
    piece.scale.copy(piece.userData.bridgeStartScale);
  }
  piece.userData.bridgeHeld = false;
  group.heldByHand = null;
  hand.heldPiece = null;
  return assembleBridgePiece(piece);
}

function releaseAllVrHeldPieces() {
  if (!vrInteraction.ready) return;
  let restoredAnyPiece = false;
  vrInteraction.hands.forEach((hand) => {
    const piece = hand.heldPiece;
    const group = piece?.userData.bridgeGroup;
    const originalParent = piece?.userData.bridgeOriginalParent;
    if (piece && originalParent) {
      restoredAnyPiece = true;
      scene.updateMatrixWorld(true);
      originalParent.attach(piece);
      piece.position.copy(piece.userData.bridgeStartPosition);
      piece.quaternion.copy(piece.userData.bridgeStartQuaternion);
      piece.scale.copy(piece.userData.bridgeStartScale);
      piece.userData.bridgeHeld = false;
    }
    if (group) group.heldByHand = null;
    hand.heldPiece = null;
  });
  if (restoredAnyPiece) {
    setBridgePanel(getBridgeSequencePrompt(), bridgePuzzle.complete ? "complete" : "ready");
  }
}

function handleVrHandAction(hand) {
  if (!hand || mode !== "roam") return false;
  updateVrHandRay(hand);
  if (hand.heldPiece) return releaseVrHeldPieceToBridge(hand);

  if (hand.hitType === "reward-card") {
    return cardReward.collect();
  }

  if (hand.hitType === "fountain") {
    startFountainAnimation();
    return true;
  }

  const piece = hand.hoveredPiece;
  return piece ? grabVrBridgePiece(hand, piece) : false;
}

function getActiveVrHand() {
  if (!vrInteraction.activeHandId) return null;
  return vrInteraction.hands.find((hand) => hand.id === vrInteraction.activeHandId) || null;
}

function beginVrViewPointer(event) {
  if (event.button !== 1 || mode !== "roam") return false;
  event.preventDefault();
  renderer.domElement.focus();
  vrInteraction.hands.forEach((hand) => {
    hand.pressed = false;
    hand.moved = false;
    hand.movement = 0;
  });
  vrInteraction.activeHandId = "";
  pointerState.active = true;
  pointerState.id = event.pointerId;
  pointerState.button = event.button;
  pointerState.x = event.clientX;
  pointerState.y = event.clientY;
  pointerState.startX = event.clientX;
  pointerState.startY = event.clientY;
  pointerState.moved = false;
  document.body.dataset.vrMiddleViewActive = "true";
  if (document.pointerLockElement !== renderer.domElement && renderer.domElement.setPointerCapture) {
    try {
      renderer.domElement.setPointerCapture(event.pointerId);
    } catch {
      // Pointer capture is optional while Pointer Lock is active.
    }
  }
  return true;
}

function moveVrViewPointer(deltaX, deltaY) {
  if (!pointerState.active || (!deltaX && !deltaY)) return false;
  if (Math.hypot(deltaX, deltaY) > 0) pointerState.moved = true;
  rotatePlayer(deltaX, deltaY, 0.0024);
  return true;
}

function finishVrViewPointer(button) {
  if (button !== 1 || !pointerState.active) return false;
  pointerState.active = false;
  pointerState.id = null;
  pointerState.button = null;
  document.body.dataset.vrMiddleViewActive = "false";
  return true;
}

function beginVrPointer(event) {
  const hand = getVrHandByButton(event.button);
  if (!hand || mode !== "roam") return false;
  event.preventDefault();
  renderer.domElement.focus();
  if (pointerState.active) finishVrViewPointer(pointerState.button);
  vrInteraction.hands.forEach((other) => {
    if (other === hand) return;
    other.pressed = false;
    other.moved = false;
    other.movement = 0;
  });
  hand.pressed = true;
  hand.moved = false;
  hand.movement = 0;
  hand.lastX = event.clientX;
  hand.lastY = event.clientY;
  vrInteraction.activeHandId = hand.id;
  if (document.pointerLockElement !== renderer.domElement && renderer.domElement.setPointerCapture) {
    try {
      renderer.domElement.setPointerCapture(event.pointerId);
    } catch {
      // Some browsers do not expose pointer capture while entering Pointer Lock.
    }
  }
  return true;
}

function moveVrPointers(deltaX, deltaY) {
  const hand = getActiveVrHand();
  if (!hand?.pressed || (!deltaX && !deltaY)) return false;
  hand.pointer.x = THREE.MathUtils.clamp(hand.pointer.x + deltaX * 0.0032, -0.86, 0.86);
  hand.pointer.y = THREE.MathUtils.clamp(hand.pointer.y - deltaY * 0.0032, -0.72, 0.78);
  hand.movement += Math.hypot(deltaX, deltaY);
  if (hand.movement > 4) hand.moved = true;
  rotatePlayer(deltaX, deltaY, 0.00125);
  return true;
}

function finishVrPointer(button) {
  const hand = getVrHandByButton(button);
  if (!hand || !hand.pressed || vrInteraction.activeHandId !== hand.id) return false;
  hand.pressed = false;
  vrInteraction.activeHandId = "";
  if (hand.moved) return true;
  handleVrHandAction(hand);
  return true;
}

function getBridgeDebugState() {
  return {
    ready: bridgePuzzle.ready,
    complete: bridgePuzzle.complete,
    assembledCount: bridgePuzzle.assembledCount,
    groupCount: bridgePuzzle.groups.length,
    pieceCount: bridgePuzzle.pieces.length,
    sequence: [...bridgeSelectionSequence],
    nextSequenceIndex: bridgePuzzle.nextSequenceIndex,
    nextGroup: getExpectedBridgeGroup()?.id ?? null,
    missing: [...bridgePuzzle.missing],
    animating: bridgePuzzle.animations.map((animation) => animation.group.id),
    rejecting: bridgePuzzle.groups.filter((group) => group.rejecting).map((group) => group.id),
    visibleFloatingCount: bridgePuzzle.groups.filter(
      (group) => !group.assembled && !group.animating,
    ).length,
    groups: bridgePuzzle.groups.map((group) => ({
      id: group.id,
      label: group.label,
      representative: group.representative?.userData.bridgeIndex ?? null,
      members: group.members.map((piece) => piece.userData.bridgeIndex),
      assembled: group.assembled,
      animating: group.animating,
      rejecting: group.rejecting,
      heldByHand: group.heldByHand,
    })),
    pieces: bridgePuzzle.pieces.map((piece) => ({
      index: piece.userData.bridgeIndex,
      name: piece.name,
      groupId: piece.userData.bridgeGroupId,
      representative: piece.userData.bridgeRepresentative,
      visible: piece.visible,
      assembled: piece.userData.bridgeAssembled,
      position: piece.position.toArray().map((value) => Number(value.toFixed(4))),
      scale: piece.scale.toArray().map((value) => Number(value.toFixed(4))),
      floatingScale: piece.userData.bridgeStartScale.toArray().map((value) => Number(value.toFixed(4))),
      target: piece.userData.bridgeTarget.position.toArray().map((value) => Number(value.toFixed(4))),
      targetScale: piece.userData.bridgeTarget.scale.toArray().map((value) => Number(value.toFixed(4))),
    })),
  };
}

function prepareGroundCollision(model) {
  groundCollision.islandMeshes.length = 0;
  groundCollision.bridgeMeshes.length = 0;

  model.traverse((child) => {
    if (!child.isMesh) return;
    if (/grass(?:\s|_)+cap/i.test(child.name)) {
      groundCollision.islandMeshes.push(child);
    }
    if (child.name === "BRIDGE_PIECE_01") {
      groundCollision.bridgeMeshes.push(child);
    }
  });

  groundCollision.ready = groundCollision.islandMeshes.length > 0;
  document.body.dataset.groundReady = String(groundCollision.ready);
  document.body.dataset.islandGroundCount = String(groundCollision.islandMeshes.length);
  document.body.dataset.bridgeGroundCount = String(groundCollision.bridgeMeshes.length);
  if (roamTestButton) roamTestButton.disabled = !groundCollision.ready;
  window.__ROAM_STATE__ = getRoamDebugState;
}

function isWorldVisible(object) {
  let current = object;
  while (current) {
    if (!current.visible) return false;
    if (current === scene) break;
    current = current.parent;
  }
  return true;
}

function getGroundSample(x, z) {
  if (!groundCollision.ready) return null;
  scene.updateMatrixWorld(true);

  const rayHeight = Number.isFinite(modelBounds.max.y) ? Math.max(modelBounds.max.y + 3, 12) : 12;
  groundCollision.origin.set(x, rayHeight, z);
  groundCollision.raycaster.set(groundCollision.origin, groundCollision.down);
  groundCollision.raycaster.far = rayHeight + 20;

  const candidates = bridgePuzzle.complete
    ? groundCollision.islandMeshes.concat(groundCollision.bridgeMeshes)
    : groundCollision.islandMeshes;
  const hits = groundCollision.raycaster.intersectObjects(candidates, false);
  for (const hit of hits) {
    if (!hit.face || !isWorldVisible(hit.object)) continue;
    if (hit.object.userData.bridgeIndex && !hit.object.userData.bridgeAssembled) continue;
    groundCollision.worldNormal.copy(hit.face.normal).transformDirection(hit.object.matrixWorld);
    if (groundCollision.worldNormal.y < 0.45) continue;

    return {
      surfaceY: hit.point.y,
      name: hit.object.name,
      type: hit.object.userData.bridgeIndex ? "bridge" : "island",
      normalY: groundCollision.worldNormal.y,
    };
  }
  return null;
}

function getGroundSurfaceDebug(mesh) {
  const bounds = new THREE.Box3().setFromObject(mesh);
  const center = bounds.getCenter(new THREE.Vector3());
  return {
    name: mesh.name,
    visible: isWorldVisible(mesh),
    min: bounds.min.toArray().map((value) => Number(value.toFixed(3))),
    max: bounds.max.toArray().map((value) => Number(value.toFixed(3))),
    center: center.toArray().map((value) => Number(value.toFixed(3))),
  };
}

function publishGroundSurfaceDebug() {
  const surfaces = groundCollision.islandMeshes.map(getGroundSurfaceDebug);
  document.body.dataset.groundSurfaces = JSON.stringify(surfaces);
}

function publishGroundProbeDebug() {
  if (!roamDebugMode || !groundCollision.ready) return;
  const probes = [
    ["main", 3.0, 4.07],
    ["lower-step", 2.0, 4.07],
    ["middle-step", 1.3, 4.07],
    ["high-step", -0.2, 4.07],
    ["high-island", -1.62, 4.07],
    ["bridge-center", 7.5, 4.0],
    ["outside-edge", -3.75, 4.07],
  ].map(([label, x, z]) => {
    const sample = getGroundSample(x, z);
    return {
      label,
      x,
      z,
      surfaceY: sample ? Number(sample.surfaceY.toFixed(3)) : null,
      name: sample?.name ?? null,
      type: sample?.type ?? null,
    };
  });
  document.body.dataset.groundProbes = JSON.stringify(probes);

  const bridgeProfile = [];
  for (let x = 10.6; x >= 4.8; x -= 0.1) {
    const sample = getGroundSample(x, 4.0);
    bridgeProfile.push({
      x: Number(x.toFixed(2)),
      surfaceY: sample ? Number(sample.surfaceY.toFixed(3)) : null,
      name: sample?.name ?? null,
    });
  }
  document.body.dataset.bridgeGroundProfile = JSON.stringify(bridgeProfile);
}

function publishRoamStairTest() {
  document.body.dataset.roamStairTest = JSON.stringify({
    status: roamStairTest.status,
    transitions: roamStairTest.transitions,
    edgeBlocked: roamStairTest.edgeBlocked,
    position: player.position.toArray().map((value) => Number(value.toFixed(3))),
    groundY: Number(player.groundY.toFixed(3)),
    groundName: player.groundName,
  });
}

function recordRoamStairTransition() {
  const previous = roamStairTest.transitions.at(-1);
  if (previous?.name === player.groundName) return;
  roamStairTest.transitions.push({
    name: player.groundName,
    surfaceY: Number(player.groundY.toFixed(3)),
    cameraY: Number(player.position.y.toFixed(3)),
    x: Number(player.position.x.toFixed(3)),
  });
  publishRoamStairTest();
}

function startRoamStairTest() {
  if (!roamDebugMode || !groundCollision.ready) return;
  setMode("roam");
  const startX = 2.75;
  const startZ = 4.07;
  const ground = getGroundSample(startX, startZ);
  if (!ground) {
    roamStairTest.status = "failed-no-start-ground";
    publishRoamStairTest();
    return;
  }

  player.position.set(startX, ground.surfaceY + player.eyeHeight, startZ);
  player.groundY = ground.surfaceY;
  player.groundName = ground.name;
  player.yaw = Math.PI * 0.5;
  player.pitch = 0.08;
  roamStairTest.active = true;
  roamStairTest.status = "walking";
  roamStairTest.transitions.length = 0;
  roamStairTest.edgeBlocked = null;
  recordRoamStairTransition();
  applyPlayerCamera();
}

function updateRoamStairTest(delta) {
  if (!roamStairTest.active) return false;
  if (roamStairTest.status === "settling") return true;

  const dx = roamStairTest.targetX - player.position.x;
  const dz = roamStairTest.targetZ - player.position.z;
  const remaining = Math.hypot(dx, dz);
  if (remaining <= 0.012) {
    roamStairTest.status = "settling";
    publishRoamStairTest();
    return true;
  }

  const distance = Math.min(player.speed * 0.82 * delta, remaining);
  const nextX = player.position.x + (dx / remaining) * distance;
  const nextZ = player.position.z + (dz / remaining) * distance;
  if (!tryMovePlayerTo(nextX, nextZ)) {
    roamStairTest.active = false;
    roamStairTest.status = "failed-blocked-on-route";
    publishRoamStairTest();
    return true;
  }
  recordRoamStairTransition();
  return true;
}

function publishRoamBridgeTest() {
  document.body.dataset.roamBridgeTest = JSON.stringify({
    status: roamBridgeTest.status,
    transitions: roamBridgeTest.transitions,
    position: player.position.toArray().map((value) => Number(value.toFixed(3))),
    groundY: Number(player.groundY.toFixed(3)),
    groundName: player.groundName,
  });
}

function recordRoamBridgeTransition() {
  const previous = roamBridgeTest.transitions.at(-1);
  if (previous?.name === player.groundName) return;
  roamBridgeTest.transitions.push({
    name: player.groundName,
    surfaceY: Number(player.groundY.toFixed(3)),
    x: Number(player.position.x.toFixed(3)),
  });
  publishRoamBridgeTest();
}

function startRoamBridgeTest() {
  if (!roamDebugMode || !bridgePuzzle.complete || !groundCollision.ready) return;
  setMode("roam");
  const startX = 10.55;
  const startZ = 4.0;
  const ground = getGroundSample(startX, startZ);
  if (!ground) {
    roamBridgeTest.status = "failed-no-start-ground";
    publishRoamBridgeTest();
    return;
  }

  roamStairTest.active = false;
  player.position.set(startX, ground.surfaceY + player.eyeHeight, startZ);
  player.groundY = ground.surfaceY;
  player.groundName = ground.name;
  player.yaw = Math.PI * 0.5;
  player.pitch = 0.08;
  roamBridgeTest.active = true;
  roamBridgeTest.status = "walking";
  roamBridgeTest.transitions.length = 0;
  recordRoamBridgeTransition();
  applyPlayerCamera();
}

function updateRoamBridgeTest(delta) {
  if (!roamBridgeTest.active) return false;
  const dx = roamBridgeTest.targetX - player.position.x;
  const dz = roamBridgeTest.targetZ - player.position.z;
  const remaining = Math.hypot(dx, dz);
  if (remaining <= 0.012) {
    roamBridgeTest.active = false;
    roamBridgeTest.status = "complete";
    publishRoamBridgeTest();
    return true;
  }

  const distance = Math.min(player.speed * 0.9 * delta, remaining);
  const nextX = player.position.x + (dx / remaining) * distance;
  const nextZ = player.position.z + (dz / remaining) * distance;
  if (!tryMovePlayerTo(nextX, nextZ)) {
    roamBridgeTest.active = false;
    roamBridgeTest.status = "failed-blocked-on-route";
    publishRoamBridgeTest();
    return true;
  }
  recordRoamBridgeTransition();
  return true;
}

function getRoamDebugState() {
  const sample = getGroundSample(player.position.x, player.position.z);
  return {
    ready: groundCollision.ready,
    mode,
    position: player.position.toArray().map((value) => Number(value.toFixed(3))),
    yaw: Number(player.yaw.toFixed(3)),
    pitch: Number(player.pitch.toFixed(3)),
    groundY: Number(player.groundY.toFixed(3)),
    groundName: player.groundName,
    eyeHeight: player.eyeHeight,
    currentSample: sample
      ? {
          surfaceY: Number(sample.surfaceY.toFixed(3)),
          name: sample.name,
          type: sample.type,
          normalY: Number(sample.normalY.toFixed(3)),
        }
      : null,
    islandSurfaceCount: groundCollision.islandMeshes.length,
    bridgeSurfaceCount: groundCollision.bridgeMeshes.length,
    bridgeEnabled: bridgePuzzle.complete,
    surfaces: groundCollision.islandMeshes.map(getGroundSurfaceDebug),
  };
}

function prepareSeatedAnimalDebug(model) {
  const rootPattern = /^ANIMAL_(BEAR|CAT|DUCK|FROG)_ROOT$/;
  const roots = [];
  model.traverse((object) => {
    if (rootPattern.test(object.name)) roots.push(object);
  });

  const bounds = new THREE.Box3();
  const position = new THREE.Vector3();
  roots.forEach((root) => bounds.expandByObject(root));
  const getState = () => ({
    count: roots.length,
    ids: roots.map((root) => root.name.replace(/^ANIMAL_|_ROOT$/g, "").toLowerCase()),
    roots: roots.map((root) => ({
      name: root.name,
      position: root
        .getWorldPosition(position)
        .toArray()
        .map((value) => Number(value.toFixed(3))),
      seatBench: root.userData.seat_bench || "",
      seatOffset: Number(root.userData.seat_offset || 0),
      pose: root.userData.pose || "",
      replacementSource: root.userData.replacementSource || "",
      replacementModel: root.children[0]?.name || "",
    })),
  });
  window.__ANIMAL_CHARACTER_STATE__ = getState;
  document.body.dataset.animalCharacterCount = String(roots.length);
  document.body.dataset.animalCharacterIds = getState().ids.join(",");
  document.body.dataset.animalCharacterState = JSON.stringify(getState());

  if (!animalPreviewMode || roots.length !== 4 || bounds.isEmpty()) return;
  const center = bounds.getCenter(new THREE.Vector3());
  camera.position.set(center.x + 2.42, center.y + 0.52, center.z);
  camera.fov = 43;
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
  document.body.dataset.animalPreview = "true";
}

function loadGltfAsset(loader, url) {
  return new Promise((resolve, reject) => loader.load(url, resolve, undefined, reject));
}

function configureLowAnimalAsset(asset, definition) {
  asset.name = `LOW_${definition.id.toUpperCase()}_FBX_MODEL`;
  asset.position.set(0, 0, 0);
  asset.rotation.set(0, definition.yaw, 0);
  asset.scale.setScalar(1);
  asset.traverse((child) => {
    if (!child.isMesh) return;
    child.castShadow = true;
    child.receiveShadow = true;
    const materials = Array.isArray(child.material) ? child.material : [child.material];
    materials.filter(Boolean).forEach((material) => {
      material.flatShading = true;
      material.roughness = 0.82;
      material.metalness = 0;
      material.envMapIntensity = 0.35;
      material.toneMapped = true;
      material.color.multiply(new THREE.Color(...definition.tint));
      if (material.map) {
        material.map.colorSpace = THREE.SRGBColorSpace;
        material.map.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
        material.map.needsUpdate = true;
      }
      material.needsUpdate = true;
    });
  });
}

async function replaceAnimalsWithLowFbx(model) {
  const loader = new GLTFLoader();
  const roots = lowAnimalDefinitions.map((definition) => {
    const root = model.getObjectByName(definition.rootName);
    if (!root) throw new Error(`Missing animal anchor: ${definition.rootName}`);
    root.visible = false;
    return { definition, root, originalChildren: [...root.children], originalBounds: new THREE.Box3().setFromObject(root) };
  });

  document.body.dataset.animalReplacementStatus = "loading";
  if (loaderStatus) loaderStatus.textContent = "正在加载低模角色…";

  try {
    const loaded = await Promise.all(
      roots.map(async (entry) => ({
        ...entry,
        asset: (await loadGltfAsset(loader, entry.definition.url)).scene,
      })),
    );

    loaded.forEach(({ definition, root, asset, originalBounds }) => {
      configureLowAnimalAsset(asset, definition);
      root.clear();
      root.add(asset);
      root.visible = true;
      root.updateWorldMatrix(true, true);

      const originalSize = originalBounds.getSize(new THREE.Vector3());
      const replacementSize = new THREE.Box3().setFromObject(asset).getSize(new THREE.Vector3());
      if (replacementSize.y > 0) asset.scale.setScalar(originalSize.y / replacementSize.y);
      root.updateWorldMatrix(true, true);

      const originalCenter = originalBounds.getCenter(new THREE.Vector3());
      const replacementBounds = new THREE.Box3().setFromObject(asset);
      const replacementCenter = replacementBounds.getCenter(new THREE.Vector3());
      const worldDelta = new THREE.Vector3(
        originalCenter.x - replacementCenter.x,
        originalBounds.min.y - replacementBounds.min.y,
        originalCenter.z - replacementCenter.z,
      );
      const rootWorld = root.getWorldPosition(new THREE.Vector3());
      const rootLocal = root.worldToLocal(rootWorld.clone());
      const offsetLocal = root.worldToLocal(rootWorld.clone().add(worldDelta)).sub(rootLocal);
      asset.position.add(offsetLocal);

      root.userData.replacementSource = `low ${definition.id}.fbx`;
      root.userData.pose = "original_low_fbx_at_existing_seat";
    });

    document.body.dataset.animalReplacementStatus = "complete";
    document.body.dataset.animalReplacementSources = lowAnimalDefinitions
      .map((definition) => `low ${definition.id}.fbx`)
      .join(",");
  } catch (error) {
    roots.forEach(({ root, originalChildren }) => {
      if (root.children.length === 0) originalChildren.forEach((child) => root.add(child));
      root.visible = true;
    });
    document.body.dataset.animalReplacementStatus = "error";
    throw error;
  }
}

function loadModel() {
  const loader = new GLTFLoader();
  loader.load(
    "/models/sky_island_lowpoly.glb",
    async (gltf) => {
      const model = gltf.scene;
      model.name = "Loaded Blender lowpoly sky island";
      model.traverse((child) => {
        if (!child.isMesh) return;
        child.castShadow = true;
        child.receiveShadow = true;
        if (child.material) {
          child.material.flatShading = true;
          child.material.needsUpdate = true;
        }
      });

      modelRoot.add(model);
      requestShadowRefresh();
      prepareFountainAnimation(model);
      prepareVrFountainTarget(model);
      prepareBridgePuzzle(model);
      prepareGroundCollision(model);
      try {
        await replaceAnimalsWithLowFbx(model);
      } catch (error) {
        console.error("Failed to replace Sky Island animals with low FBX assets", error);
      }
      requestShadowRefresh();
      modelBounds = new THREE.Box3().setFromObject(modelRoot);
      modelLoaded = true;
      publishGroundSurfaceDebug();
      publishGroundProbeDebug();
      window.__SKY_ISLAND_READY__ = true;
      window.__SKY_ISLAND_STATE__ = getDebugState;
      document.body.dataset.ready = "true";
      loaderStatus?.remove();
      resetOverviewCamera();
      prepareSeatedAnimalDebug(model);
    },
    (event) => {
      if (!event.total || !loaderStatus) return;
      const progress = Math.round((event.loaded / event.total) * 100);
      loaderStatus.textContent = `加载天空岛 ${progress}%`;
    },
    () => {
      if (loaderStatus) loaderStatus.textContent = "模型加载失败";
    },
  );
}

function resetOverviewCamera() {
  camera.position.copy(overviewCameraPreset.position);
  camera.fov = overviewCameraPreset.fov;
  camera.updateProjectionMatrix();
  controls.target.copy(overviewCameraPreset.target);
  controls.update();
}

function resetPlayer() {
  player.position.copy(roamCameraPreset.position);
  player.yaw = roamCameraPreset.yaw;
  player.pitch = roamCameraPreset.pitch;
  const ground = getGroundSample(player.position.x, player.position.z);
  player.groundY = ground?.surfaceY ?? roamCameraPreset.position.y - player.eyeHeight;
  player.groundName = ground?.name ?? "";
  player.position.y = player.groundY + player.eyeHeight;
  applyPlayerCamera();
}

function setMode(nextMode, shouldLock = false) {
  mode = nextMode;
  document.body.dataset.mode = mode;
  document.body.dataset.cameraMode = mode;
  window.__SKY_ISLAND_MODE__ = mode;
  modeLabel.textContent = mode === "browse" ? "浏览" : "漫游";
  browseButton.setAttribute("aria-pressed", String(mode === "browse"));
  roamButton.setAttribute("aria-pressed", String(mode === "roam"));
  controls.enabled = mode === "browse";
  movePad.hidden = mode !== "roam";
  setVrHandsVisible(mode === "roam");
  cardReward.setMode(mode);
  syncFountainStarProgress();
  renderer.domElement.focus();

  if (mode === "browse") {
    releaseAllVrHeldPieces();
    if (document.pointerLockElement === renderer.domElement) {
      document.exitPointerLock();
    }
    resetOverviewCamera();
    return;
  }

  modelRoot.rotation.y = 0;
  resetPlayer();
  if (shouldLock && renderer.domElement.requestPointerLock) {
    renderer.domElement.requestPointerLock();
  }
}

function rotatePlayer(deltaX, deltaY, sensitivity = 0.0024) {
  player.yaw -= deltaX * sensitivity;
  player.pitch -= deltaY * sensitivity;
  player.pitch = THREE.MathUtils.clamp(player.pitch, -0.72, 0.55);
}

function applyPlayerCamera() {
  camera.position.copy(player.position);
  camera.rotation.order = "YXZ";
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;
  camera.rotation.z = 0;
  camera.fov = 68;
  camera.updateProjectionMatrix();
  document.body.dataset.playerX = player.position.x.toFixed(3);
  document.body.dataset.playerY = player.position.y.toFixed(3);
  document.body.dataset.playerZ = player.position.z.toFixed(3);
  document.body.dataset.playerYaw = player.yaw.toFixed(3);
  document.body.dataset.playerPitch = player.pitch.toFixed(3);
  document.body.dataset.playerGroundY = player.groundY.toFixed(3);
  document.body.dataset.playerGround = player.groundName;
}

function tryMovePlayerTo(x, z) {
  const ground = getGroundSample(x, z);
  if (!ground) return false;
  const heightDelta = ground.surfaceY - player.groundY;
  if (heightDelta > player.maxStepHeight || heightDelta < -player.maxDropHeight) return false;

  player.position.x = x;
  player.position.z = z;
  player.groundY = ground.surfaceY;
  player.groundName = ground.name;
  groundCollision.lastSample = ground;
  return true;
}

function updateCardRewardTrigger() {
  const rewardState = cardReward.getState();
  if (
    mode === "roam" &&
    bridgePuzzle.complete &&
    !rewardState.triggered &&
    !rewardState.collected &&
    player.position.x <= 6.45 &&
    player.groundName.includes("Main_playable_floating_island")
  ) {
    cardReward.trigger();
  }
}

function updatePlayer(delta) {
  if (mode !== "roam") return;

  if (!updateRoamBridgeTest(delta) && !updateRoamStairTest(delta)) {
    playerForward.set(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
    playerRight.set(Math.cos(player.yaw), 0, -Math.sin(player.yaw));
    playerIntent.set(0, 0, 0);
    if (keyIsActive("KeyW") || keyIsActive("ArrowUp")) playerIntent.add(playerForward);
    if (keyIsActive("KeyS") || keyIsActive("ArrowDown")) playerIntent.sub(playerForward);
    if (keyIsActive("KeyA") || keyIsActive("ArrowLeft")) playerIntent.sub(playerRight);
    if (keyIsActive("KeyD") || keyIsActive("ArrowRight")) playerIntent.add(playerRight);

    if (playerIntent.lengthSq() > 0) {
      playerIntent.normalize().multiplyScalar(player.speed * delta);
      const nextX = player.position.x + playerIntent.x;
      const nextZ = player.position.z + playerIntent.z;
      if (!tryMovePlayerTo(nextX, nextZ)) {
        if (!tryMovePlayerTo(nextX, player.position.z)) {
          tryMovePlayerTo(player.position.x, nextZ);
        }
      }
    }
  }

  const currentGround = getGroundSample(player.position.x, player.position.z);
  if (currentGround) {
    player.groundY = currentGround.surfaceY;
    player.groundName = currentGround.name;
    groundCollision.lastSample = currentGround;
  }
  player.position.y = THREE.MathUtils.damp(
    player.position.y,
    player.groundY + player.eyeHeight,
    player.verticalFollow,
    delta,
  );
  if (
    roamStairTest.active &&
    roamStairTest.status === "settling" &&
    Math.abs(player.position.y - (player.groundY + player.eyeHeight)) < 0.006
  ) {
    const finalX = player.position.x;
    const finalZ = player.position.z;
    roamStairTest.edgeBlocked = !tryMovePlayerTo(-3.75, 4.07);
    player.position.x = finalX;
    player.position.z = finalZ;
    const finalGround = getGroundSample(finalX, finalZ);
    if (finalGround) {
      player.groundY = finalGround.surfaceY;
      player.groundName = finalGround.name;
    }
    roamStairTest.active = false;
    roamStairTest.status = "complete";
    publishRoamStairTest();
  }
  dismissFountainStarsOnStairs();
  updateCardRewardTrigger();
  applyPlayerCamera();
}

function animate() {
  const frameDelta = clock.getDelta();
  frameMetrics.samples.push(frameDelta * 1000);
  if (frameMetrics.samples.length > frameMetrics.maxSamples) frameMetrics.samples.shift();
  frameMetrics.framesSincePublish += 1;
  if (frameMetrics.framesSincePublish >= 60) {
    document.body.dataset.frameMetrics = JSON.stringify(getFramePerformance());
    frameMetrics.framesSincePublish = 0;
  }
  const movementDelta = Math.min(frameDelta, 0.033);
  const animationDelta = Math.min(frameDelta, 0.25);
  introDrift += movementDelta;
  updatePlayer(movementDelta);
  updateFountainAnimation(animationDelta, introDrift);
  updateBridgePuzzle(animationDelta, introDrift);
  cardReward.update(animationDelta, introDrift);

  if (mode === "browse") {
    controls.update();
    modelRoot.rotation.y = Math.sin(introDrift * 0.22) * 0.012;
  } else {
    modelRoot.rotation.y = THREE.MathUtils.damp(modelRoot.rotation.y, 0, 4, movementDelta);
  }

  updateVrHands(movementDelta);

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

function resize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  vrInteraction.hands.forEach((hand) => {
    hand.rayMaterial.resolution.set(window.innerWidth, window.innerHeight);
  });
}

function mapMoveKey(direction) {
  return {
    forward: "KeyW",
    back: "KeyS",
    left: "KeyA",
    right: "KeyD",
  }[direction];
}

function getDebugState() {
  return {
    mode,
    ready: modelLoaded,
    camera: camera.position.toArray(),
    player: player.position.toArray(),
    bounds: [modelBounds.min.toArray(), modelBounds.max.toArray()],
    drawCalls: renderer.info.render.calls,
    triangles: renderer.info.render.triangles,
    performance: getFramePerformance(),
    fountain: getFountainDebugState(),
    bridge: getBridgeDebugState(),
    cardReward: cardReward.getState(),
    roam: getRoamDebugState(),
    vrHands: getVrHandDebugState(),
  };
}

window.addEventListener("resize", resize);

window.addEventListener("keydown", (event) => {
  keys.add(event.code);
  if (!event.repeat && event.code === "Space") {
    event.preventDefault();
    const nextMode = mode === "browse" ? "roam" : "browse";
    setMode(nextMode, nextMode === "roam");
    return;
  }
  if (!event.repeat && event.code === "KeyX") {
    event.preventDefault();
    cardReward.toggleBackpack();
    return;
  }
  if (!event.repeat && event.code === "KeyF") {
    event.preventDefault();
    startFountainAnimation();
    return;
  }
  if (!event.repeat && event.code === "KeyR") {
    event.preventDefault();
    if (mode === "browse") resetOverviewCamera();
    else resetPlayer();
    return;
  }
  if (bridgeDebugMode && mode === "roam" && !event.repeat && event.code === "KeyB") {
    event.preventDefault();
    startBridgeDebugSequence();
    return;
  }
  if (bridgeDebugMode && mode === "roam" && !event.repeat && event.code === "KeyC") {
    event.preventDefault();
    cardReward.trigger();
    return;
  }
  if (bridgeDebugMode && mode === "roam" && !event.repeat && event.code === "KeyV") {
    event.preventDefault();
    startRoamBridgeTest();
    return;
  }
  if (roamDebugMode && mode === "roam" && !event.repeat && event.code === "KeyT") {
    event.preventDefault();
    startRoamStairTest();
    return;
  }
  if (event.code === "Escape" && mode === "roam") {
    setMode("browse");
  }
});

window.addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

document.addEventListener("pointerlockchange", () => {
  if (mode === "roam" && document.pointerLockElement !== renderer.domElement) {
    renderer.domElement.focus();
  }
});

document.addEventListener("mousemove", (event) => {
  if (mode !== "roam" || document.pointerLockElement !== renderer.domElement) return;
  if (pointerState.active) moveVrViewPointer(event.movementX, event.movementY);
  else moveVrPointers(event.movementX, event.movementY);
});

renderer.domElement.addEventListener("pointerdown", (event) => {
  if (!beginVrViewPointer(event)) beginVrPointer(event);
});

renderer.domElement.addEventListener("pointermove", (event) => {
  if (mode !== "roam" || document.pointerLockElement === renderer.domElement) return;
  if (pointerState.active) {
    const dx = event.clientX - pointerState.x;
    const dy = event.clientY - pointerState.y;
    pointerState.x = event.clientX;
    pointerState.y = event.clientY;
    moveVrViewPointer(dx, dy);
    return;
  }
  const hand = getActiveVrHand();
  if (!hand?.pressed) return;
  const dx = event.clientX - hand.lastX;
  const dy = event.clientY - hand.lastY;
  hand.lastX = event.clientX;
  hand.lastY = event.clientY;
  moveVrPointers(dx, dy);
});

document.addEventListener("pointerup", (event) => {
  if (mode !== "roam") return;
  if (!finishVrViewPointer(event.button)) finishVrPointer(event.button);
});

document.addEventListener("pointercancel", (event) => {
  if (
    pointerState.active &&
    (event.button === 1 || event.pointerId === pointerState.id)
  ) {
    finishVrViewPointer(1);
    return;
  }
  const hand = getVrHandByButton(event.button);
  if (!hand) return;
  hand.pressed = false;
  hand.moved = false;
  hand.movement = 0;
  if (vrInteraction.activeHandId === hand.id) vrInteraction.activeHandId = "";
});

renderer.domElement.addEventListener("contextmenu", (event) => event.preventDefault());
renderer.domElement.addEventListener("auxclick", (event) => {
  if (event.button === 1) event.preventDefault();
});

browseButton.addEventListener("click", () => setMode("browse"));
roamButton.addEventListener("click", () => setMode("roam", true));
fountainButton.addEventListener("click", () => {
  if (mode === "browse") startFountainAnimation();
});
resetButton.addEventListener("click", () => {
  if (mode === "browse") resetOverviewCamera();
  else resetPlayer();
});

moveButtons.forEach((button) => {
  const key = mapMoveKey(button.dataset.move);
  button.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    pressedPadKeys.add(key);
    button.setPointerCapture(event.pointerId);
  });
  button.addEventListener("pointerup", () => pressedPadKeys.delete(key));
  button.addEventListener("pointercancel", () => pressedPadKeys.delete(key));
  button.addEventListener("pointerleave", () => pressedPadKeys.delete(key));
});

if (roamDebugMode) {
  roamTestButton = document.createElement("button");
  roamTestButton.id = "roam-stair-test";
  roamTestButton.className = "tool-button";
  roamTestButton.type = "button";
  roamTestButton.textContent = "△";
  roamTestButton.setAttribute("aria-label", "测试台阶");
  roamTestButton.disabled = true;
  roamTestButton.addEventListener("click", startRoamStairTest);
  document.querySelector(".toolbar")?.appendChild(roamTestButton);

  roamBridgeTestButton = document.createElement("button");
  roamBridgeTestButton.id = "roam-bridge-test";
  roamBridgeTestButton.className = "tool-button";
  roamBridgeTestButton.type = "button";
  roamBridgeTestButton.textContent = "⌁";
  roamBridgeTestButton.setAttribute("aria-label", "测试过桥");
  roamBridgeTestButton.disabled = true;
  roamBridgeTestButton.addEventListener("click", startRoamBridgeTest);
  document.querySelector(".toolbar")?.appendChild(roamBridgeTestButton);
}

setupVrHands();
setupLighting();
resetOverviewCamera();
setMode("browse");
loadModel();
animate();
