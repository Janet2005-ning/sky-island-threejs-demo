# 项目交接文档

> 文档基准时间：2026-06-30（Asia/Shanghai）  
> 权威状态来源：当前磁盘中的 `models/sky_island_lowpoly.blend`、`public/models/sky_island_lowpoly.glb`、`src/main.js` 和实际运行的 `http://127.0.0.1:5173/`。  
> 重要原则：旧聊天记录和早期策划文档只能辅助理解，若与当前 `.blend`、GLB 或网页代码冲突，以当前文件为准。

## 1. 项目基本信息

- 项目名称：
  - npm 包名：`sky-island-threejs-demo`
  - 当前产品名称：低模卡通天空岛 3D 网页浏览/漫游 Demo
  - 早期文档名称“VR classroom expression training demo”是旧策划名，不代表当前已实现功能。
- 项目目标：
  - 将 Blender 中制作和手工调整的低模卡通天空岛导出为 GLB，在桌面网页中提供全景浏览、第一人称漫游和可点击触发的泉水/荷叶/荷花动画。
  - 当前核心体验是“查看完整天空岛场景、进入漫游、点击唤醒泉水并观看干池到荷花绽放的完整变化”。
- 这个项目最终要解决什么问题：
  - 让没有游戏开发和建模经验的用户也能把 Blender 场景直接用于网页展示。
  - 保留 Blender 手工摆放的模型结果，同时在 Three.js 中增加浏览、漫游、按钮交互和轻量动画。
  - 为后续游戏化交互或作品集演示提供可直接运行的 3D 原型。
- 当前开发阶段：
  - 可运行原型已完成，核心视觉和主要交互已验证。
  - 当前不是完整游戏：没有任务系统、角色、存档、音效、后端、账号、数据库或线上部署。
  - 下一轮工作更适合做视觉微调、性能优化、真实碰撞或扩展互动，而不是重建场景。
- 技术栈：
  - Blender 4.5.4 LTS：模型编辑、材质、GLB 导出、预览图渲染。
  - Python + Blender `bpy`：模型追加、材质重配、动画组件生成、导出。
  - Three.js 0.180.0：GLB 加载、光照、OrbitControls、第一人称相机和动画。
  - Vite 8.1.0：本地开发服务器和生产构建。
  - 原生 HTML/CSS/JavaScript ES Modules：UI 与交互逻辑；没有 React/Vue/TypeScript。
- 运行环境：
  - 操作系统：Windows 11，系统版本 `10.0.22631`。
  - PowerShell：5.1.22621.6133。
  - Node.js：v22.16.0。
  - npm：10.9.2。
  - Blender：`C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`。
  - 本地开发地址：`http://127.0.0.1:5173/`。
  - 2026-06-28 审计时，5173 端口由 Vite 正常监听，页面与 GLB 都返回 HTTP 200。
- 主要依赖：
  - 运行依赖：`three@0.180.0`。
  - 开发依赖：`vite@8.1.0`。
  - Blender Python 使用内置 `bpy`、`mathutils`，不需要 pip 安装。
- 项目所在目录：
  - `D:\aidocument\sky-island-threejs-demo`
- 当前分支或版本状态：
  - 当前目录不是 Git 仓库，没有 `.git`、分支、commit 或 tag。
  - 因此无法通过 Git 判断修改历史、回退或区分用户修改；必须依赖 `.blend` 备份文件和文件时间戳。
  - `package.json` 版本是 `0.0.0`，仅为脚手架版本，不代表正式发布版本。
- 是否有线上部署：
  - 没有发现线上部署、域名、Vercel/Netlify 配置或服务器配置。
  - 当前只有本机 Vite 开发预览。
- 是否涉及数据库：
  - 不涉及。
  - 没有数据库连接、schema、migration、ORM 或本地数据文件。
- 是否涉及第三方 API：
  - 网页运行不调用第三方 API。
  - Blender 生成脚本会读取本机的外部 `.blend` 素材文件，但这不是网络 API。
- 是否涉及敏感配置或密钥：
  - 未发现 `.env`、API Key、Token、密码、私钥或 Cookie。
  - 当前没有需要写成 `[REDACTED]` 的真实密钥。
  - 脚本中存在本机绝对素材路径，但不是认证信息；迁移电脑时需要修改。

## 2. 当前项目进度

### 模块 A：Blender 主场景与权威模型

- 状态：已完成，已验证，可继续手工编辑。
- 相关文件：
  - `models/sky_island_lowpoly.blend`
  - `models/sky_island_lowpoly.blend1`
  - `public/assets/sky_island_blender_preview.png`
- 核心逻辑：
  - `models/sky_island_lowpoly.blend` 是当前唯一权威源文件。
  - 当前场景包含主岛、右侧阶梯岛、远离主岛的小岛、桥、石圈、石堆、两个陶罐、火堆、花草、树、原木长凳以及默认隐藏的泉水动画组件。
  - 2026-06-28 Blender 审计结果：场景 191 个对象，其中 145 个 Mesh、99 个材质。
  - 当前场景存在两个根级空对象 `Sky Island Game Model` 和 `Sky Island Game Model.001`，这是历史生成/手工编辑留下的结构；目前渲染正常，不要在不理解层级的情况下合并或删除。
- 已验证内容：
  - Blender 能以后台模式打开并保存。
  - 能导出 GLB 和 1600×900 Blender 预览图。
  - 网页能加载最新 GLB。
- 当前问题：
  - 模型层级不是完全整洁，存在 `.001` 后缀、多个根对象和一些手工移动后的非统一命名。
  - 没有自动化检查能判断用户在 Blender 中的最新手工调整是否被脚本覆盖。
- 下一步：
  - 每次改模型前先复制备份。
  - 用户在 Blender 中修改后，只运行 `scripts/export_saved_blend.py` 同步网页，不要重新生成整个场景。

### 模块 B：岛屿布局、桥、火堆、植物与长凳

- 状态：已完成，已验证。
- 相关文件：
  - `models/sky_island_lowpoly.blend`
  - `models/qiao.blend`
  - `models/fire.blend`
  - `scripts/append_fire_to_saved_blend.py`
  - `scripts/style_fire_in_saved_blend.py`
  - `scripts/append_garden_plants_to_saved_blend.py`
  - `scripts/append_log_benches_to_saved_blend.py`
  - `scripts/recolor_coral_tree_to_green.py`
- 核心逻辑：
  - 桥来自用户提供的 `qiao.blend`，连接远处小岛和主岛；当前桥面高度已经与两端岛面协调。
  - 火堆来自 `D:\aidocument\fire.blend`，项目中保留副本 `models/fire.blend`；当前放在右侧高岛。
  - 花草树木来自 `D:\aidocument\I216-卡通花园环境\I216-卡通花园环境_BLEND.blend`。
  - 三张浅棕色原木长凳来自 `D:\aidocument\Forest Nature\forest_nature_set_all_in.blend` 的 `Log_small_regular`。
  - 当前 `Imported bright garden plants` 集合有 30 个对象，`Imported light brown log benches` 集合有 3 个对象。
  - 2026-06-28 最新修改：主岛石池旁原来的桃粉色大树 `tree_coral_crown` 已改为三档绿色树冠和三档暖棕色树干/枝条；网页已验证。
- 已验证内容：
  - 桥、火堆、花草、树与长凳均存在于当前 GLB。
  - 最新网页截图显示目标大树已经是绿色树冠、棕色树干。
  - 页面加载无控制台错误。
- 当前问题：
  - 花草和树经历过脚本导入后又被用户手工移动/复制；再次运行植物导入脚本会重置这些手工结果。
  - `append_fire_to_saved_blend.py`、`append_log_benches_to_saved_blend.py` 也会删除同名前缀对象后重新创建，可能覆盖后续手工调整。
- 下一步：
  - 只在用户明确要求“重新生成植物/火堆/长凳”时运行对应脚本。
  - 普通位置或颜色微调优先直接修改当前 `.blend`，然后执行导出脚本。

### 模块 C：Blender 泉水、池水、荷叶与荷花组件

- 状态：已完成，已验证。
- 相关文件：
  - `scripts/add_fountain_animation_components.py`
  - `scripts/export_saved_blend.py`
  - `models/sky_island_lowpoly.blend`
  - `models/sky_island_lowpoly.before_fountain_20260627-214704.blend`
- 核心逻辑：
  - Blender 中独立集合名为 `Fountain_Animation`。
  - 集合包含 43 个对象，并使用稳定的 `FX_` 前缀命名。
  - 主要对象：
    - `FX_Fountain_Animation`
    - `FX_Water_Stream_Upper`
    - `FX_Water_Stream_Lower`
    - `FX_Pond_Water`
    - `FX_Water_Ripple_Inner`
    - `FX_Water_Ripple_Outer`
    - `FX_LilyPad_01` 至 `FX_LilyPad_07`
    - `FX_Lotus_Platform_00`
    - `FX_Lotus_Bud`
    - `FX_Lotus_Bloom_Outer`
    - `FX_Lotus_Bloom_Middle`
    - `FX_Lotus_Bloom_Inner`
    - `FX_Lotus_Bloom_Center`
  - 池中心 Blender 坐标约为 `(4.02, -3.73, 0.245)`；荷花中心约为 `(4.02, -3.66, 0.31)`。
  - 组件在 Blender 视图和渲染中默认隐藏，满足初始干池状态。
  - `export_saved_blend.py` 导出时临时取消隐藏，导出完成后恢复隐藏状态；否则网页 GLB 会缺少这些对象。
- 已验证内容：
  - Blender 集合 `hide_viewport=true`、`hide_render=true`，集合内 43 个对象都默认隐藏。
  - 最新 GLB 有 188 个节点、140 个 mesh、97 个材质，其中 `FX_` 节点 43 个、荷叶 7 个、荷花层 4 个。
  - 水蓝、叶绿、花粉、花心金色材质已正确写入 GLB。
- 当前问题：
  - 如果用户手工修改 `Fountain_Animation` 集合后再运行 `add_fountain_animation_components.py`，该集合会被删除并重建，手工改动会丢失。
- 下一步：
  - 普通同步只运行导出脚本。
  - 只有需要按脚本坐标完整重建泉水组件时，才运行生成脚本。

### 模块 D：网页 3D 加载与浏览模式

- 状态：已完成，已验证。
- 相关文件：
  - `index.html`
  - `src/main.js`
  - `src/style.css`
  - `public/models/sky_island_lowpoly.glb`
- 核心逻辑：
  - `GLTFLoader` 从 `/models/sky_island_lowpoly.glb` 加载模型。
  - 模型加载后开启阴影、平面着色，计算包围盒并设置 `data-ready="true"`。
  - 浏览模式使用 `OrbitControls`，启用阻尼，禁用平移，限制距离和俯仰角。
  - 默认总览相机：位置 `(4.1, 3.15, -7.35)`，目标 `(4.1, 0.3, 4.0)`，FOV 50。
  - 浏览模式下模型根节点有非常轻微的 Y 轴漂移，使画面不完全静止。
- 已验证内容：
  - 最新页面标题为“低模天空岛漫游”。
  - 页面、canvas、模型与按钮均能加载。
  - 2026-06-28 页面和 GLB HTTP 状态均为 200。
- 当前问题：
  - `src/main.js` 单文件约 637 行，场景、输入、漫游和泉水动画全部耦合在一起。
- 下一步：
  - 若继续扩展多个互动，建议拆为 `scene.js`、`movement.js`、`fountain.js`；当前规模仍可运行，不要为重构而重构。

### 模块 E：网页漫游模式

- 状态：已完成，桌面端已验证；跨浏览器和移动端未系统验证。
- 相关文件：
  - `src/main.js`
  - `index.html`
  - `src/style.css`
- 核心逻辑：
  - 点击“漫游”切换到第一人称相机。
  - 支持 WASD、方向键和屏幕方向键移动。
  - 桌面优先使用 Pointer Lock；无法锁定时仍支持按住画布拖动旋转视角。
  - 漫游初始位置为远处小岛 `(10.7, 1.04, 3.55)`，yaw `1.58`，pitch `0.1`；镜头眼高固定为离地 `0.92`。
  - `prepareGroundCollision()` 自动收集 5 个名称含 `grass cap` 的真实草地网格；桥完成后只把真正承载行走的蓝色桥面主板 `BRIDGE_PIECE_01` 纳入脚底射线，避免扶手、桥柱和拱门被误判为高台。
  - `getGroundSample()` 从候选位置向下射线，只接受朝上的真实网格面；无地面时拒绝移动，不能穿出岛边或掉进空中。
  - `tryMovePlayerTo()` 限制单级上升 `0.46`、下降 `0.58`；相机 Y 以阻尼跟随地面高度，走三级台阶时有连续抬升感。
- 已验证内容：
  - 模式切换、键盘移动、方向键 UI 和重置视角已经在浏览器验证中正常工作。
  - 自动台阶路线依次命中主岛、低台阶、中台阶和高岛，地面 Y 为 `0.12 → 0.284 → 0.50 → 0.80`；最终相机 Y 为 `1.72`，始终保持相同眼高。
  - 高岛外侧无草地处移动被拒绝；桥完成前中央无地面，完成后命中 `BRIDGE_PIECE_01`，地面 Y 约 `0.119`。
- 当前问题：
  - 当前是足点地面射线，不是胶囊体；不会跌落或穿过地面，但不会阻挡树木、石池和栏杆等竖直装饰物。
- 下一步：
  - 若以后需要角色体积和竖直障碍物碰撞，再引入胶囊体/空间索引；仅移动现有草地与桥网格无需维护手工区域坐标。

### 模块 F：网页泉水与荷花按钮动画

- 状态：已完成，已验证，可重复播放。
- 相关文件：
  - `index.html`
  - `src/main.js`
  - `src/style.css`
  - `public/models/sky_island_lowpoly.glb`
- 核心逻辑：
  - 按钮 ID：`#fountain-animation`，模型就绪后初始文字为“1/7 唤醒泉水”；每次鼠标左键只播放一段，片段结束自动暂停并提示下一段。
  - 模型加载完成前按钮禁用；缺少关键 `FX_` 对象时显示“泉水组件缺失”。
  - 总时长仍为 11.4 秒，但拆成 7 个独立区间：
    - `0–0.8s`：唤醒泉水。
    - `0.8–2.2s`：流出水柱。
    - `2.2–3.35s`：水柱扩散。
    - `3.35–4.8s`：池水上涨。
    - `4.8–7.0s`：荷叶生长。
    - `7.0–8.6s`：荷花花苞。
    - `8.6–11.4s`：荷花盛开。
    - 第 7 段完成后按钮改为“已完成 · 重新唤醒”，再次点击会重置干池并只播放第 1 段。
  - 浏览模式点击时仍会聚焦池子，位置 `(3.05, 3.0, -1.82)`，目标 `(3.18, 0.56, 3.72)`，FOV 46。
  - 浏览模式仍可使用泉水按钮；漫游模式隐藏按钮，必须用左右任一 VR 手射线命中泉水模型后单击触发，不切换模式、不接管相机。
  - 流水由多段 mesh 依次显示；池水由缩放与透明度模拟填充；荷叶使用错峰回弹；花苞淡入后淡出，四层花瓣依次展开。
  - 完成后水面、荷叶、水波和流水仍有轻微循环运动。
  - 调试接口：`window.__FOUNTAIN_STATE__()` 和 `window.__FOUNTAIN_SEEK__(seconds)`。
- 已验证内容：
  - 实际网页已逐阶段截图验证水、7 片荷叶、花苞、四层粉色荷花和最终持续流水。
  - 7 次左键依次停在 `0.8 / 2.2 / 3.35 / 4.8 / 7.0 / 8.6 / 11.4` 秒；每段结束均为 `playing=false`，不会自动串播下一段。
  - 第 7 段完成后计数为 `7/7`；再次点击能从第 1 段重新开始。
  - 漫游中启动后 `mode=roam`、`startedMode=roam`；动画播放期间浏览器实测 yaw/pitch 和玩家 X/Z 坐标均可继续变化。
  - 控制台没有项目错误或警告。
- 当前问题：
  - 动画是 Three.js 中的程序时间轴，不是 Blender Action/骨骼动画。
  - 页面后台休眠后恢复时，单帧动画增量最多 0.25 秒，避免瞬间跳到终态；极低帧率下仍可能略有节奏差异。
- 下一步：
  - 若要改变节奏，优先修改 `getFountainPhase()` 和 `applyFountainTimeline()` 的时间点，不要改 Blender 坐标。

### 模块 G：Blender 到网页的同步/导出流程

- 状态：已完成，已验证，是后续最重要的维护流程。
- 相关文件：
  - `scripts/export_saved_blend.py`
  - `models/sky_island_lowpoly.blend`
  - `public/models/sky_island_lowpoly.glb`
  - `public/assets/sky_island_blender_preview.png`
- 核心逻辑：
  - 从当前保存的 `.blend` 直接导出网页 GLB，不重建岛屿。
  - 导出使用 Y-up、应用变换、导出材质，不导出 Blender 相机和灯光。
  - 同时用 Eevee Next 渲染 1600×900 预览图。
  - 导出时临时显示 `Fountain_Animation`，之后恢复隐藏。
  - 导出时也临时显示 6 个隐藏的桥组成员，保证 GLB 包含全部 12 个桥构件；导出后恢复 Blender 初态。
- 已验证内容：
  - 2026-06-28 最新导出成功。
  - 最新 GLB 约 2.39 MB，网页正常加载。
- 当前问题：
  - 导出脚本没有自动做备份；备份必须在运行修改脚本前手工创建。
- 下一步：
  - 所有 Blender 手工编辑后的网页同步都使用这一脚本。

### 模块 H：Blender 六款式积木桥与网页整组归位动画

- 状态：已完成，已验证；天空仅显示 6 个颜色款式代表块，点击后整组构件恢复原桥。
- 相关文件：
  - `scripts/setup_bridge_puzzle.py`
  - `models/sky_island_lowpoly.blend`
  - `models/sky_island_lowpoly.before_bridge_puzzle_20260628-161833.blend`
  - `public/models/sky_island_lowpoly.glb`
  - `index.html`
  - `src/main.js`
  - `src/style.css`
- Blender 核心逻辑：
  - 原 `qiao.blend` 桥的 12 个既有网格没有被替换，而是稳定重命名为 `BRIDGE_PIECE_01` 至 `BRIDGE_PIECE_12`。
  - 每块对应一个 `BRIDGE_TARGET_01` 至 `BRIDGE_TARGET_12` 空对象；目标节点保存改造前原桥的最终位置、旋转和缩放。
  - 12 个桥块按当前 GLB 真实材质/款式分成 6 组：蓝色 `01`；红色 `02–05`；绿色 `06–07`；粉色 `08–09`；黄色 `10`；橙色 `11–12`。
  - `.blend` 初态只显示代表块 `01、02、06、08、10、11`；其余 6 个同组构件位于各自目标位并隐藏，因此天空严格只有 6 块且桥面缺口没有可见连接。
  - `export_saved_blend.py` 导出时临时显示全部 12 个桥网格，确保网页能在落地时显示隐藏组员；导出后恢复 Blender 的 6 显示/6 隐藏状态。
  - `Bridge_Puzzle_Guides` 集合保存目标空对象，`BRIDGE_PUZZLE_ROOT` 是桥父节点。
- 网页核心逻辑：
  - `prepareBridgePuzzle()` 按稳定名称绑定 12 块、12 个目标节点和 6 个款式组，并只保留每组代表块可见/可拾取。
  - 漫游时 6 个代表块持续轻微上下漂浮；准星对准后发光，鼠标左键或 E/回车/空格触发约 1.05–1.23 秒弧线归位。
  - 代表块落地时，同组全部成员一次性显示，并逐件强制写入各自目标节点的精确局部 position/quaternion/scale。
  - 进度面板显示 `0 / 6` 到 `6 / 6`；全部完成后提示“桥梁搭建完成，现在可以走到对岸”。
  - 桥面 `walkZone` 带 `requiresBridge`，6 个款式组未完成前禁止通过，完成后才开放。
  - 调试接口：`window.__BRIDGE_STATE__()`、`window.__BRIDGE_RESET__()`、`window.__BRIDGE_ASSEMBLE__(index)`、`window.__BRIDGE_ASSEMBLE_ALL__()`；`?bridge-debug=1` 下可按 B 做全量验收，普通页面无此快捷键。
- 已验证内容：
  - GLB 中有 12 个 `BRIDGE_PIECE_*` mesh 节点和 12 个 `BRIDGE_TARGET_*` 节点。
  - Blender 当前有 12 个桥网格、6 个代表块可见、6 个同组成员隐藏，组 ID 为 1–6。
  - 网页初态进度 `0 / 6`，总览画面严格只有 6 个悬浮款式代表块。
  - 严格顺序模式下点击蓝色代表块后进度变为 `1 / 6`，下一组切换为绿色；整组真实桥件在动画结束后同时出现在各自目标桥位。
  - 全量验收后进度为 `6 / 6`、`data-bridge-complete="true"`，网页全景显示原桥完整连接两岛。
  - 隐藏组员在 GLB 中与对应目标节点的最大变换误差小于 `3.2e-8`。
  - 当前目标矩阵与改造前备份逐件比较，最大绝对误差小于 `1.8e-7`，属于 Blender 浮点保存误差。
- 维护注意：
  - 普通同步仍只运行 `scripts/export_saved_blend.py`。
  - 不要删除或随意重命名 `BRIDGE_PIECE_*`、`BRIDGE_TARGET_*`、`BRIDGE_PUZZLE_ROOT`。
  - 在 Blender 调整最终桥形时，应移动对应 `BRIDGE_TARGET_*`；调整漂浮初态时才移动 `BRIDGE_PIECE_*`。
  - 只有明确要按脚本预设重新布置散件时才运行 `setup_bridge_puzzle.py`；它会重置六组映射、6 个代表块悬浮坐标和 6 个隐藏成员状态。

### 模块 I：早期策划、已放弃或未实现方案

- 状态：旧规划保留，但当前未实现或已废弃。
- 相关文件：
  - `docs/interaction_flow.md`
  - `docs/10_day_schedule.md`
  - `docs/model_list.md`
  - `docs/recording_checklist.md`
  - `PRODUCTION_README.md`
- 核心逻辑：
  - 这些文档描述 Claim/Evidence/Reasoning 方块、VR 手、奖励卡和课堂表达训练流程。
  - 当前代码仍未实现旧课堂方案中的表达方块、任务判定、奖励卡或相机飞行动画；但“修改 17”已经为当前积木桥与泉水玩法加入独立的 VR 模拟双手和射线交互，不能再笼统视为没有 VR 手。
- 已废弃/被取代的需求：
  - 云朵模型已明确移除，不要重新加回。
  - 早期程序生成的错误桥方案已删除，后来改用用户提供的 `qiao.blend`。
  - “清除所有植物”是较早阶段要求，后来用户又明确添加花园植物；当前真实状态包含植物，不要依据旧要求再次清空。
  - 仅在 Three.js 中临时生成泉水几何的狭窄方案没有采用；最终方案是在 Blender 中建立独立组件，再由网页控制动画。
- 哪些方案已经证明不可行或不应重复：
  - 运行 `create_sky_island_model.py` 重新构建整个场景会覆盖用户在 Blender 中的手工调整，不可作为普通更新方式。
  - 直接把泉水集合永久设为可见会破坏 Blender 初始干池预览；永久隐藏又会导致常规导出遗漏，因此必须使用“导出时临时显示”的现有逻辑。
  - 只修改材质 `diffuse_color` 在 Blender 中文界面/节点材质下曾导出成白色；有效方案是按节点类型 `BSDF_PRINCIPLED` 找到 Principled BSDF，并写入节点输入。

### 功能验证状态汇总

- 已验证可用：
  - Blender 主文件打开/保存。
  - GLB 导出和 Blender 预览图生成。
  - Vite 开发服务器。
  - 页面、模型、canvas、浏览/漫游/重置按钮。
  - 泉水完整阶段动画和重复播放。
  - 积木桥 6 个款式代表块的高亮、整组归位、完整拼桥与完成状态。
  - 最新目标树的绿色树冠与棕色树干。
  - `npm run build`。
- 已写代码但没有全面验证：
  - CSS 的所有移动端尺寸；只做了响应式规则，没有完整手机设备矩阵测试。
  - Pointer Lock 在所有浏览器中的一致性。
  - `npm run preview` 生产预览命令本次没有实际启动验证。
- 写到一半的功能：
  - 当前主线没有已知“半写完但会自动执行”的功能。
  - 早期 VR 课堂流程是策划，不是半成品实现。
- 不要让新 AI 重复尝试：
  - 不要运行全量重建脚本来同步用户手工 Blender 改动。
  - 不要重新导入植物/长凳/火堆，除非用户明确要求重置这些资产。
  - 不要重新加入云朵。
  - 不要把旧 `docs/interaction_flow.md` 当成当前产品功能清单。

## 3. 文件结构说明

- `package.json`
  - 作用：定义 npm 包、Vite 命令和 Three.js/Vite 依赖。
  - 当前状态：有效，已验证。
  - 最重要配置：`dev`、`build`、`preview`、`static` scripts。
  - 修改注意：`static` 当前只是从项目根目录启动 Python 静态服务，不能替代 Vite 的 public 目录映射；不要作为推荐启动方式。
- `package-lock.json`
  - 作用：锁定 npm 依赖版本。
  - 当前状态：有效；`npm list --depth=0` 显示 Three.js 0.180.0、Vite 8.1.0。
  - 修改注意：只通过 npm 命令更新，不要手工编辑。
- `index.html`
  - 作用：网页入口、canvas 容器、加载遮罩、模式工具栏、泉水按钮、积木桥进度面板/准星、漫游方向键。
  - 当前状态：有效，UTF-8 中文在浏览器中显示正确。
  - 最重要元素：`#app`、`#loader-status`、`#browse-mode`、`#roam-mode`、`#fountain-animation`、`#bridge-puzzle-panel`、`#bridge-crosshair`、`#reset-camera`、`#move-pad`。
  - 修改注意：PowerShell 读取时必须使用 `Get-Content -Encoding utf8`，否则终端可能显示乱码，但文件本身不是乱码。
- `src/main.js`
  - 作用：整个网页 3D 应用的核心入口与业务逻辑。
  - 当前状态：有效，约 1119 行，构建通过。
  - 最重要函数：
    - `setupLighting()`：灯光。
    - `loadModel()`：GLB 加载、材质/阴影初始化、debug 状态。
    - `setMode()`：浏览/漫游切换。
    - `updatePlayer()`、`isWalkable()`：移动与区域碰撞。
    - `prepareFountainAnimation()`：按对象名绑定泉水组件。
    - `applyFountainTimeline()`：泉水动画时间轴。
    - `animateFountainSurface()`：终态循环运动。
    - `startFountainAnimation()`、`completeFountainAnimation()`：开始/完成/重播。
    - `prepareBridgePuzzle()`、`assembleBridgePiece()`、`updateBridgePuzzle()`：桥块绑定、拾取与归位时间轴。
    - `updateBridgeHover()`、`selectBridgePiece()`：漫游准星高亮和点击选择。
    - `animate()`：主渲染循环。
  - 修改注意：Blender 对象名是 Three.js 绑定契约；重命名 `FX_`、`BRIDGE_PIECE_` 或 `BRIDGE_TARGET_` 对象后必须同步修改这里。
- `src/style.css`
  - 作用：全屏 canvas、HUD、按钮、积木桥进度/准星、方向键、加载遮罩和响应式样式。
  - 当前状态：有效，构建通过。
  - 最重要规则：`.hud`、`.toolbar`、`.fountain-button`、`.bridge-puzzle-panel`、`.bridge-crosshair`、`.move-pad`、`body[data-mode]`、`@media (max-width: 720px)`。
  - 修改注意：底部工具栏和移动方向键不能相互遮挡；移动端改动后要截图验证。
- `src/counter.js`
  - 作用：Vite 模板遗留的计数器代码。
  - 当前状态：未被当前入口引用，可视为无用文件。
  - 修改注意：可在清理时删除，但不是当前风险。
- `src/assets/`
  - 作用：包含 Vite 模板遗留 SVG 和 `hero.png`。
  - 当前状态：当前 3D 页面没有使用这些模板资产，是否全部可删需再查引用。
- `models/sky_island_lowpoly.blend`
  - 作用：当前 Blender 权威源文件。
  - 当前状态：最新，约 6.13 MB，最后修改时间 2026-06-28 16:37。
  - 重要内容：所有岛屿、积木桥块/目标、火堆、植物、长凳、泉水组件和用户手工调整。
  - 修改注意：任何脚本执行前先备份；不要用旧脚本覆盖。
- `models/sky_island_lowpoly.blend1`
  - 作用：Blender 自动备份。
  - 当前状态：时间对应泉水完成前后的状态；不是当前权威文件。
  - 修改注意：只用于紧急恢复。
- `models/sky_island_lowpoly.before_bridge_puzzle_20260628-161833.blend`
  - 作用：积木桥改造前的原桥权威备份，用于核对原始桥形和目标矩阵。
  - 当前状态：已用于逐件矩阵审计，必须保留。
- `models/sky_island_lowpoly.before_six_bridge_groups_20260628-210007.blend`
  - 作用：从 12 个漂浮块改为 6 个款式代表块之前的备份。
  - 当前状态：有效恢复点，必须保留。
- `models/sky_island_lowpoly.before_sparse_garden.blend`
  - 作用：稀疏花园导入前备份。
  - 当前状态：历史备份。
- `models/sky_island_lowpoly.before_bright_garden.blend`
  - 作用：亮色花园版本前备份。
  - 当前状态：历史备份。
- `models/sky_island_lowpoly.before_log_benches.blend`
  - 作用：原木长凳导入前备份。
  - 当前状态：历史备份。
- `models/sky_island_lowpoly.before_fountain_20260627-214704.blend`
  - 作用：泉水动画组件创建前备份。
  - 当前状态：重要恢复点。
- `models/sky_island_lowpoly.before_green_tree_20260628-154418.blend`
  - 作用：目标大树改绿前备份。
  - 当前状态：最新重要恢复点。
- `models/qiao.blend`
  - 作用：桥的源模型。
  - 当前状态：已用于当前场景。
  - 修改注意：当前桥已经在主 `.blend` 内，普通导出不需要再次读取此文件。
- `models/fire.blend`
  - 作用：火堆源模型项目副本。
  - 当前状态：已用于当前场景。
- `public/models/sky_island_lowpoly.glb`
  - 作用：网页实际加载的生产 3D 资源。
  - 当前状态：最新，约 2.39 MB，HTTP 200。
  - 修改注意：不能只改 `.blend` 而不重新导出；网页不会直接读取 `.blend`。
- `public/assets/sky_island_blender_preview.png`
  - 作用：Blender 自动总览预览图。
  - 当前状态：最新，已显示绿色目标树。
- `public/assets/garden_asset_catalog.png`
  - 作用：花园素材候选目录图。
  - 当前状态：参考资产，不参与网页主场景逻辑。
- `public/assets/garden_tree_catalog.png`
  - 作用：树木素材候选目录图。
  - 当前状态：参考资产。
- `public/assets/panorama.png`、`public/assets/first-person.png`
  - 作用：早期视觉参考图。
  - 当前状态：当前代码未作为主要渲染输入。
- `scripts/export_saved_blend.py`
  - 作用：从当前保存的 Blender 文件导出 GLB，并渲染预览图。
  - 当前状态：推荐且已验证的日常同步脚本。
  - 最重要函数：`reveal_animation_components_for_export()`、`reveal_bridge_pieces_for_export()`、`restore_bridge_piece_visibility()`、`export_glb()`、`render_preview()`。
  - 修改注意：不能删除临时显示泉水集合和隐藏桥组成员的逻辑，否则 GLB 会缺少运行时组件。
- `scripts/add_fountain_animation_components.py`
  - 作用：在 Blender 中创建两股流水、池水、水波、7 片荷叶、花苞和四层荷花。
  - 当前状态：已执行并验证。
  - 最重要函数：`create_stream()`、`make_ellipse_disc()`、`make_lily_pad()`、`create_petal_layer()`、`create_lotus()`、`mark_default_hidden()`。
  - 修改注意：会删除并重建 `Fountain_Animation`，不是普通导出脚本。
- `scripts/recolor_coral_tree_to_green.py`
  - 作用：将 `tree_coral_crown` 的三个树冠 part 改为绿色，将 trunk part 改为棕色，并保持低模分面。
  - 当前状态：2026-06-28 已执行并验证。
  - 最重要函数：`require_materials()`、`assign_palette()`。
  - 修改注意：依赖当前对象名和既有花园材质名；对象重命名后会明确报错。
- `scripts/append_fire_to_saved_blend.py`
  - 作用：从 `D:\aidocument\fire.blend` 追加火堆，复制源文件到项目并放在指定位置。
  - 当前状态：已执行；当前场景已有火堆。
  - 修改注意：会删除已有同名前缀火堆并重建，可能覆盖手工调整。
- `scripts/style_fire_in_saved_blend.py`
  - 作用：给已导入火焰、木头、石圈和灰烬重配低模材质。
  - 当前状态：已执行。
  - 修改注意：依赖火堆对象命名规则。
- `scripts/append_garden_plants_to_saved_blend.py`
  - 作用：从 I216 花园素材包导入 3 棵树和 8 组花草，创建亮色平面材质并按岛面高度放置。
  - 当前状态：已执行；当前场景之后又有手工移动/复制。
  - 修改注意：会删除 `Imported bright garden plants` 后重建，普通维护中不要再次运行。
- `scripts/append_log_benches_to_saved_blend.py`
  - 作用：从 Forest Nature 素材包导入 3 张浅棕原木长凳。
  - 当前状态：已执行。
  - 修改注意：会删除同集合和同前缀对象后重建。
- `scripts/setup_bridge_puzzle.py`
  - 作用：把当前 `qiao.blend` 桥的 12 个现有网格转换为稳定命名积木块，创建目标空对象，建立 6 个材质款式组，并写入 6 显示/6 隐藏的初态。
  - 当前状态：2026-06-28 已执行并验证；当前 `.blend` 已是脚本执行后的权威状态。
  - 最重要函数：`ensure_target()`、`scatter_piece()`、`main()`。
  - 修改注意：重跑会按脚本坐标重置所有桥块的悬浮初态；普通同步不要运行。
- `scripts/create_sky_island_model.py`
  - 作用：早期从零程序化生成岛屿、石圈、陶罐、桥等，并直接保存/导出。
  - 当前状态：历史生成脚本；与当前手工模型不完全一致。
  - 最重要函数：`clear_scene()`、`make_island()`、`populate_main()`、`append_qiao_bridge()`、`save_outputs()`。
  - 修改注意：高危。`clear_scene()` 会清空当前场景；绝不能用于同步现有手工 `.blend`。
- `scripts/render_garden_asset_catalog.py`
  - 作用：渲染花园素材目录图。
  - 当前状态：诊断/选材工具，主运行流程不需要。
- `scripts/render_garden_tree_catalog.py`
  - 作用：渲染树木素材目录图。
  - 当前状态：诊断/选材工具。
- `docs/interaction_flow.md`
  - 作用：早期 VR 课堂互动策划。
  - 当前状态：过期规划，不是当前实现说明。
- `docs/model_list.md`
  - 作用：早期模型清单与命名建议。
  - 当前状态：部分可参考，实际对象名以 Blender/GLB 为准。
- `docs/10_day_schedule.md`
  - 作用：早期 10 天制作计划。
  - 当前状态：历史计划。
- `docs/recording_checklist.md`
  - 作用：浏览器录屏和 AE 后期检查表。
  - 当前状态：如需作品集录屏仍可使用。
- `PRODUCTION_README.md`
  - 作用：早期生产流程入口。
  - 当前状态：部分路径和目标名已经过期，优先阅读本交接文档。
- `dist/`
  - 作用：`npm run build` 生成的生产静态文件。
  - 当前状态：最新构建通过，包含 GLB 与静态资产；被 `.gitignore` 忽略。
  - 修改注意：不要手工改，重新构建即可覆盖。
- `dev-server*.log`、`vite.*.log`
  - 作用：历史或当前 Vite 日志。
  - 当前状态：可用于排查端口与启动问题；被 `.gitignore` 忽略。
- API 路由文件：不存在。
- 数据库文件：不存在。
- 自动化测试文件：不存在。
- 部署配置文件：不存在。

## 4. 核心逻辑说明

### 4.1 用户从哪里进入

1. 用户打开 `http://127.0.0.1:5173/`。
2. Vite 返回 `index.html`，随后浏览器加载 `src/main.js` 和 `src/style.css`。
3. `main.js` 创建 Three.js 场景、相机、WebGLRenderer、OrbitControls 和灯光。
4. 页面开始显示全屏“加载天空岛”遮罩。
5. `GLTFLoader` 请求 `/models/sky_island_lowpoly.glb`。
6. 模型成功后，代码设置阴影/平面着色、绑定泉水与积木桥组件、计算包围盒、移除加载遮罩并重置总览相机。

### 4.2 Blender 数据如何进入网页

1. 用户或脚本修改 `models/sky_island_lowpoly.blend`。
2. 必须先在 Blender 保存。
3. 运行 `scripts/export_saved_blend.py`。
4. 脚本临时显示 Blender 中默认隐藏的 `Fountain_Animation`。
5. Blender glTF 导出器生成 `public/models/sky_island_lowpoly.glb`。
6. 脚本恢复泉水集合隐藏状态，再渲染 `public/assets/sky_island_blender_preview.png`。
7. Vite 的 `public` 目录把 GLB 映射为网页 `/models/sky_island_lowpoly.glb`。
8. 页面刷新后加载新 GLB。

这样设计的原因：用户会直接在 Blender 里手工摆放模型，因此 `.blend` 必须是权威源；网页只负责运行时交互，不应该反向重建 Blender 场景。

### 4.3 浏览模式

- `mode === "browse"` 时启用 OrbitControls。
- 鼠标拖动旋转，滚轮缩放；不能平移，避免把模型移出画面。
- `resetOverviewCamera()` 回到预设总览视角。
- 模型根节点有极小的正弦旋转，增加活感。

### 4.4 漫游模式

- `setMode("roam")` 禁用 OrbitControls，调用 `resetPlayer()`。
- 键盘、方向键 UI 更新 `keys`/`pressedPadKeys`。
- `updatePlayer()` 根据 yaw 计算前进/右移向量。
- `getGroundSample()` 对真实草地/桥面网格向下射线，`tryMovePlayerTo()` 同时检查是否有地面和相邻高度是否可跨越。
- 若完整移动被阻挡，会尝试只移动 X 或只移动 Z，减少卡边；无真实地面则保持原位。
- `applyPlayerCamera()` 每帧写入坐标和朝向；相机 Y 阻尼跟随 `groundY + eyeHeight`。

容易出 bug 的地方：草地节点名必须继续包含 `grass cap`（空格和下划线均可）；桥件必须保持 `BRIDGE_PIECE_*` 命名，否则不会进入地面候选。

### 4.5 泉水动画

- Blender 只提供分离且可命名的静态低模组件；网页负责时间轴。
- `prepareFountainAnimation()` 通过名字查找所有组件。如果 7 片荷叶或 4 层花缺失，按钮保持不可用。
- `cloneFxMaterials()` 为动画对象克隆材质，避免改透明度时污染别的模型。
- `resetFountainVisuals()` 隐藏水、叶、花，恢复干池。
- `applyFountainTimeline(time)` 根据时间计算每一组对象的透明度、缩放和旋转。
- `animateFountainSurface()` 在主动画完成后继续做水波、荷叶漂浮和流水亮度变化。
- `startFountainAnimation()` 播放 `nextSegmentIndex` 指向的单段；`completeFountainSegment()` 在段尾暂停并把按钮推进到下一段。只有完成 7 段后再点击才会重置为干池并重播第 1 段。
- `focusFountainCamera()` 只在浏览模式生效；漫游中改由任一 VR 手射线点击泉水启动，模式和第一人称相机都不会被重置。

这样设计的原因：

- Blender 中需要保留可编辑的低模资产。
- Three.js 时间轴更容易由按钮控制、重复播放、调节阶段，也不依赖 Blender 动画剪辑导出兼容性。
- 用对象名作为绑定契约比按节点序号可靠，但也意味着不能随意重命名。

### 4.6 六款式积木桥动画

- Blender 提供 12 个真实桥网格、12 个目标空对象和 6 个可见款式代表；网页不临时生成替代桥。
- `prepareBridgePuzzle()` 建立桥块—目标—款式组映射，`updateBridgePuzzle()` 只驱动 6 个代表块漂浮和真实时间归位动画。
- 高亮与点击使用同一组未归位桥块射线结果；Pointer Lock 下优先操作当前高亮块，避免点击事件移动指针后重新射线导致失选。
- `completeBridgePiece()` 在代表块落地时显示该组全部成员并逐件精确复制目标变换；6 组完成后开放桥面通行区。

### 4.7 当前技术债和临时方案

- `src/main.js` 仍是单文件，没有模块化。
- 漫游碰撞是手工区域，不是真实网格碰撞。
- Blender 场景层级有历史重复根和后缀对象。
- 没有测试框架，验证主要靠 `npm run build`、HTTP 状态、浏览器截图和 console logs。
- 外部 Blender 素材路径硬编码在脚本中，换电脑后需要修改。
- 初始策划文档与当前产品方向不同，必须避免误读。

## 5. 环境变量与配置

- `无必填环境变量`
  - 用途：当前前端不读取 `import.meta.env`，也没有后端密钥。
  - 是否必填：否。
  - 示例值：不适用。
  - 缺失会导致什么问题：不会导致问题。
- `.env`
  - 检查结果：不存在。
- `.env.example`
  - 检查结果：不存在。
- `vite.config.*`
  - 检查结果：不存在；项目使用 Vite 默认配置。
- 数据库连接配置
  - 检查结果：不存在。
- API 配置
  - 检查结果：不存在。
- 代理配置
  - 检查结果：不存在。
- 部署配置
  - 检查结果：不存在。

非环境变量但必须知道的硬编码配置：

- `MODEL_URL`
  - 实际位置：`src/main.js` 中硬编码 `/models/sky_island_lowpoly.glb`。
  - 是否必填：是，文件必须存在于 `public/models/`。
  - 缺失影响：加载遮罩会显示模型加载失败，页面没有 3D 场景。
- `BLENDER_EXE`
  - 实际路径：`C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`。
  - 是否必填：只有执行 Blender 后台脚本时需要。
  - 缺失影响：无法通过命令行导出 GLB；仍可手工打开 Blender。
- `SOURCE_FIRE_PATH`
  - 实际路径：`D:\aidocument\fire.blend`。
  - 是否必填：只有重新导入火堆时需要。
  - 缺失影响：`append_fire_to_saved_blend.py` 报错；当前主 `.blend` 中已有火堆，不影响网页。
- `GARDEN_SOURCE_BLEND`
  - 实际路径匹配：`D:\aidocument\I216-*\I216-*_BLEND.blend`。
  - 是否必填：只有重新导入花园资产时需要。
  - 缺失影响：植物导入脚本报错；当前网页不受影响。
- `FOREST_SOURCE_BLEND`
  - 实际路径：`D:\aidocument\Forest Nature\forest_nature_set_all_in.blend`。
  - 是否必填：只有重新生成长凳时需要。
  - 缺失影响：长凳导入脚本报错；当前网页不受影响。

## 6. 启动、运行、测试方式

### 1. 进入项目

```powershell
Set-Location 'D:\aidocument\sky-island-threejs-demo'
```

- 状态：已验证。

### 2. 安装依赖

```powershell
npm install
```

- 状态：命令是标准安装方式；本次未重新安装，但现有 `node_modules` 已通过 `npm list --depth=0` 验证。
- 预期依赖：`three@0.180.0`、`vite@8.1.0`。

### 3. 启动前端开发服务器

```powershell
npm run dev
```

- 状态：已验证。
- 默认地址：`http://127.0.0.1:5173/`。
- 如果 5173 已占用：

```powershell
npm run dev -- --host 127.0.0.1 --port 5174
```

- 启动成功后应该看到：
  - 蓝色天空背景和完整浮岛。
  - 左下角“模式/浏览”。
  - 右下角“浏览”“漫游”“唤醒泉水”和重置按钮。
  - 初始石池为空；点击“唤醒泉水”后开始动画。
  - 桥梁初始为空，6 个颜色款式代表积木悬浮在两岛附近；点击代表块后该款式全部桥件同时显现。

### 4. 后端启动命令

- 不存在后端，无需启动。

### 5. 数据库启动方式

- 不涉及数据库，无需启动。

### 6. 用户在 Blender 手工修改后的正确同步命令

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' `
  --background 'D:\aidocument\sky-island-threejs-demo\models\sky_island_lowpoly.blend' `
  --python 'D:\aidocument\sky-island-threejs-demo\scripts\export_saved_blend.py'
```

- 状态：已验证，是推荐工作流。
- 结果：
  - 更新 `public/models/sky_island_lowpoly.glb`。
  - 更新 `public/assets/sky_island_blender_preview.png`。
  - 不会重建岛屿，也不会保存脚本临时取消隐藏的泉水状态。

### 7. 重新生成泉水组件

只有用户明确要求按脚本完整重建泉水时才运行：

```powershell
Copy-Item '.\models\sky_island_lowpoly.blend' '.\models\sky_island_lowpoly.before_fountain_regen.blend'
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' `
  --background '.\models\sky_island_lowpoly.blend' `
  --python '.\scripts\add_fountain_animation_components.py'
```

- 状态：已验证。
- 风险：会删除并重建整个 `Fountain_Animation` 集合。
- 运行后还要执行第 6 步导出。

### 8. 重新应用目标树绿色/棕色配色

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' `
  --background '.\models\sky_island_lowpoly.blend' `
  --python '.\scripts\recolor_coral_tree_to_green.py'
```

- 状态：已验证。
- 前提：对象名和花园材质名没有被改动。
- 运行后还要执行第 6 步导出。

### 9. 构建生产版本

```powershell
npm run build
```

- 状态：2026-06-28 已验证通过。
- 输出：`dist/`。
- 当前输出大小：JS 约 607.01 kB（gzip 154.49 kB），CSS 约 4.98 kB，GLB 约 2.39 MB。
- 当前只有 chunk 超过 500 kB 的警告，不是构建失败。

### 10. 预览生产构建

```powershell
npm run preview -- --host 127.0.0.1
```

- 状态：未验证。
- Vite 默认通常使用 4173 端口；具体地址以终端输出为准。

### 11. 测试命令

- `package.json` 没有 `test`、`lint` 或 `typecheck` 脚本。
- 当前有效验证流程：

```powershell
npm run build
Invoke-WebRequest 'http://127.0.0.1:5173/' -UseBasicParsing
Invoke-WebRequest 'http://127.0.0.1:5173/models/sky_island_lowpoly.glb' -Method Head -UseBasicParsing
```

- 浏览器人工验证：
  - 初始干池。
  - 浏览模式可旋转缩放。
  - 漫游模式可移动。
  - 泉水动画依次出现流水、池水、荷叶、花苞、盛开。
  - 完成后“再次绽放”可重播。
  - 检查 console error/warn。

### 12. 部署命令

- 当前没有部署脚本。
- 可行但未验证的方式：运行 `npm run build` 后，将整个 `dist/` 目录上传到支持静态站点和根路径资源的托管服务。
- 必须确认部署后 `/models/sky_island_lowpoly.glb` 能直接访问。

### 13. 常见启动失败原因

- 5173 端口已有服务：换端口或停止旧 Vite 进程。
- 只打开 `index.html`：ES Module、GLB 路径和浏览器安全策略可能失败，应使用 Vite。
- 使用 `npm run static`：从项目根目录启动 Python 静态服务器时，`/models/...` 不会自动映射到 `public/models/...`，不推荐。
- GLB 未更新：确认先保存 `.blend`，再运行 `export_saved_blend.py`。
- 泉水按钮显示组件缺失：检查 GLB 是否含完整 `FX_` 节点、导出脚本是否临时显示了隐藏集合。
- Blender 命令找不到：检查 Blender 安装路径和版本。
- PowerShell 显示中文乱码：读取文件时加 `-Encoding utf8`；浏览器中文目前正常。

## 7. 已知问题与坑

### 问题：全量生成脚本会覆盖当前手工模型

- 表现：运行 `create_sky_island_model.py` 后，用户在 Blender 中手工移动、复制、缩放、改材质的内容可能消失。
- 可能原因：脚本包含 `clear_scene()`，设计目标是从零重建，不是增量同步。
- 已尝试方案：早期使用全量脚本快速生成场景。
- 有效方案：把当前 `.blend` 当权威源，只使用 `export_saved_blend.py` 导出。
- 无效方案：用户改完 Blender 后再次跑全量生成脚本。
- 相关文件：`scripts/create_sky_island_model.py`、`models/sky_island_lowpoly.blend`。
- 新 AI 下一步该怎么查：先比较 `.blend` 与 GLB 时间戳；若 `.blend` 新，只导出，不重建。

### 问题：植物、火堆和长凳导入脚本会重置同类资产

- 表现：重跑脚本后，用户后续手工调整的位置或尺寸恢复为脚本值。
- 可能原因：脚本先删除同集合/前缀对象，再重新追加。
- 已尝试方案：脚本做成可重复生成，避免重复对象。
- 有效方案：只在明确需要整体重置该类资产时运行；普通微调直接改当前 `.blend`。
- 无效方案：把这些导入脚本当作无副作用的导出命令。
- 相关文件：`append_garden_plants_to_saved_blend.py`、`append_fire_to_saved_blend.py`、`append_log_benches_to_saved_blend.py`。
- 新 AI 下一步该怎么查：先询问用户是否要保留现有摆放，并创建备份。

### 问题：泉水组件默认隐藏与 GLB 导出的耦合

- 表现：如果按普通“只导出可见对象”的方式导出，网页可能找不到 `FX_` 组件，按钮显示“泉水组件缺失”。
- 可能原因：Blender 中集合为了初始干池而默认隐藏。
- 已尝试方案：永久显示会污染 Blender 预览；永久隐藏会漏导。
- 有效方案：`export_saved_blend.py` 导出前临时显示，导出后恢复。
- 无效方案：删除 `reveal_animation_components_for_export()`。
- 相关文件：`scripts/export_saved_blend.py`、`scripts/add_fountain_animation_components.py`。
- 新 AI 下一步该怎么查：解析 GLB 节点名，确认存在 43 个 `FX_` 节点。

### 问题：`npm run static` 不适合作为当前推荐服务器

- 表现：Python 从项目根目录服务时，页面请求 `/models/sky_island_lowpoly.glb` 可能 404。
- 可能原因：Vite 会把 `public/models` 映射到 `/models`，普通 Python 静态服务器不会。
- 已尝试方案：package 中保留 `python -m http.server 5173`。
- 有效方案：开发使用 `npm run dev`；生产先 `npm run build`，再服务 `dist/`。
- 无效方案：直接在项目根目录使用 Python server 并期待 Vite 路径规则。
- 相关文件：`package.json`、`src/main.js`。
- 新 AI 下一步该怎么查：请求 `/models/sky_island_lowpoly.glb` 并检查状态码。

### 问题：没有自动化测试、lint 和类型检查

- 表现：只能靠构建、HTTP、浏览器截图和人工操作验证回归。
- 可能原因：项目是快速原型，使用原生 JavaScript。
- 已尝试方案：使用 debug globals、DOM dataset、浏览器 console 和截图验证。
- 有效方案：每次改动后至少运行构建并验证关键交互。
- 无效方案：仅凭代码阅读声明完成。
- 相关文件：`package.json`、`src/main.js`。
- 新 AI 下一步该怎么查：先看 `package.json` 是否新增测试命令；没有则执行手工验收清单。

### 问题：Vite 构建有大 chunk 警告

- 表现：`npm run build` 提示 JS chunk 超过 500 kB。
- 可能原因：Three.js 和全部逻辑打入单个入口 chunk。
- 已尝试方案：目前未拆包，因为 gzip 后约 151 kB，原型可接受。
- 有效方案：未来需要时使用动态 import 或 Vite code splitting。
- 无效方案：把警告当作构建失败。
- 相关文件：`src/main.js`、`package.json`。
- 新 AI 下一步该怎么查：看实际加载性能和目标部署限制，再决定是否优化。

### 问题：GLB 和场景对象数量较大

- 表现：GLB 约 2.39 MB，188 个节点、140 个 mesh、97 个材质。
- 可能原因：多次导入花园资产、火堆、长凳和 43 个泉水对象；材质没有统一合批。
- 已尝试方案：保持低模几何、平面材质和有限像素比。
- 有效方案：如性能不足，先合并静态非交互装饰和复用材质。
- 无效方案：在未测性能前盲目合并所有对象，因为泉水动画依赖独立命名对象。
- 相关文件：`.blend`、GLB、`src/main.js`。
- 新 AI 下一步该怎么查：查看 renderer drawCalls/triangles 和真实设备帧率。

### 问题：漫游碰撞目前只有地面射线，没有角色胶囊体

- 表现：草地、台阶和完成后的桥面都能承接玩家高度，岛边也会阻挡；但树、石池、桥栏杆等竖直装饰物不会挡住玩家。
- 原因：当前碰撞目标是防止穿过地面/跌出岛面，并实现上下台阶，使用单足点向下射线即可；尚未加入角色体积和水平障碍物检测。
- 已实现方案：自动收集真实 `grass cap` 与 `BRIDGE_PIECE_*` 网格，过滤朝上表面，并限制单次可跨越高度。
- 如需扩展：为玩家增加胶囊体，并对静态障碍物构建 BVH；不要恢复已删除的 `walkZones` 手工坐标。
- 相关文件：`src/main.js`。

### 问题：硬编码外部素材路径影响迁移

- 表现：换电脑或移动 `D:\aidocument` 后，导入脚本找不到素材。
- 可能原因：素材包不全部在项目目录中。
- 已尝试方案：火堆会复制一份到项目 `models/fire.blend`；其他包仍引用外部路径。
- 有效方案：迁移前复制素材并修改脚本常量，或把素材依赖写入配置。
- 无效方案：假设任何 Windows 用户都有相同路径。
- 相关文件：植物、火堆、长凳脚本。
- 新 AI 下一步该怎么查：先运行 `Test-Path` 验证三个源 `.blend`。

### 问题：Blender 场景层级有历史重复与后缀对象

- 表现：存在 `Sky Island Game Model` 与 `.001`，一些对象/mesh 带 `.001` 后缀。
- 可能原因：早期生成、追加素材和用户手工编辑共同累积。
- 已尝试方案：当前保持不动，以免破坏父子变换。
- 有效方案：只有在创建完整备份和视觉对比条件下做层级清理。
- 无效方案：仅按名称后缀批量删除 `.001`。
- 相关文件：当前 `.blend`。
- 新 AI 下一步该怎么查：先检查 parent、world matrix、collection 和网页截图，再做任何删除。

### 问题：早期文档与当前实现不一致

- 表现：旧文档描述完整课堂 VR 流程、表达方块和奖励卡；网页目前只实现了服务于积木桥和泉水的 VR 模拟双手，不包含旧课堂任务系统。
- 可能原因：产品方向从课堂互动 Demo 转为天空岛浏览/漫游/泉水展示。
- 已尝试方案：保留旧文档作为创意记录。
- 有效方案：以本交接文档和当前代码为准；旧功能必须作为新需求重新确认。
- 无效方案：把旧计划中的每一项当成待修 bug。
- 相关文件：`docs/`、`PRODUCTION_README.md`。
- 新 AI 下一步该怎么查：搜索实际代码和 GLB 对象，找不到就标记未实现。

### 问题：PowerShell 默认读取中文时可能显示乱码

- 表现：`Get-Content` 不指定编码时显示乱码，但浏览器中文正常。
- 可能原因：Windows PowerShell 默认编码与 UTF-8 文件不一致。
- 已尝试方案：实际浏览器验证文字。
- 有效方案：使用 `Get-Content -Encoding utf8`。
- 无效方案：看到终端乱码就直接重写中文文件。
- 相关文件：`index.html`、`src/main.js`。
- 新 AI 下一步该怎么查：先用 UTF-8 读取，再看浏览器 DOM。

### 问题：应用内浏览器控制偶发超时

- 表现：自动化过程中标签页 reload/list/get 偶尔等待超时，但 HTTP 服务和页面本身正常。
- 可能原因：Codex 应用内浏览器连接或遥测网络抖动，不是项目代码错误。
- 已尝试方案：重新连接同一个 in-app browser、创建新标签页、用 DOM CUA 点击。
- 有效方案：先检查 5173 和 HTTP 200，再重连浏览器；不要因此切换到无关浏览器后端。
- 无效方案：把浏览器控制超时误判为 Vite 或 Three.js 崩溃。
- 相关文件：无特定项目文件。
- 新 AI 下一步该怎么查：先用 `Get-NetTCPConnection` 和 `Invoke-WebRequest` 区分服务问题与控制工具问题。

### 问题：移动端和多浏览器兼容尚未系统测试

- 表现：CSS 有移动端规则，但没有完整 iPhone/Android/Firefox/Safari 验收记录。
- 可能原因：当前目标是 Windows 桌面作品集预览。
- 已尝试方案：限制像素比、提供屏幕方向键和拖动视角回退。
- 有效方案：需要发布前做响应式截图和交互矩阵测试。
- 无效方案：仅凭 CSS media query 声明移动端完成。
- 相关文件：`src/style.css`、`src/main.js`。
- 新 AI 下一步该怎么查：测试 390×844、768×1024、1280×720 等视口，并检查按钮重叠与文字溢出。

### 已修好的坑：泉水材质导出成白色

- 表现：第一次导出时水、荷叶和花瓣都接近白色。
- 可能原因：按节点显示名查找 `Principled BSDF`，在本地 Blender 环境中没有正确命中节点。
- 已尝试方案：只设置 `material.diffuse_color`，无效。
- 有效方案：按 `node.type == "BSDF_PRINCIPLED"` 找节点并写入 Base Color/Roughness/Metallic/Alpha。
- 无效方案：只依赖 viewport diffuse color。
- 相关文件：`scripts/add_fountain_animation_components.py`。
- 新 AI 下一步该怎么查：解析 GLB `baseColorFactor` 或网页截图；不要撤销当前实现。

### 已修好的坑：低帧率时泉水动画播放过慢

- 表现：早期把主帧间隔统一限制为 0.033 秒，低帧率/自动化环境中 11.4 秒动画实际需要更久。
- 可能原因：移动安全限速和动画真实时间共用了同一个 delta。
- 已尝试方案：统一 clamp delta，无效。
- 有效方案：移动使用 `movementDelta <= 0.033`，动画使用 `animationDelta <= 0.25`。
- 无效方案：继续用同一个 0.033 delta。
- 相关文件：`src/main.js` 的 `animate()`。
- 新 AI 下一步该怎么查：不要合并这两个 delta；用实际阶段时间验证。

### 已修好的坑：目标树颜色与其他树不一致

- 表现：石池旁大树原为桃粉树冠和粉色树干。
- 可能原因：源素材 `tree_coral_crown` 的原始调色板。
- 已尝试方案：无，用户直接要求统一配色。
- 有效方案：树冠 part 02–04 复用三档绿色材质，part 01 复用三档暖棕色材质，并按面分配。
- 无效方案：直接修改共享材质颜色，会影响其他树。
- 相关文件：`scripts/recolor_coral_tree_to_green.py`、当前 `.blend`。
- 新 AI 下一步该怎么查：对象 custom property `recolored_green_canopy` 为 true，并在网页确认。

## 8. 最近修改记录

### 修改 11：新增并升级 Blender 六款式积木桥与网页整组归位动画（2026-06-28）

- 修改原因：用户要求参考积木散件图，让图 1 原桥在漫游初态消失，点击空中漂浮桥块后逐件自动回归。
- 修改文件：
  - `scripts/setup_bridge_puzzle.py`
  - `models/sky_island_lowpoly.blend`
  - `models/sky_island_lowpoly.before_bridge_puzzle_20260628-161833.blend`
  - `public/models/sky_island_lowpoly.glb`
  - `public/assets/sky_island_blender_preview.png`
  - `index.html`
  - `src/main.js`
  - `src/style.css`
- 改了什么：把原桥 12 个网格转为稳定命名桥块并分为 6 个材质款式组；天空只显示每组一个代表块，代表块落地后整组桥件同时显现；进度改为 `0/6` 至 `6/6`。
- 为什么这么改：保留用户指定的 `qiao.blend` 原桥造型和精确变换，同时让 Blender 负责真实模型/目标、Three.js 负责输入与时间轴。
- 是否验证：已验证初态仅 6 个代表块、单组一块触发两件显现、6 组完整归位、完成 UI、完整桥全景、GLB 节点数量、隐藏组员目标矩阵和生产构建；浏览器控制台无项目错误。
- 可能影响：桥节点名现在是网页绑定契约；不要随意重命名。漫游出生点调整为 `(10.7, 1.05, 3.55)`，避免树冠遮挡桥块。

### 修改 1：目标大树改为绿色树冠和棕色树干（2026-06-28）

- 修改原因：用户指出石池旁大树配色与其他树不一致。
- 修改文件：
  - `scripts/recolor_coral_tree_to_green.py`
  - `models/sky_island_lowpoly.blend`
  - `public/models/sky_island_lowpoly.glb`
  - `public/assets/sky_island_blender_preview.png`
- 改了什么：
  - `tree_coral_crown part 02–04` 改用三档绿色。
  - `part 01` 改用三档暖棕色。
  - 每个 polygon 保持 flat shading 并分配不同明暗材质。
- 为什么这么改：与场景其他绿色树统一，同时保留低模分面。
- 是否验证：已验证；Blender 总览图与网页截图均正确，控制台无错误。
- 可能影响：只重配目标树的材质槽，不移动对象；脚本依赖当前对象名。

### 修改 2：新增 Blender 泉水/荷叶/荷花低模组件（2026-06-27）

- 修改原因：用户要求参照阶段图，在 Blender 先建立两股流水、池水、荷叶、花苞和分层荷花，并由网页按钮控制。
- 修改文件：
  - `scripts/add_fountain_animation_components.py`
  - `scripts/export_saved_blend.py`
  - `.blend`、GLB、预览图
- 改了什么：新增 `Fountain_Animation` 集合及 43 个 `FX_` 对象，默认隐藏。
- 为什么这么改：让组件既能在 Blender 编辑，又能在网页独立控制。
- 是否验证：已验证对象数量、隐藏状态、GLB 节点和网页显示。
- 可能影响：GLB 从约 2.25 MB 增至约 2.39 MB；导出流程必须保留临时显示逻辑。

### 修改 3：新增并修正网页泉水动画（2026-06-27）

- 修改原因：实现参考图中的“流水→注满→荷叶→花苞→盛开”，并支持重复播放。
- 修改文件：`index.html`、`src/main.js`、`src/style.css`。
- 改了什么：
  - 增加“唤醒泉水/再次绽放”按钮。
  - 增加 11.4 秒时间轴和池子聚焦相机。
  - 增加水面、荷叶、水波和流水的持续循环。
  - 增加 debug 状态和 seek 接口。
  - 修复低帧率计时过慢。
- 为什么这么改：Three.js 时间轴比 Blender baked animation 更容易由按钮重播和调节阶段。
- 是否验证：已逐阶段截图、重复播放、console 和构建验证。
- 可能影响：`src/main.js` 体积和复杂度增加；依赖固定 `FX_` 名称。

### 修改 4：修复泉水材质导出颜色（2026-06-27）

- 修改原因：第一次 GLB 中 FX 材质的 baseColorFactor 变成 0.8 灰白。
- 修改文件：`scripts/add_fountain_animation_components.py`。
- 改了什么：按节点类型查找 Principled BSDF 并写入颜色、粗糙度、金属度和透明度。
- 为什么这么改：避免 Blender 界面语言/节点显示名影响材质写入。
- 是否验证：已解析 GLB 材质数据并在网页看到蓝水、绿叶、粉花、金花心。
- 可能影响：无负面影响；不要退回只写 `diffuse_color`。

### 修改 5：导入亮色花园植物与原木长凳（2026-06-27）

- 修改原因：用户希望岛屿恢复更丰富的卡通花园元素，并在火堆区域加入座位。
- 修改文件：
  - `append_garden_plants_to_saved_blend.py`
  - `append_log_benches_to_saved_blend.py`
  - `.blend`、GLB、两张 catalog 图
- 改了什么：导入 3 棵树、8 组花草和 3 张长凳，重建亮色平面材质。
- 为什么这么改：使用现成低模素材包，比手工重建更贴合风格。
- 是否验证：当前网页可见。
- 可能影响：这些脚本重跑会重置当前手工摆放。

### 修改 6：导入并重配火堆（2026-06-26 至 2026-06-27）

- 修改原因：用户要求把 `fire.blend` 放到右侧高岛指定位置，大小约为罐子 1.5 倍；最终脚本使用整体 scale 1.9。
- 修改文件：`append_fire_to_saved_blend.py`、`style_fire_in_saved_blend.py`、`models/fire.blend`、主 `.blend` 和 GLB。
- 改了什么：追加火堆 mesh，创建父对象，应用低模火焰/木头/石头材质。
- 为什么这么改：将外部素材转为与天空岛一致的低模配色。
- 是否验证：当前场景远端高岛可见火堆。
- 可能影响：重跑追加脚本会覆盖当前火堆对象。

### 修改 7：桥替换为用户 qiao.blend 并校平两端（2026-06-26）

- 修改原因：早期自动桥不符合要求，用户先要求删除，随后提供 `qiao.blend` 要求连接远处小岛与主岛。
- 修改文件：`models/qiao.blend`、主 `.blend`、早期 `create_sky_island_model.py` 中的桥追加逻辑。
- 改了什么：使用用户桥模型并调整桥面与岛面高度。
- 为什么这么改：保留用户指定模型和视觉结构。
- 是否验证：网页总览和漫游视角均可见桥。
- 可能影响：桥位置若再次改变，必须同步 `walkZones` 中矩形桥区域。

### 修改 8：中间石池与陶罐反复手工调整（2026-06-26 至 2026-06-27）

- 修改原因：用户多次要求罐子与石头衔接、向内倾斜、整组旋转并直接在 Blender 中修改。
- 修改文件：主要是 `models/sky_island_lowpoly.blend` 与导出的 GLB。
- 改了什么：两个陶罐倾斜并靠近石堆，石圈/石堆方向和整体构图由用户手工确认。
- 为什么这么改：自动脚本坐标无法完全替代视觉手调。
- 是否验证：网页当前画面已反映最新 Blender 保存状态。
- 可能影响：不要依赖旧 `create_sky_island_model.py` 中的陶罐初始参数恢复当前结果。

### 修改 9：右侧岛改为台阶结构、移除云朵并调整远岛（2026-06-25 至 2026-06-26）

- 修改原因：用户要求参考台阶图优化右侧岛，删除云朵，并让最小岛远离主岛。
- 修改文件：早期生成脚本和主 `.blend`。
- 改了什么：右侧由低、中、高三个阶梯台面组成；远岛独立拉开；云朵删除。
- 为什么这么改：匹配参考图和后续漫游构图。
- 是否验证：当前网页总览符合这些要求。
- 可能影响：不要从旧参考或脚本重新加云朵。

### 修改 10：建立 Three.js 浏览与漫游基础（2026-06-25 至 2026-06-26）

- 修改原因：让 Blender 模型可在网页查看并模拟游戏漫游。
- 修改文件：`index.html`、`src/main.js`、`src/style.css`、`package.json`。
- 改了什么：GLB 加载、OrbitControls、灯光阴影、模式切换、WASD/方向键、Pointer Lock、移动区域和调试状态。
- 为什么这么改：以最少依赖实现可作品集演示的 3D 体验。
- 是否验证：已验证桌面端核心流程。
- 可能影响：扩展功能前需注意单文件复杂度和手工碰撞区。

### 最近用户确认过的需求

- 当前主场景必须保留用户手工 Blender 调整结果。
- 云朵不要恢复。
- 桥使用 `qiao.blend`，并保持两端高度协调。
- 桥在漫游初态只显示 6 个颜色款式代表积木；同款只漂浮一个，点击后该款式全部桥件同时在各自位置显现；6 组未完成前不可通过，完成后恢复通行。
- 桥的唯一正确选择顺序是“蓝色 → 绿色 → 粉色柱子 → 黄色 → 橙色 → 红色细长连接条”；点错的积木只能震动并闪红色轮廓，不能归位或增加进度。
- 泉水必须按“唤醒泉水 → 流出水柱 → 水柱扩散 → 池水上涨 → 荷叶生长 → 荷花花苞 → 荷花盛开”拆成 7 段；浏览模式由按钮逐段播放，漫游模式由左右任一 VR 手射线单击逐段播放，全部完成后可重播。
- 泉水组件必须在 Blender 独立命名且默认隐藏。
- 石池旁大树必须是绿色树冠、棕色树干。
- 当前植物是后续重新加入的有效状态，不要依据早期“清空植物”要求删除。

### 修改 12：积木桥严格顺序、错误反馈与完整浏览器验收（2026-06-29）

- 修改原因：用户指定六组积木必须按固定颜色顺序选择，错误选择不得成为桥的一部分。
- 修改文件：`index.html`、`src/main.js`、`PROJECT_HANDOFF.md`。
- 正确顺序：蓝色（组 1）→ 绿色（组 3）→ 粉色柱子（组 4）→ 黄色（组 5）→ 橙色（组 6）→ 红色细长连接条（组 2）。
- 正确行为：只有当前期待的组可以启动原有的平滑弧线归位动画；整组真实桥件在动画结束后于各自目标位置显现，进度和“下一块”提示同步前进。
- 错误行为：点错的代表积木进行约 `0.68s` 的衰减震动，材质红色发光并显示背面放大生成的红色轮廓；震动结束后恢复原位置，不归位、不增加进度。
- 调试接口：`window.__BRIDGE_DEBUG_STATE__()` 会返回 `sequence`、`nextSequenceIndex`、`nextGroup` 和各组 `rejecting` 状态；`?bridge-debug=1` 下按 `B` 或调用 `window.__BRIDGE_ASSEMBLE_ALL__()` 会严格按正确顺序自动验收。
- 浏览器验收：粉色组在首步被故意点错时，页面为 `error`、`errorGroup=4`、进度保持 `0 / 6`，截图可见红色轮廓；震动结束后仍为 `0 / 6`。随后手动选择蓝色，进度变为 `1 / 6`。完整自动序列最终为 `complete=true`、`state=complete`、`6 / 6`，完整桥可见；绿色/橙色映射及 `nextGroup` 的最终验收见“修改 13”。
- 构建验收：`npm run build` 成功；主 JS 约 `610.00 kB`（gzip `155.28 kB`），仅保留 Vite 的大 chunk 提示。浏览器日志没有项目脚本异常；Pointer Lock 验收期间出现过由 Chromium 自己标注的内部 `UnknownError`，未影响页面状态或交互。

### 修改 13：纠正绿色与橙色组映射（2026-06-29）

- 问题：旧代码把组 3（`BRIDGE_PIECE_06–07`）写成橙色、把组 6（`BRIDGE_PIECE_11–12`）写成绿色，导致程序虽然执行 `[1, 6, 4, 5, 3, 2]`，网页实际颜色却成为“蓝 → 橙 → 粉 → 黄 → 绿 → 红”。
- 证据：直接解析当前 `public/models/sky_island_lowpoly.glb`，`06–07` 的 `baseColorFactor` 为约 `[0.142, 0.801, 0.392]`（绿色），`11–12` 为约 `[0.801, 0.415, 0.141]`（橙色）。
- 修正：组 3 改名为绿色、组 6 改名为橙色；网页严格顺序改为 `[1, 3, 4, 5, 6, 2]`，对应真实视觉“蓝 → 绿 → 粉 → 黄 → 橙 → 红”。`scripts/setup_bridge_puzzle.py` 同步修正，避免以后重跑脚本再次写反。
- 浏览器验收：`?bridge-debug=1` 下自动装配记录到的 `nextGroup` 依次为 `1 → 3 → 4 → 5 → 6 → 2`，最终进入 `state=complete`、进度 `6 / 6`；页面与 GLB 均返回 HTTP 200。

### 修改 14：漫游中播放泉水动画与真实地面/台阶碰撞（2026-06-29）

- 修改原因：用户要求漫游中唤醒泉水和荷花时不切换浏览模式，播放期间仍可自由移动视角；同时要求草地、桥和三级台阶成为不可穿透的真实地面。
- 修改文件：`index.html`、`src/main.js`、`PROJECT_HANDOFF.md`。
- 动画修正：`focusFountainCamera()` 仅在浏览模式生效；漫游中可点击按钮或按 `F` 原地播放。浏览器实测播放时保持 `mode=roam`，yaw/pitch 与玩家 X/Z 均可继续改变。
- 地面修正：删除 `walkZones`，改由向下射线自动识别 5 个 `grass cap` 草地网格；桥完成后启用真实桥面作为候选地面，只接受朝上的三角面。最终桥面筛选规则见“修改 15”。
- 台阶体验：允许单级上升 `0.46`、下降 `0.58`，相机以阻尼跟随 `groundY + 0.92`。自动路线记录到地面 Y `0.12 → 0.284 → 0.50 → 0.80`，最终高岛相机 Y `1.72`。
- 防穿模验收：高岛外侧无地面点被拒绝；桥中央在未完成时无命中，完成 `6 / 6` 后命中 `BRIDGE_PIECE_01`，高度约 `0.119`。
- 调试方式：`?roam-debug=1` 才显示“测试台阶”按钮，并在 `data-ground-probes` / `data-roam-stair-test` 写入验收数据；后续还增加了“测试过桥”，普通入口不显示这些测试控件。
- 构建验收：`npm run build` 成功；主 JS 约 `615.15 kB`（gzip `156.72 kB`），只有 Vite 大 chunk 提示。

### 修改 15：修复桥面高度卡住并前移绿色悬浮积木（2026-06-30）

- 修改原因：用户反馈漫游过桥会被高度卡住，同时绿色代表积木位于背景后方、与岛面颜色混在一起不清楚；明确要求其他内容不变。
- 修改文件：`src/main.js`、`scripts/setup_bridge_puzzle.py`、`PROJECT_HANDOFF.md`；没有改动 `.blend`、GLB、其他五组悬浮坐标或任何桥目标变换。
- 过桥修正：原地面候选包含全部 12 个桥件，向下射线会先命中拱门、扶手或桥柱顶部，从而被 `maxStepHeight=0.46` 拦截。现在只使用真实蓝色桥面主板 `BRIDGE_PIECE_01` 作为桥上脚底地面。
- 过桥验收：桥完成后沿 `z=4.0` 从 `x=10.6` 到 `x=4.8` 采样 59 点，零空洞，地面高度仅为 `0.119–0.120`；“测试过桥”使用正式 `tryMovePlayerTo()` 从远岛 `x=10.55` 走到主岛 `x=5.00`，状态为 `complete`。
- 绿色积木：组 3 代表件 `BRIDGE_PIECE_06` 的网页初始世界坐标固定为 `(6.1, 2.0, 4.0)`，从背景后方向前侧空位移出；最终归位仍复制原 `BRIDGE_TARGET_06`，不改变桥形。`SCATTER_POSES` 同步为 Blender 坐标 `(6.10, -4.00, 2.00)`，防止以后重跑脚本恢复旧位置。
- 可见性验收：网页初态截图中绿色件已与主岛背景分离，呈现在粉色柱下方偏右的天空空位；`data-bridge-floating-positions` 证明其他五组仍保持原坐标。
- 构建验收：`npm run build` 成功；主 JS 约 `617.24 kB`（gzip `157.16 kB`），只有 Vite 大 chunk 提示。

### 修改 16：泉水与荷花改为七次左键分段播放（2026-06-30）

- 修改原因：用户要求整套泉水动画不再一次连续播完，而是每次鼠标左键只播放一段，共 7 段。
- 修改文件：`index.html`、`src/main.js`、`PROJECT_HANDOFF.md`；模型、桥、漫游碰撞和场景布局均未改动。
- 七段顺序：`唤醒泉水 → 流出水柱 → 水柱扩散 → 池水上涨 → 荷叶生长 → 荷花花苞 → 荷花盛开`，时间边界为 `0 / 0.8 / 2.2 / 3.35 / 4.8 / 7.0 / 8.6 / 11.4` 秒。
- 交互规则：按钮显示 `1/7` 至 `7/7`；正在播放时重复点击会被忽略，段尾自动暂停并显示下一段。漫游中的 `F` 键复用同一逐段推进逻辑。
- 完成规则：第 7 段结束后显示“已完成 · 重新唤醒”；再点击一次会清空视觉状态并只播放第 1 段，不会一键连续播放 7 段。
- 调试状态：`data-fountain-segments` 保存七段清单；`data-fountain-active-segment`、`data-fountain-next-segment`、`data-fountain-completed-segments` 和 `data-fountain-awaiting-input` 可直接验收暂停状态。
- 浏览器验收：第 1–7 次点击均记录到对应 `activeSegment`；段尾依次停在 `0.8 / 2.2 / 3.35 / 4.8 / 7.0 / 8.6 / 11.4` 秒，最终 `completed=7`、`playing=false`、`phase=complete`。
- 构建验收：`npm run build` 成功；主 JS 约 `619.33 kB`（gzip `157.76 kB`），只有 Vite 大 chunk 提示；普通页面与 GLB 均返回 HTTP 200。

### 修改 17：漫游 VR 模拟双手、双射线与点击收尾（2026-06-30）

- 修改原因：用户要求漫游底部显示固定的 VR 模拟双手，左/右键分别控制左/右手射线与抓握，以射线取代鼠标光标选择积木和泉水；此前容量中断时主体代码已写入，但拖动松开会误触发、抓取多一次锁定点击且漫游按钮仍会截获鼠标。
- 修改文件：`index.html`、`src/main.js`、`src/style.css`、`PROJECT_HANDOFF.md`；没有改动 Blender、GLB、桥目标变换、泉水时间轴或地面碰撞。
- 双手与射线：相机下方固定显示青色左手和粉色右手，两条射线分别从手部发出；按住左键只移动左手射线，按住右键只移动右手射线，最新按下的按钮成为唯一活动手，未活动手保持不动。移动射线时同步更新 yaw/pitch，使视角跟随射线方向。
- 点击规则：累计移动超过 `4px` 视为拖动，松开只完成瞄准，不抓取积木、不触发泉水；随后原地单击同一键会直接把命中积木抓到对应手中，移除了 `lockedPiece/lockedGroup` 中间态；手持状态再次单击才尝试归桥。
- 桥规则：正确积木继续沿平滑弧线归位并增加进度；错误积木在放置时恢复原悬浮位置、震动和闪红，`nextGroup` 与进度不变。按 Esc 或切回浏览会把尚未放置的手持积木安全复位，并恢复正确的“下一块”提示。
- 泉水规则：漫游中隐藏泉水 UI 按钮，以覆盖整组泉水模型的透明代理作为命中区域；左右任一手的无拖动单击只触发一段，播放中重复点击被忽略，段尾继续暂停等待下一次输入。
- 界面规则：漫游时保持 `cursor: none` 并隐藏工具栏和方向键，只保留桥进度、双手、双射线和非交互状态提示；使用 WASD 移动、Esc 退出漫游。浏览模式光标的最终规则见“修改 18”。
- 调试接口：`window.__VR_HAND_STATE__()` 返回 `activeHand`，每只手返回 `pointer`、`pressed`、`moved`、`movement`、`hitType`、`hoveredGroup` 和 `heldGroup`；不再返回 `lockedGroup`。
- 浏览器验收：左手拖动命中蓝色桥面后松开，桥提示和 `0 / 6` 均不变；下一次左键直接进入 `held`，再次左键后进度变为 `1 / 6`。右手可直接触发泉水，连续快速点击第二段时仍只从 `completed=1` 前进到 `completed=2`。右手抓取错误黄色拱块后放置，页面进入 `errorGroup=5`，进度保持 `1 / 6`、`nextGroup=3`，反馈结束后恢复 `ready`。手持黄色拱块按 Esc 后回到浏览，积木复位且提示恢复正确顺序。最后用 `?bridge-debug=1` 的 `B` 键完整回归六组顺序，结果为 `complete=true`、`state=complete`、`6 / 6`。
- 可见性验收：漫游中 `hudDisplay=none`、`movePadDisplay=none`、`vrHandsVisible=true`、双手状态 HUD 与桥面板可见，body/canvas 光标均为 `none`；截图确认旧按钮不再遮挡右手。
- 构建与日志：`npm run build` 成功；主 JS 约 `626.50 kB`（gzip `160.12 kB`），CSS 约 `6.05 kB`（gzip `1.99 kB`），仅有 Vite 大 chunk 提示。当前项目脚本无异常；验收日志中只有此前 Pointer Lock 触发过的 Chromium 内部 `UnknownError`，与“修改 12/14”记录一致，不影响交互状态。

### 修改 18：浏览模式恢复可见光标（2026-06-30）

- 问题：全局 `cursor: none` 同时覆盖浏览模式、按钮和 canvas，导致用户看不到鼠标位置，无法可靠点击“漫游”。
- 修正：浏览模式 body 使用普通箭头，按钮使用手形光标，canvas 使用 `grab/grabbing`；只有进入漫游后才对 body、按钮和 canvas 强制使用 `cursor: none`。
- 模式行为：点击“漫游”后仍隐藏旧工具栏并显示 VR 双手；按 Esc 返回浏览时，工具栏和可见光标同时恢复。
- 验收：浏览初态为 `bodyCursor=default`、`canvasCursor=grab`、`roamButtonCursor=pointer`；点击漫游后为 `mode=roam`、`bodyCursor=none`、`canvasCursor=none`、`vrHandsVisible=true`；按 Esc 后恢复 `mode=browse`、`bodyCursor=default` 和可见工具栏。
- 构建：`npm run build` 成功；仅保留 Vite 大 chunk 提示。

### 修改 19：参考贴图双手、粗射线与宽容瞄准（2026-06-30）

- 修改原因：用户反馈原程序生成手缺少质感、射线太细且难以对准积木，要求使用提供的开放/抓握双手参考图制作半透明 2.5D 手部，并在抓握时仍看见积木。
- 修改文件：`src/main.js`、`public/assets/vr-hands-open.png`、`public/assets/vr-hands-grip.png`、`PROJECT_HANDOFF.md`；没有改动 Blender、GLB、桥目标、泉水时间轴或碰撞。
- 贴图资产：两张用户参考图分别作为“开放手”和“抓握手”的编辑目标，使用内置图像生成编辑将深色背景替换成纯绿色键控背景，再由官方 `remove_chroma_key.py` 生成带 alpha 的 PNG。最终开放手约 `540 KB`，抓握手约 `517 KB`，透明角落与手部覆盖均已检查。
- 图像提示词要点：严格保留原图双手姿态、比例、蓝色边缘光与左右对称，只把背景改成均匀 `#00ff00`；抓握版额外要求保留中央开口，以便显示手中积木；禁止文字、水印、阴影、额外手指和其他物体。
- 2.5D 手部：删除原先由方块与手指几何组成的程序手，改为相机下方两组透明平面；每组纹理 UV 只取整张双手贴图的一半。开放/抓握平面通过 `grip` 阻尼交叉淡入，左键只控制左手、右键只控制右手；按住鼠标或手持积木时切换抓握贴图。
- 半透明与持有：开放手最大不透明度 `0.72`，抓握手约 `0.70`，手持积木时抓握手降至 `0.56`；持有锚点位于抓握开口且略靠近相机，浏览器截图确认绿色侧板和黄色拱块均能在对应手掌开口中看见。
- 粗射线：`THREE.LineBasicMaterial` 替换为 `Line2 + LineMaterial`，射线宽度固定为闲置 `7px`、按住 `9px`，左右射线使用高饱和青/粉色；增加发光端点球，命中积木/泉水时放大并切换命中颜色。窗口缩放会同步更新 `LineMaterial.resolution`。
- 宽容瞄准：积木命中由实际三角面改为随模型更新的扩展世界包围盒，按积木尺寸增加 `0.065–0.16` 的瞄准余量；拾取射线直接使用相机屏幕指针，显示射线再从手部连接到命中点，消除旧实现把相机方向强行移到手部原点造成的视差。
- 交互验收：左手拖动后松开保持 `0 / 6` 且只更新瞄准目标；左键点击命中后进入 `held` 并显示抓握贴图。通过相机转向让右射线命中黄色拱块，右键点击后 `rightState=held`，左手仍为 `idle`，截图确认左右手状态独立且右手中央可见黄色积木。
- 构建与运行：`npm run build` 成功，主 JS 约 `649.02 kB`（gzip `166.76 kB`）；两张 PNG 均返回 HTTP 200；最终浏览器运行日志无项目错误，仅保留 Vite 大 chunk 构建提示。

### 修改 20：中键独立视角、缩小双手与六块横向排布（2026-07-01）

- 修改原因：用户要求按住鼠标中键移动时只控制视角；2.5D 双手进一步缩小并下移；六组悬浮积木在漫游初始画面中横向排开且尽量不重叠；左右射线闲置时统一为蓝色。
- 修改文件：`src/main.js`、`scripts/setup_bridge_puzzle.py`、`PROJECT_HANDOFF.md`；没有改动 Blender、GLB、桥目标变换或泉水时间轴。
- 中键视角：新增独立的 `pointerState` 中键流程。漫游中 `button === 1` 按下后进入视角控制，Pointer Lock 与普通指针路径都会把移动量传给 `rotatePlayer()`；松开/取消时结束，不会选择积木、抓取、归桥或触发泉水。左右键原有双手逻辑保持独立。
- 双手布局：相机局部位置由 `y=-0.12` 下移至 `y=-0.20`，手部平面由 `0.42×0.63` 缩小至 `0.33×0.50`；射线起点、手持锚点和手持积木最大尺寸同步缩小校准。
- 积木排布：六组代表件统一为世界坐标 `x=5.9、y=2.15`，沿 `z=6.35 / 5.40 / 4.45 / 3.50 / 2.55 / 1.60` 排列，对应画面从左到右“蓝、绿、粉、黄、橙、红”。`scripts/setup_bridge_puzzle.py` 已同步 Blender 坐标，防止以后重跑脚本恢复旧散布位置。
- 射线颜色：左右手基础色均为 `#00baff`；持有积木仍为绿色 `#83f0bd`、命中泉水仍为青色 `#6ee9ff`、命中积木仍为黄色 `#ffd35c`。调试状态与 body dataset 额外记录当前色和闲置色，便于回归。
- 浏览器验收：漫游截图确认双手更小且更靠下，六块代表件横向分离；`data-bridge-floating-positions` 返回六组新坐标；`data-vr-left-idle-ray-color` 与 `data-vr-right-idle-ray-color` 均为 `#00baff`，初始命中积木时两条射线均按原规则显示 `#ffd35c`。应用内浏览器无法持续按住中键并同时移动，因此该项以完整事件路由和构建检查验收；普通中键点击不会触发手部操作。
- 构建验收：`npm run build` 成功，主 JS 为 `650.66 kB`（gzip `167.16 kB`），CSS 为 `6.21 kB`（gzip `2.02 kB`）；仅保留 Vite 大 chunk 提示。

### 修改 21：四只参考动物建模、贴图与横木坐姿（2026-07-01）

- 修改原因：用户提供火堆横木座位图与 4 张动物参考图，要求复刻眼镜熊、紫裙白猫、黄鸭和绿青蛙，并让它们坐在红圈标出的四个位置。
- 参考映射：图 2 为戴大圆眼镜并拿铅笔的米灰熊；图 3 为穿紫色裙、闭眼微笑并举手的白猫；图 4 为黄身橙嘴橙脚的小鸭；图 5 为拿红书、吐舌微笑的薄荷绿青蛙。
- 修改文件：`scripts/add_seated_cartoon_animals.py`、`scripts/split_animal_face_atlas.py`、`scripts/render_seated_cartoon_animals_preview.py`、`scripts/verify_seated_cartoon_animals.py`、`scripts/export_saved_blend.py`、`src/main.js`、`textures/animal_characters/*`、主 `.blend`、网页 GLB、两张预览图与本交接文件。
- 贴图生成：使用内置 `imagegen`，以图 2–5 为身份参考生成 2×2 面部贴图图集；提示词要求按“熊、猫、鸭、蛙”顺序、正交正面、匹配原表情与配色、无身体/文字/阴影，并使用纯洋红抠像背景。最终源图保存为 `textures/animal_characters/animal_face_atlas_key.png`。
- 透明处理：内置抠像助手对自动采样色 `#f704d6` 的红色通道优势会误删黄鸭，因此保留助手产物验证记录后，最终由 `split_animal_face_atlas.py` 使用边缘实测 key `(247,3,215)`、通道最大距离 `36→90` 平滑生成 alpha，再拆为 `bear_face.png`、`cat_face.png`、`duck_face.png`、`frog_face.png`。四张贴图均为 `627×627 RGBA`，透明角落与角色内部不透明区域已逐像素验证。
- 建模方式：每只动物都由独立 3D 头部体积、身体、坐姿大腿/脚、手臂与标志性配件组成；面部贴图只贴在带 UV 的头部正面平面上。熊有铅笔和举笔手，猫有紫裙、粉纽扣、奶油裙边与挥手，鸭有双翼和橙脚，青蛙有双手与红书/书页。
- 座位：熊、猫位于 `log bench imported 01` 的局部长轴偏移 `-0.215 / +0.215`；鸭、蛙位于 `log bench imported 02` 的 `-0.215 / +0.215`。四个根节点高度均为 `0.9938`，横木顶面为 `0.9878`，统一高出 `0.006`，姿态元数据为 `seated_facing_campfire`；后侧第三根横木保持空置。
- 自动验证：`verify_seated_cartoon_animals.py` 已通过。熊/猫/鸭/蛙分别包含 `14 / 15 / 9 / 13` 个建模子部件，四张面部贴图均有 UV、唯一图像节点且已 pack 入 `.blend`。
- GLB 验收：最终 `public/models/sky_island_lowpoly.glb` 为 `3,913,312` 字节；GLB JSON 中有 4 个角色根节点、55 个 `ANIMAL_` 节点、4 个面部贴图节点、4 张嵌入图像与 4 个纹理。导出已开启 `export_extras=True`，座位、偏移和姿态元数据可在网页端读取。
- 网页验收：`?animals-preview=1` 只用于将浏览相机聚焦到角色，不改变普通入口；页面状态返回 `count=4`、`ids=bear,cat,duck,frog`，并记录两只在横木 01、两只在横木 02。网页截图与 `public/assets/seated_cartoon_animals_preview.png` 均确认四只动物坐在火堆两侧目标横木，面部透明贴图、铅笔、紫裙、橙脚和红书可见。
- 备份与构建：修改前备份为 `models/sky_island_lowpoly.before_seated_animals_20260701-162244.blend`。`npm run build` 成功，主 JS 为 `651.64 kB`（gzip `167.51 kB`），仅保留 Vite 大 chunk 提示。
