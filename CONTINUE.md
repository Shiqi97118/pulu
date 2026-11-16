# 当前检查点 · 2026-11-16

先读取 CORE_PRINCIPLES.md 全文。它是用户指定唯一核心准则正文。实际队列见 docs/TASK_QUEUE.md，历史任务包只作设计基线。

## 本轮成果

- 角色研究稿V0.2：幼猫坐姿、白胸白爪、银灰虎斑、耳内/眼睛/胡须/铃铛。已有可编辑JS源、GLB和10个变换节点动画；未视觉定稿、无skinned骨骼成品。
- GLB导出后重新导入，14项自动测试与构建通过。模型21096三角形、68网格、11材质；绘制调用/材质预算不达任务书目标，不能声称性能通过。
- 新版本地设置、显式偏好、14天互动摘要、查看/删除/导出UI与意图替身；删除备份不保留记忆，epoch/并发冲突测试通过。重启后减少动态设置保留已通过原生UI观察。
- 复制Electron框架时绝对符号链接导致新包启动失败；保留相对链接后应用入口已成功显示角色与控制面板。新增verify-preview检查14个内部相对链接；旧坏包被该检查拒绝。CLI SIGABRT仍未解决。

## 待审而非完成

当前代码为研发预览。没有G1/G3签收、独立代码审核、完整diff验收、T01–T24全覆盖或商业结果。应用包仍未分发签名/公证。不得清空队列或关闭主要Issue。

## 下一执行单元

先读核心准则、此检查点、实际队列和已有review记录。按12条阅读实现成果与完整diff，尤其复核本地备份删除一致性、主进程IPC、拖动取消/释放、隐藏停帧、GLB资源释放、材质调用优化。修复审核发现的问题后再补原生桌面和无障碍证据。角色还需三视图/表情板及用户签收，不能只看截图通过。

本轮预算记录见 docs/reviews/2026-11-16-principles-adoption.md；无可靠实际Token计量，估算采用后的执行单元已接近12000上限，保存检查点，不以新ID重试规避。此前用量未验证。执行者为当前主Agent/GPT-6；本轮无子Agent派工。

## 用户反馈后的优先级更新

用户认为模型质量低于早期概念图且体积过大。已将功能研究版缩小到200x190 CSS窗口；主进程、渲染、命中使用共享尺寸。正式角色改为Blender建模/UV/绑定、GPT Image辅助贴图；先静态视觉/三视图，再做动作。原概念图需用户提供，Blender MCP尚未连接。见docs/character/BLENDER_HANDOFF.md。其余队列保留，不因路线调整假报完成。

## 2026-11-16 · 角色重建接手（DSH 主 Agent）

已定：美术方向 = 半写实外观 + 烘焙贴图/壳层绒毛；工作面 = `Desktop/PULU/pulu`（origin 一致，未新增提交前状态）；角色优先于桌面壳验收。

已做：量出 Codex 桌面机器人 overlay 为 `mascot 112×121`，据此定 PULU 视觉高 **76 px**（窗口 96×112，可调 56–96）；从签收 V05 三视图量出比例表；产出 blockout v1（23,952 三角 / 4 材质）与三视渲染；轮廓 IoU 0.508 / 0.360 / 0.397（门槛 0.90，未过）。

规格：`docs/character/ASSET_REBUILD_SPEC.md`；证据：`docs/evidence/2026-11-16-character-blockout.md`；脚本：`scripts/character/build_kitten.py`、`scripts/character/measure.py`；渲染：`docs/character/renders/`。

下一执行单元（按顺序）：
1. 按 IoU 差值修躯干基座宽度与腮部宽度，正/侧/背都过 0.90。
2. 脸部：眼窝、琥珀虹膜环、口鼻过渡、耳内。
3. UV + 虎斑图集烘焙（川字背纹、侧腰牛眼、纯色尾、白胸白爪）。
4. 2 层毛壳（共用图集，reduced 模式可关）。
5. 骨骼 + 10 clip + GLB 预算校验 + 接回 Electron（76 px 常量）。
6. 真机 76 px 观感、命中、拖动、隐藏停帧回归，再更新 `docs/TASK_QUEUE.md`。

未做/未验证：视觉签收、UV/贴图/毛壳/绑定/动作、桌面实机、性能、独立审核。不得把这些写成通过。

### 2026-11-16 · 角色重建第二轮（比例收敛）

- 修两处量测工具 bug：参考图掩膜缺行、侧视相机镜像。修正后同一份渲染 IoU 由 0.51/0.36/0.40 更正为 **0.891/0.837/0.875**；旧数字作废，证据文件已写明。
- 形体调整：头部加深（RY 0.206→0.236）、躯干后缘外扩、尾巴改为躺在身后地上（后缘 −0.44H）、颈与底座收窄、加眼窝（rim+floor）、眼径 0.055。
- 24,080 三角，仍在 30k 内；4 材质不变。
- 实验结论：轮廓外扩 1–4px 只能补 0.01（正）/0.02（侧），背面反而下降 → 门槛未过属形体差异，不是毛边；背面还需收肩宽。

下一执行单元：UV 展开 + 程序化虎斑在 3D 生成后烘焙到 1024 图集（白胸白爪、川字背纹、侧腰牛眼、纯色尾），再做 2 层毛壳；贴图完成后再评估是否继续收肩宽。

### 2026-11-16 · 角色重建第三轮（贴图与导出）

- 构造式 UV：躯干/四肢/尾/耳按 loft 拓扑生成（正面固定 u=0.5），头用位置投影，眼/鼻/垫/趾用平面或单点映射；在细分**之前**赋值。
- 图集 1024²，八分区（`atlas_layout.json`），图案按 2π 整数周期绘制，消除背缝锯齿。
- GLB：612,024 字节 / 24,080 三角 / 3 网格 / 3 材质（fur、eye、red）/ 1 张内嵌贴图 → 绘制调用 3，材质 3，均在预算内。
- 轮廓 IoU 0.887 / 0.826 / 0.874，门槛 0.90 仍未过。
- 修掉 5 个 bug（UV 跨界接缝、共享顶点 UV 被改写、UV 赋值晚于细分、尾巴环面斜切、渲染曝光洗白），详见 `docs/evidence/2026-11-16-character-texture.md`。
- 未做：毛壳、骨骼、10 clip、Electron 接入、76 px 实机。

下一执行单元：2 层毛壳（共用图集，`reduced` 可关）→ 补腮毛与身体灰白配比 → 再校 IoU；然后骨骼与 10 clip。

### 2026-11-16 · 角色重建第四轮（毛壳否决 + 尾巴几何修复）

- 毛壳两轮实验后否决：两层壳 + 硬 alpha 是撒盐点；几何毛刺在 76 px 无收益。改为贴图低频颗粒，`--fluff` 仅作实验开关。
- 导出隐患已排除：全部材质 OPAQUE、单面（先前 fur/eye 被导成 BLEND + doubleSided）。
- 尾巴环面改为沿切线定向，尾尖收细，去掉端盖大平面。
- GLB 884,272 字节 / 24,208 三角 / 3 图元 / 3 材质 / 1 张 1024² RGB 贴图。
- IoU 0.887 / 0.826 / 0.874（仍差门槛 0.90）。

下一执行单元：骨骼绑定（root/pelvis/spine/neck/head/ear/tail ×3/四肢）+ 10 个 clip，导出带动画 GLB 并在 Three.js 侧验证 mixer。

### 2026-11-16 · 角色重建第五轮（绑定 + 10 clip）

- 22 骨骼，双骨平滑权重；眼固定 head，项圈铃铛固定 neck；根节点缩放 0.19（1 单位 = 1 m）。
- GLB：1,270,008 字节 / 24,208 三角 / 3 材质 / 1 skin / 22 关节 / 10 动画。
- 已知问题：转头时项圈不跟随、大角度下眼窝轻微穿插、walk 为坐姿近似、未在 Three.js 内实测播放。
- 证据：`docs/evidence/2026-11-16-character-rig.md`；帧渲染：`docs/character/renders/anim-strip.png`。

下一执行单元：接回 Electron（新 GLB、76 px 视觉高、窗口 96×112、按 clip 名映射、验证 mixer 交叉淡入与命中），再做 76 px 实机与性能记录。

### 2026-11-16 · 桌面壳接入（76 px）

- 窗口 96×112；相机 30°/0.522 m，角色占可视高度 68% ≈ 76 px；资产换为 `assets/pulu-kitten-rigged.glb`。
- **CLI 启动问题根因找到**：环境变量 `ELECTRON_RUN_AS_NODE=1` 让 Electron 退化成纯 Node 跑 main.cjs，导致 `app` 未定义。`start`/`smoke` 已加 `env -u ELECTRON_RUN_AS_NODE`。SIGABRT 是否同因**未证实**，不要合并结论。
- 冒烟启动打印 `PULU_SMOKE_READY`（渲染器已解析新 GLB 并完成首帧）。
- 桌面截图 / 穿透 / 拖动 / 多屏 / 76 px 观感：**全部 NOT_RUN**，本机无屏幕捕获权限，需用户在真实桌面确认。
- 新增 `tests/coat-glb.test.js` 守住资产预算；`npm run check` 16 tests 全通过。

下一执行单元：请用户确认 76 px 观感；同时用 `webContents.capturePage()` 增加 `--shot` 取证通道，替代系统截图权限。

### 2026-11-16 · 2D 序列帧管线打通

- 按 ADR-001 切换：`app.js` 移除 three.js，改 `SpritePlayer`（canvas 2D + alpha 命中）；状态机与 clip 名未改。
- 占位帧源：`scripts/art/render_frames.py` 渲 210 帧（152²，3/4 机位）→ `pack_atlas.py` 打包 10 条 WebP（**586 KiB**）。
- 应用内实拍成功（`--shot`），窗口 96×112、角色 76 px。
- 修 3 个接入期 bug：play/rAF 死锁、图集路径缺 `sprites/` 前缀、codex exec 被 stdin 卡住。
- `npm run check` 18 tests 通过（新增 sprite 资产守卫）。
- 未验证：动效播放/循环接缝、命中与拖动实机、76 px 观感、性能。占位帧画质不高于现 3D。

下一执行单元：等 GPT Image 帧源（Codex 额度 15:59 重置，探针在跑）；拿到后按 clip 替换条带，再实机验动效与命中。

### 2026-11-16 · GPT Image 帧源打通（2D 画质跳档）

- `gen.py` 打通：透明背景单帧生成可用，`--image=<ref>` 锁身份；实测帧间一致性良好。
- 首版 idle 4 帧（睁眼/闭眼/呼吸两态）已替换占位帧，进桌面壳实拍验证（`work/ai-preview.png`）。
- 图集 498 KiB（10 clips，其中 idle 为 AI 帧，其余仍为占位）。
- 坑：`--image` 是多值参数，必须写 `--image=<path>`，否则吞掉提示词。
- 下一步：按 clip 批量出帧（预计 40–60 次调用），先出 walk + pet_react（最能体现"活"的两个），再补其余。

### 2026-11-16 · 环境恢复、基线修复与仓库接回（DSH 主 Agent）

**环境**

- 沙箱在工作区根建立了写授权，但 `pulu/`、`work/` 早于该授权存在、没有继承到，导致 shell 一律 EPERM（`npm ci` 报 `mkdir node_modules` 失败）。用户把会话切到完全权限后恢复。
- 这台机器没有装 git，但 `C:\Program Files\WorkBuddy\resources\vendor\PortableGit\cmd\git.exe`（2.55.0）可用；连 GitHub 必须加 `-c http.sslBackend=openssl`，否则 schannel 报 `SEC_E_NO_CREDENTIALS`。

**基线（本轮实测，不是引用历史）**

- `npm ci --ignore-scripts`：55 包，0 漏洞。
- `npm run check` 第一次跑出 **1 个失败**：`tests/sprite-assets.test.js` 仍断言旧的 10-clip 清单。
- 顺着它查出一个真实缺陷：`src/renderer/app.js` 把 `micro` 状态映射到 `micro_groom`，而 14-clip 重打包后 manifest 里已没有该 clip（被 `micro_ear_tail` 取代）。`SpritePlayer.play()` 对未知 clip **静默 `return false`**，所以 micro 状态一直什么都没播，界面上看不出来。已改映射；守卫测试更新到 14 个 clip。
- 现在：**18/18 测试通过，构建成功**。
- 遗留未处理：`assets/sprites/micro_groom.webp` 已成孤儿（manifest 不引用）；`play()` 静默失败没有告警，调用方也没检查返回值。

**仓库**

- 本地这份拷贝没有 `.git`（交接 zip 里也没有）。已 `git init` + 接回 origin，`git reset --mixed origin/main` 对齐后提交 `5555aa8`（`a6f78ae` 的快进）。
- 远端实际有 4 个分支，`work/character-rebuild`（`247155f`）比 `main` 新得多，含 2D 管线与 Windows 打包。

**安全问题（未闭环，需用户操作）**

- 公开分支 `work/character-rebuild` 里提交了 **730 个 `.codexhome/` 文件**，含 `auth.json`（Codex 登录令牌）、24 份会话 jsonl、`logs/memories/goals/queue/state` sqlite。污染起点 `da5ce12`；`787bff5` 等提交继续累积。`main` 与另两个分支干净。
- 已给 `.gitignore` 补 `.codexhome/`。
- **凭据轮换尚未完成**——用户在 Codex 侧退出并重新登录之前，这条不算解决。删分支不等于撤回：旧提交对象仍可被 SHA 直接访问。

**Codex 直连（已验证）**

- `codex exec --sandbox read-only` 回显 `PULU_CODEX_OK`。版本 0.169.0-alpha.11.1，model `gpt-6.1-sol`，session `01a1e3f0-cf07-77c0-ba70-14c0433ef9a3`，7,181 tokens。
- 出帧（把提示词与参考图发给外部服务）**仍未授权**，本轮没有触碰。

