import * as THREE from "three";

const clamp01 = (value) => Math.max(0, Math.min(1, value));

const easeOutCubic = (value) => 1 - Math.pow(1 - clamp01(value), 3);

const easeOutBack = (value) => {
  const t = clamp01(value);
  const c1 = 1.45;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};

export function createCardRewardSystem({ camera, backpackElement }) {
  const textureLoader = new THREE.TextureLoader();
  const loadTexture = (url) => {
    const texture = textureLoader.load(url);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 4;
    return texture;
  };

  const backTexture = loadTexture("/cards/card-back.png");
  const card01Texture = loadTexture("/cards/card-01.png");
  const cardGeometry = new THREE.PlaneGeometry(0.38, 0.58);
  const aimBox = new THREE.Box3();
  const aimPoint = new THREE.Vector3();
  const collectTargetPosition = new THREE.Vector3(0.74, -0.52, -0.96);
  const group = new THREE.Group();
  group.name = "CARD_REWARD_PRESENTATION";
  group.visible = false;
  camera.add(group);

  const targetPositions = [
    new THREE.Vector3(0, 0.04, -1.36),
    new THREE.Vector3(-0.58, 0.29, -1.62),
    new THREE.Vector3(0.58, 0.29, -1.62),
    new THREE.Vector3(-0.68, -0.29, -1.68),
    new THREE.Vector3(0.68, -0.29, -1.68),
    new THREE.Vector3(0, -0.47, -1.72),
  ];

  const cards = Array.from({ length: 6 }, (_, index) => {
    const material = new THREE.MeshBasicMaterial({
      map: backTexture,
      color: 0xffffff,
      transparent: true,
      opacity: 1,
      alphaTest: 0.01,
      depthTest: false,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    const card = new THREE.Mesh(cardGeometry, material);
    card.name = index === 0 ? "CARD_REWARD_01" : `CARD_REWARD_BACK_${index + 1}`;
    card.renderOrder = 82 - index;
    card.frustumCulled = false;
    card.userData.cardRewardIndex = index;
    group.add(card);
    return card;
  });

  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0xffd05d,
    transparent: true,
    opacity: 0,
    depthTest: false,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    toneMapped: false,
  });
  const glow = new THREE.Mesh(new THREE.CircleGeometry(0.43, 48), glowMaterial);
  glow.name = "CARD_REWARD_GLOW";
  glow.position.set(0, 0.04, -1.39);
  glow.renderOrder = 70;
  glow.frustumCulled = false;
  group.add(glow);

  const state = {
    triggered: false,
    collected: false,
    phase: "idle",
    elapsed: 0,
    frontShown: false,
    hovered: false,
    backpackOpen: false,
    roamMode: false,
    collectStartPosition: new THREE.Vector3(),
    collectStartScale: new THREE.Vector3(),
  };

  function publish() {
    document.body.dataset.cardRewardTriggered = String(state.triggered);
    document.body.dataset.cardRewardCollected = String(state.collected);
    document.body.dataset.cardRewardPhase = state.phase;
    document.body.dataset.cardRewardTargetable = String(state.phase === "ready");
    document.body.dataset.cardBackpackOpen = String(state.backpackOpen);
  }

  function setBackpackOpen(open) {
    state.backpackOpen = Boolean(open && state.collected && state.roamMode);
    backpackElement?.classList.toggle("is-open", state.backpackOpen);
    backpackElement?.setAttribute("aria-hidden", String(!state.backpackOpen));
    publish();
    return state.backpackOpen;
  }

  function resetPresentation() {
    cards.forEach((card, index) => {
      card.material.map = backTexture;
      card.material.color.setHex(0xffffff);
      card.material.opacity = 1;
      card.material.needsUpdate = true;
      card.position.set(0, -0.03, -0.78 - index * 0.012);
      card.rotation.set(0, (index - 2.5) * 0.13, (index - 2.5) * 0.055);
      card.scale.setScalar(0.02);
      card.visible = true;
    });
    glow.material.opacity = 0;
    glow.scale.setScalar(0.4);
    state.frontShown = false;
    state.hovered = false;
  }

  function trigger() {
    if (state.triggered || state.collected) return false;
    state.triggered = true;
    state.phase = "intro";
    state.elapsed = 0;
    resetPresentation();
    group.visible = state.roamMode;
    publish();
    return true;
  }

  function beginReveal() {
    state.phase = "reveal";
    state.elapsed = 0;
  }

  function updateIntro(delta, time) {
    state.elapsed += delta;
    cards.forEach((card, index) => {
      const progress = clamp01((state.elapsed - index * 0.075) / 1.28);
      const eased = easeOutBack(progress);
      const target = targetPositions[index];
      card.position.set(
        target.x * eased + Math.sin(time * 3.2 + index) * (1 - progress) * 0.05,
        target.y * eased + Math.cos(time * 2.7 + index) * (1 - progress) * 0.07,
        THREE.MathUtils.lerp(-0.78 - index * 0.012, target.z, easeOutCubic(progress)),
      );
      card.rotation.y = (1 - progress) * (index % 2 ? -Math.PI * 1.35 : Math.PI * 1.35);
      card.rotation.z = (1 - progress) * (index - 2.5) * 0.36;
      const baseScale = index === 0 ? 1 : 0.76;
      card.scale.setScalar(Math.max(0.01, eased * baseScale));
    });
    if (state.elapsed >= 1.95) beginReveal();
  }

  function updateReveal(delta) {
    state.elapsed += delta;
    const progress = clamp01(state.elapsed / 1.2);
    const center = cards[0];
    const flip = Math.abs(Math.cos(progress * Math.PI));

    if (progress >= 0.48 && !state.frontShown) {
      state.frontShown = true;
      center.material.map = card01Texture;
      center.material.needsUpdate = true;
    }

    center.position.copy(targetPositions[0]);
    center.position.z = THREE.MathUtils.lerp(-1.36, -1.22, easeOutCubic(progress));
    const centerScale = THREE.MathUtils.lerp(1, 1.18, easeOutBack(progress));
    center.scale.set(centerScale * Math.max(0.055, flip), centerScale, centerScale);
    center.rotation.y = 0;
    center.rotation.z = 0;

    cards.slice(1).forEach((card, outerIndex) => {
      const index = outerIndex + 1;
      const target = targetPositions[index];
      card.position.set(
        target.x * (1 + progress * 0.08),
        target.y * (1 + progress * 0.08),
        target.z - progress * 0.08,
      );
      card.scale.setScalar(THREE.MathUtils.lerp(0.76, 0.66, progress));
      card.material.opacity = THREE.MathUtils.lerp(1, 0.68, progress);
      card.rotation.set(0, 0, (index - 3) * 0.035);
    });

    glow.material.opacity = Math.sin(progress * Math.PI) * 0.7 + progress * 0.16;
    glow.scale.setScalar(THREE.MathUtils.lerp(0.45, 1.05, easeOutBack(progress)));
    if (progress >= 1) {
      state.phase = "ready";
      state.elapsed = 0;
      publish();
    }
  }

  function updateReady(delta, time) {
    state.elapsed += delta;
    const center = cards[0];
    const pulse = 1.18 + Math.sin(time * 2.7) * 0.025 + (state.hovered ? 0.07 : 0);
    center.scale.setScalar(pulse);
    center.position.copy(targetPositions[0]);
    center.position.z = -1.22;
    center.material.color.setHex(state.hovered ? 0xfff0b5 : 0xffffff);
    glow.material.opacity = (state.hovered ? 0.5 : 0.22) + Math.sin(time * 3.2) * 0.045;
    glow.scale.setScalar(state.hovered ? 1.13 : 1.02 + Math.sin(time * 2.1) * 0.025);

    cards.slice(1).forEach((card, outerIndex) => {
      const index = outerIndex + 1;
      card.position.y = targetPositions[index].y * 1.08 + Math.sin(time * 1.5 + index) * 0.012;
    });
  }

  function collect() {
    if (state.phase !== "ready" || state.collected) return false;
    state.phase = "collect";
    state.elapsed = 0;
    state.hovered = false;
    state.collectStartPosition.copy(cards[0].position);
    state.collectStartScale.copy(cards[0].scale);
    publish();
    return true;
  }

  function updateCollect(delta) {
    state.elapsed += delta;
    const progress = clamp01(state.elapsed / 0.72);
    const eased = easeOutCubic(progress);
    const center = cards[0];
    center.position.lerpVectors(
      state.collectStartPosition,
      collectTargetPosition,
      eased,
    );
    center.rotation.z = eased * 0.18;
    center.scale.copy(state.collectStartScale).multiplyScalar(Math.max(0.02, 1 - eased));
    glow.material.opacity = (1 - progress) * 0.42;
    cards.slice(1).forEach((card) => {
      card.material.opacity = Math.max(0, 0.68 * (1 - progress));
      card.scale.multiplyScalar(0.94);
    });

    if (progress >= 1) {
      state.collected = true;
      state.phase = "collected";
      group.visible = false;
      setBackpackOpen(true);
      publish();
    }
  }

  function update(delta, time) {
    if (!state.triggered || state.collected || !state.roamMode) return;
    group.visible = true;
    if (state.phase === "intro") updateIntro(delta, time);
    else if (state.phase === "reveal") updateReveal(delta);
    else if (state.phase === "ready") updateReady(delta, time);
    else if (state.phase === "collect") updateCollect(delta);
  }

  function findHit(raycaster) {
    if (state.phase !== "ready" || !group.visible) return null;
    aimBox.setFromObject(cards[0]).expandByScalar(0.2);
    const point = raycaster.ray.intersectBox(aimBox, aimPoint);
    if (!point) return null;
    const distance = raycaster.ray.origin.distanceTo(point);
    return distance <= raycaster.far
      ? {
          type: "reward-card",
          piece: cards[0],
          distance,
          point,
        }
      : null;
  }

  function setHovered(hovered) {
    state.hovered = Boolean(hovered && state.phase === "ready");
  }

  function setMode(mode) {
    state.roamMode = mode === "roam";
    if (!state.roamMode) setBackpackOpen(false);
    group.visible = state.roamMode && state.triggered && !state.collected;
    publish();
  }

  function toggleBackpack() {
    if (!state.collected || !state.roamMode) return false;
    return setBackpackOpen(!state.backpackOpen);
  }

  function getState() {
    return {
      triggered: state.triggered,
      collected: state.collected,
      phase: state.phase,
      targetable: state.phase === "ready",
      hovered: state.hovered,
      backpackOpen: state.backpackOpen,
      visible: group.visible,
    };
  }

  publish();
  return {
    collect,
    findHit,
    getState,
    setHovered,
    setMode,
    toggleBackpack,
    trigger,
    update,
  };
}
