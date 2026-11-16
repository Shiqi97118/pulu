# 2D 序列帧规格 v0.1

状态：随 ADR-001 生效。数值为起点，按实物校准。

## 尺寸与坐标

| 项 | 值 |
|---|---|
| 窗口 | 96×112 CSS px（沿用） |
| 角色视觉高 | 76 px（可调 56–96） |
| 单帧画布 | 152×152（2× DPR 上限），锚点为脚底中心 |
| 留边 | 每帧四周 8 px，避免缩放采样溢出 |
| 排序 | 单图集内按 clip 分行，行内按帧序列 |

## 帧率与帧数预算（v2，含新增动作）

v2 在 M01 的 10 个 clip 之外补了用户要求的动作：真实走动、玩耍（拍打/扑跃）、舔舐、打哈欠、环绕转身。
总帧数 113，是 v1（约 211 帧的纯 3D 渲染）按"每帧都要单独生成"重算后的版本：帧数更多，但每帧成本更高，故单 clip 帧数控制在 4–12。

| clip | 时长 | fps | 帧数 | 说明 |
|---|---|---|---|---|
| idle_observe | 1.67 s | 6 | 10 | 呼吸 + 眨眼 + 轻微歪头 |
| walk_in_place | 0.83 s | 12 | 10 | **四足站立走动**（v1 是坐姿近似） |
| groom | 1.67 s | 6 | 10 | **舔爪 + 洗脸** |
| play_bat | 0.83 s | 12 | 10 | **拍打** |
| play_pounce | 0.67 s | 12 | 8 | **扑跃** |
| turn_around | 1.5 s | 8 | 12 | **环视/转身**（12 个视角，最考验一致性） |
| sleep_enter | 0.63 s | 8 | 5 | 入睡 |
| sleep_loop | 2.0 s | 4 | 8 | 蜷睡呼吸 |
| stretch_exit | 0.8 s | 10 | 8 | 伸懒腰 |
| yawn | 0.75 s | 8 | 6 | **打哈欠** |
| pet_react | 0.67 s | 12 | 8 | 被摸反应 |
| cursor_watch | 1.33 s | 6 | 8 | 离散朝向（2D 无法连续跟随） |
| micro_ear_tail | 0.5 s | 10 | 5 | 抖耳甩尾 |
| intro_peek | 0.5 s | 10 | 5 | 探头 |
| **合计** | | | **113** | |

体积：AI 帧是照片级细节，压缩率低于 3D 渲染帧。按当前实测约 25–35 KiB/帧估算，总计 **3–4 MB**；
`manifest.json` 按 clip 分文件，运行时只加载当前 clip，首屏只取 `idle_observe`。

## 生成管线（v2）

1. `scripts/art/clips.json` 定义每个 clip 的 fps、循环、帧数与逐帧姿态描述。
2. `scripts/art/batch.py` 逐帧调用 `gen.py`：第 0 帧用锚点参考图（已签收的 idle 帧）确立该 clip 的姿势族，
   其余帧以第 0 帧为参考，只描述"相对它改什么"。已存在的帧自动跳过，可断点续跑。
3. `scripts/art/assemble.py` 归一化到 152²（裁 alpha 边界、脚底对齐），生成 `summary.json`。
4. `scripts/art/pack_atlas.py` 打包成每 clip 一条 WebP + manifest。

## 资产格式

- `assets/pulu-atlas-idle.webp` 等，按 clip 分文件（便于懒加载与替换）。
- `assets/pulu-sprite.json`：`{frameSize, clips:[{name, fps, loop, frames:[{x,y,w,h,durationMs}]}], anchor}`。
- 全部本地打包，运行时不请求外部地址（沿用现有 CSP 与网络守卫）。

## 运行时

- `<canvas>` 2D 播放，`requestAnimationFrame` 按 clip fps 切帧。
- 状态机沿用 `src/core/behavior.js` 与现有 clip 名映射，不改行为逻辑。
- **命中检测**：用当前帧的 alpha 掩膜（离屏 canvas 预计算）判断，替代 raycaster；像素级更准，且无 3D 依赖。
- `reduced`（减少动态）模式：降到 4 fps 或只播首帧。
- 隐藏/暂停时停止 rAF，沿用现有窗口生命周期。

## 帧源（未定，待用户确认）

1. **AI 出图**：以 V05 三图为身份参考，每个 clip 生成一条横向 pose strip（一张图内 6–12 个姿态）再切帧——同图内一致性最好。
2. **手绘/外包**：按本规格交付。
3. **3D 渲染占位**：用现有绑定模型在 Blender 渲染同规格帧，先把管线跑通，画质等同现 3D。

方案 3 不提升画质，仅用于验证管线与尺寸；最终帧源必须是 1 或 2。
