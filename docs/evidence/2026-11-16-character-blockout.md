# 角色重建检查记录 · blockout v1

日期 2026-11-16（Asia/Shanghai），macOS arm64，Blender 5.1.1（/Applications/Blender.app），Node 24.21.0，Python 3.12 + Pillow 12.3 / numpy 2.3。
执行者：当前主 Agent（DSH），无子 Agent 派工。**作者自测，非独立审核，非视觉签收。**

## 本轮实际做了什么

1. 仓库从用户 Codex 输出目录复制到工作区 `Desktop/PULU/pulu`，未新增提交；origin 与本地一致。`npm run check` 在工作区内通过（14 测试 + build，build 之前因仓库在工作区外报 EPERM，属沙箱而非代码问题）。
2. 从 Codex 的 Electron 状态文件与 `app.asar` 读出桌面机器人尺寸：overlay `visibleBounds 384×400`，`mascot {width:112, height:121}`，窗口常量 `{112, 121}`。据此定 PULU 视觉高 **76 px**（约 2/3），窗口 96×112，可调 56–96。
3. 对已签收 V05 三视图做轮廓分割与五官量测（`scripts/character/measure.py --profile`），得到第 1 节那张比例表，写入 `docs/character/ASSET_REBUILD_SPEC.md`。
4. 用参数化曲面重建 blockout v1：椭球变形头部 + 腮部起伏 + 口鼻垫 + 下巴 + loft 躯干 + 耳 + 眼 + 鼻 + 领 + 铃 + 四肢 + 趾 + 尾。脚本 `scripts/character/build_kitten.py`，可在 headless 重跑。
5. 三视正交渲染 600×600，输出到 `docs/character/renders/`，另出 76 px / 152 px 实尺寸对比图。

## 实测数字

| 项 | 值 | 说明 |
|---|---|---|
| 总三角面 | 23,952 | 在 30,000 预算内（未减面） |
| 材质 | 4 | fur / eye / red / brass |
| 轮廓 IoU（正/侧/背） | 0.508 / 0.360 / 0.397 | 门槛 0.90，**未通过** |
| 渲染 | Workbench，film transparent | 非最终材质，仅比对轮廓 |

IoU 低的两个具体原因（已确认，不是噪声）：

- 我的躯干底部比 V05 宽（模型基座近 0.69H，参考约 0.55H），正向重叠区因此少一块。
- V05 的腮毛轮廓比我现在的头部宽；侧视 0.36 主要来自头深与腹线的差异。

## 没做 / 没验证

- 视觉签收：没有。blockout 只锁比例和部件划分。
- 毛色分区、UV、烘焙、毛壳、绑定、10 个 clip、GLB 导出：未开始。
- 桌面实机 76 px 表现、性能、穿透：未做。本轮没有启动 Electron 应用。
- 未做独立代码/美术审核；未改动 `src/` 任何文件。

## 判定

blockout v1 = 可用基线，不是交付物。下一步按 spec 第 8 节把正/侧/背 IoU 推到 ≥0.90，再做脸部和毛壳。

预算说明：本执行单元按核心准则记上限 12000 tokens，返工计入同一单元；当前环境无逐调用计量，无法给出真实值，以上为估算并已在此留检查点，不换任务 ID 重试。
