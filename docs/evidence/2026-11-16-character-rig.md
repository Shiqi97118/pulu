# 角色绑定与动作检查记录 · rig v1

日期 2026-11-16（Asia/Shanghai），Blender 5.1.1 headless，执行者：当前主 Agent（DSH）。
**作者自测，非独立审核，未在 Three.js/Electron 内验证播放。**

## 做了什么

1. 22 根骨骼，命名沿用 `03_3D_ASSETS_AND_ANIMATION.md`：
   `root, pelvis, spine_01, neck, head, ear_L/R, tail_01..03, front_upper/lower/paw_L/R, hind_upper/lower/paw_L/R`。
2. 蒙皮：coat 用**双骨平滑权重**（最近两骨，反平方衰减，权重 <0.08 归一到单骨）；眼固定 head；项圈铃铛固定 neck。
   最初用单骨硬权重，脖子处会撕裂，已改。
3. 根节点 `PULU_root` 缩放 0.19，满足"1 单位 = 1 m、角色高 0.19 m"。
4. 10 个 clip，30 fps，逐个实测时长：

| clip | 时长 | clip | 时长 |
|---|---|---|---|
| idle_observe | 6.00 s | cursor_watch | 4.00 s |
| walk_in_place | 1.23 s | pet_react | 1.50 s |
| sleep_enter | 2.00 s | micro_groom | 3.00 s |
| sleep_loop | 6.03 s | micro_ear_tail | 2.00 s |
| stretch_exit | 2.00 s | intro_peek | 2.00 s |

## 实测

| 项 | 值 |
|---|---|
| GLB 字节 | 1,270,008 |
| 三角面 | 24,208 |
| 材质 / 贴图 | 3 / 1（1024²） |
| skin / 关节 | 1 / 22 |
| 动画数量 | 10 |
| 顶点属性 | POSITION, NORMAL, TEXCOORD_0, JOINTS_0, WEIGHTS_0 |

预算复核：三角 24,208 ≤30,000；材质 3 ≤4；GLB 1.27 MB ≤12 MiB；绘制调用仍为 3。

## 已知问题（未修）

- 头左右转时**项圈不跟随**（固定 neck），大尺寸下看得出来；76 px 下约 1–2 px，暂不处理。
- 转头幅度大时眼窝与眼球有轻微穿插。
- `walk_in_place` 是坐姿近似，不是四足步态；`03` 文档要求记录为非最终步态。
- 未在 Three.js 的 AnimationMixer 内实测播放/交叉淡入，只验证了 GLB 结构与 Blender 内帧渲染（见 `renders/anim-strip.png`）。

## 判定

绑定与 10 个 clip 在 GLB 内结构完整，Blender 内可播放。**不构成动画验收通过**：未接桌面壳、未测步态、未测循环跳帧。

预算：本执行单元按核心准则记上限 12000 tokens，返工计入同一单元；无逐调用计量，以上为估算。
