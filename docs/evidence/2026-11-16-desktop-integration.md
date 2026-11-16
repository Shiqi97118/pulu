# 桌面壳接入检查记录 · 76 px 角色

日期 2026-11-16（Asia/Shanghai），macOS arm64，Electron 45.3.2 / three 0.187.0 / Node 24.21.0。
执行者：当前主 Agent（DSH）。**作者自测；桌面观感未经用户确认。**

## 做了什么

1. `src/core/viewport.cjs`：窗口 200×190 → **96×112**（共享给主进程窗口尺寸、命中与投影）。
2. `src/renderer/app.js`：
   - 资产换成 `assets/pulu-kitten-rigged.glb`（带骨骼与 10 clip）；
   - 相机 33°/0.66 m → **30°/0.522 m**，视点抬到 0.095 m，使 0.19 m 高的角色占窗口可视高度的约 68%，即 **76 px 视觉高**；
   - walk 位移 0.018 → 0.004（模型从 1.0 缩到 0.19 后的等比修正）。
3. `scripts/build.mjs`：不再每次构建重生成旧研究版 GLB（`export-character.mjs` 保留，改为手动运行）。
4. `package.json`：`start` / `smoke` 增加 `env -u ELECTRON_RUN_AS_NODE`。
5. 新增 `tests/coat-glb.test.js`：直接解析 GLB 容器，守住 12 MiB / 30k 三角 / 4 材质 / 8 draw call / 10 clip / 单 skin / 根缩放 0.19 / 材质必须 OPAQUE 且单面。

## 关键发现：CLI 启动失败的根因

仓库此前记录"`npm start` 仍可能 SIGABRT、命令行启动异常"。实测根因是环境变量 **`ELECTRON_RUN_AS_NODE=1`**：它让 Electron 二进制以纯 Node 方式执行 `main.cjs`，于是 `require('electron').app` 为 undefined，报 `Cannot read properties of undefined (reading 'setName')`。

去掉该变量后 Electron 正常启动。已把 `env -u ELECTRON_RUN_AS_NODE` 写进 `start`/`smoke`。
**注意：这不是应用代码缺陷，此前也未证实 SIGABRT 与它同因，SIGABRT 仍需单独复现。**

## 实测

| 项 | 结果 |
|---|---|
| `npm run check` | 16 tests，全通过；build 通过 |
| 冒烟启动（`--smoke`） | 打印 `PULU_SMOKE_READY`，说明渲染器已解析新 GLB、完成首帧并回调 ready |
| 桌面截图 | **NOT_RUN**。本机进程无屏幕捕获权限（`could not create image from display`），无法取真实桌面画面 |
| 透明/穿透/拖动/多屏 | **NOT_RUN**（需人工在真实桌面确认） |
| 76 px 观感 | **NOT_RUN**，待用户肉眼确认 |

在受管环境中还需 `--no-sandbox`（Chromium 的 OS 沙箱被外层进程沙箱阻挡），该参数只用于本机功能验证，未写入脚本。

## 判定

新角色已进入桌面壳并成功首帧渲染，尺寸链路（窗口 96×112 → 角色 76 px）在代码与相机参数上一致。
**不构成桌面验收通过**：观感、穿透、拖动、多屏、性能均未实测。

预算：本执行单元按核心准则记上限 12000 tokens，返工计入同一单元；无逐调用计量，以上为估算。
