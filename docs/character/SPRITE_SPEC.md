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

## 帧率与帧数预算

按"够用即停"配帧，目标是**逐帧可辨认、总字节可控**。

| clip | 时长 | fps | 帧数 |
|---|---|---|---|
| idle_observe | 6.0 s | 6 | 36 |
| walk_in_place | 1.2 s | 12 | 15 |
| sleep_enter | 2.0 s | 8 | 16 |
| sleep_loop | 6.0 s | 4 | 24 |
| stretch_exit | 2.0 s | 10 | 20 |
| cursor_watch | 4.0 s | 6 | 24（离散朝向，非连续跟随） |
| pet_react | 1.5 s | 12 | 18 |
| micro_groom | 3.0 s | 6 | 18 |
| micro_ear_tail | 2.0 s | 10 | 20 |
| intro_peek | 2.0 s | 10 | 20 |
| **合计** | | | **约 211 帧** |

体积估算：211 × 152² × 4B ≈ 19.5 MB 原始；WebP q=80 约 **2–4 MB**。按 clip 懒加载，首屏只取 `idle_observe`（约 0.5 MB）。

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
