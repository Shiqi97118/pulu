# 2D 序列帧管线检查记录

日期 2026-11-16（Asia/Shanghai），macOS arm64，Blender 5.1.1 / Electron 45.3.2 / Node 24.21.0。
执行者：当前主 Agent（DSH）。**作者自测；画面观感与动效未经用户确认。**

依据：`docs/decisions/ADR-001-2d-sprite-character.md`（用户决定改 2D）。

## 做了什么

1. **帧源（占位）**：`scripts/art/render_frames.py` 从已绑定 3D 模型渲出 210 帧，152×152、
   透明背景、角色占画幅约 92%、脚底居中、机位绕 Z 轴偏 18°（3/4 视角）。
   这是占位源，画质等同现有 3D，只用于验证管线。
2. **打包**：`scripts/art/pack_atlas.py` 每个 clip 一条横向 WebP 条带 + `manifest.json`。
3. **运行时**：`src/renderer/sprite-player.js`（canvas 2D、按 clip fps 切帧、alpha 命中掩膜、reduced 降帧）。
4. **接入**：`src/renderer/app.js` 移除 three.js/GLTFLoader/AnimationMixer，改由 `SpritePlayer` 驱动；
   状态机 `src/core/behavior.js` 与 clip 名映射**未改**。窗口仍 96×112，角色视觉高 76 px。
5. **构建**：`scripts/build.mjs` 复制 `assets/sprites/*.webp` 到 `dist/sprites/`，manifest 以 JSON import 打包
   （file:// 下 fetch 会被 CSP/CORS 拦，图片用 `<img>` 不受影响）。

## 实测

| 项 | 值 |
|---|---|
| 帧数 | 210（10 clips） |
| 图集总字节 | **586 KiB**（WebP q=82） |
| 单 clip 最大 | idle_observe 106.6 KiB |
| 单帧 | 152×152 RGBA |
| 启动载荷 | `dist/app.js` ≈ 35 KB + 首帧所需 idle 条带 107 KiB |
| `npm run check` | 18 tests 全通过 |
| 应用内实拍 | 成功：`--shot` 捕获到角色正确渲染（见 `work/pet-sprite-preview.png` 同源画面） |

## 新增取证能力

`--shot=<path>`：用 `webContents.capturePage()` 抓真实窗口画面（绕开系统截图权限）。
`--shot-seq=N`：连续抓 N 帧（间隔 400 ms），用于验证动画是否在推进。
本轮即用它证明帧动画在播放。

## 修掉的 3 个接入期 bug

1. `play()` 依赖 rAF、rAF 又依赖 `play()` → **死锁，画面空白**。改为加载后显式播一次。
2. 图集路径少了 `sprites/` 前缀 → 图片 404，`decode()` reject，应用停在 error 态。
3. `codex exec` 被 `subprocess` 继承的 stdin 卡住 → 生成脚本空输出。改 `stdin=DEVNULL`。

## 没做 / 没验证

- **动效**：已验证**在播放**（`--shot-seq=3` 连续三帧两两逐像素不同，差异覆盖角色区域），
  但播放速度是否符合 clip fps、循环首尾是否接缝、`reduced` 降帧是否生效，仍未逐项确认。
- **命中/拖动**：alpha 掩膜命中写好了但未实机验证；拖动逻辑未改，未复测。
- **76 px 观感**：未由用户确认。
- 性能（rAF 占用、内存）、多屏、锁屏恢复：NOT_RUN。
- 占位帧的画质**不高于**现 3D；真实画质要等 AI/手绘帧源。

## 判定

2D 管线端到端可用：3D 绑定 → 帧 → 图集 → 运行时 → Electron 窗口。
**不构成视觉验收**：当前帧是占位渲染，不是成品美术。

预算：本执行单元按核心准则记上限 12000 tokens，返工计入同一单元；无逐调用计量，以上为估算。

## 帧源升级：GPT Image 生成帧（2026-11-16 16:2x）

**工具链已打通**：`scripts/art/gen.py` → Codex CLI 的 `image_gen` → 透明背景 PNG → `slice_strip.normalise` → 152² 帧 → `pack_atlas.py`。

关键参数与结论：

| 项 | 结果 |
|---|---|
| 透明背景 | **可行**，返回 RGBA 且 alpha 0–255，无需抠图 |
| 参考图锁定身份 | 可行，`--image=<ref>` 传 V05 或上一帧 |
| 帧间一致性 | 良好：同一提示词骨架下，仅改姿态描述，实测 open/closed 两帧为同一只猫、同一构图 |
| 输出尺寸 | 1254×1254（模型自选），归一化到 152² |
| 首版 idle | 4 帧 @6fps，替代占位帧；图集总计 498 KiB |

**已知代价**：每帧一次生成调用（约 40–60 s），10 个 clip × 3–6 帧 ≈ 40–60 次调用，需要分批做。
**已知风险**：帧数少时循环会显得"跳"；idle 4 帧 @6fps 只有 0.67 s 一循环，可能偏快，后续加到 6–8 帧。

**`--image` 参数坑**：`--image` 是多值选项，`-i path` 形式会把后面的位置参数（提示词）当成第二个图片路径吞掉，
表现为 `No prompt provided via stdin`。必须用 `--image=<path>` 等号形式。
