<!-- 公开仓库文档副本；私人照片不上传。原1.0.0描述的是历史设计包，当前进展以仓库根目录CONTINUE.md为准。 -->

# PULU｜扑噜 · Milestone 01
## Make PULU Alive · 让 PULU 第一次活在电脑桌面上

版本：1.0.0｜编制日期：2026-11-16（Asia/Shanghai）｜性质：设计任务书 / 待实施。

**本包已编写并进行文件完整性检查；产品、模型、代码、运行性能、安全与商业结果均未实现、未实测、未审验。** 本包不包含可运行软件、3D 成品或已审批的合规结论，也不代表仓库推送、部署或任务已实际派发。

### 目标与边界

面向想养宠物但受现实条件限制的人，设计一个拥有自主行为、连续关系与未来跨设备身份的 AI 虚拟伙伴。M01 首先验证银灰虎斑白胸白爪、红铃铛小猫能自然、轻量地待在真实桌面上。Three.js 为当前指定渲染路线；Electron 为宿主候选，HyperFrames 为内容生产候选。

M01 必须交付的未来能力：离线启动、六类基础动作、自主行为、鼠标与键盘替代互动、透明区域交互验证、一键暂停/隐藏/退出、基础本地记忆与存档、隐私控制、真实桌面性能与可用性证据。云端 LLM、账号和跨端同步不作为 M01 必过条件；接口需预留并能用确定性替身验证。

### 阅读顺序

1. [决策与待定记录](01_DECISIONS_AND_QUESTIONS.md)：先理解已确认、建议与缺失证据。
2. [角色 V0.2](02_CHARACTER_V0.2.md) → [3D 资产与动作](03_3D_ASSETS_AND_ANIMATION.md)。
3. [桌面 P0 PRD](04_DESKTOP_P0_PRD.md) → [交互流程](05_INTERACTION_FLOWS.md)。
4. [行为与记忆架构](06_BEHAVIOR_AI_MEMORY.md) → [宿主与生产技术验证](07_TECH_SPIKES.md)。
5. [隐私安全与合规](08_PRIVACY_SECURITY_COMPLIANCE.md) → [任务与依赖](09_TASKS_AND_DEPENDENCIES.md)。
6. [测试与验收门槛](10_TESTS_AND_ACCEPTANCE.md) → [风险](11_RISKS.md) → [商业验证](12_COMMERCIAL_VALIDATION.md)。
7. [Agent 派工与治理](13_AGENT_GOVERNANCE.md)、[继续工作入口](CONTINUE.md)、[变更日志](CHANGELOG.md)。

辅助材料：[来源与证据边界](14_SOURCES_AND_PROVENANCE.md)、[真实照片参考](references/REFERENCE_INDEX.md)、[任务模板](templates/TASK_CARD.md)、[验收记录模板](templates/ACCEPTANCE_RECORD.md)、[数据契约](templates/DATA_CONTRACTS.md)。所有 Markdown 为 UTF-8，可独立阅读；相对链接在完整解压目录中生效。

### 状态约定

- C = 用户当前请求或原对话用户表达支持的方向；不表示可行性或法律可用性已验证。
- H = 本包建议的实施默认值，可用于估算、可逆原型；不视为用户拍板。
- Q = 开放问题；与其相关的不可逆工作需等待指定责任人决策。
- E = 实际观察到的文件或检索到的一手资料；不同于实现或审批证据。
- 工作状态统一从 NOT_STARTED 开始。未经证据不得改写为完成。

### 交付使用

开发负责人从 CONTINUE 开始，先做 G0 范围与环境记录，再做透明悬浮/穿透和模型导出验证。不要先承诺多端同步、第三方窗口贴边或云端记忆。实现阶段若改变必过门槛，必须记录决策与影响，不能通过删测试宣告通过。

ZIP 含私人猫咪照片参考，仅限本项目内部设计交接；照片涉及生活环境和人物局部，公开发布前另行确认权利并处理背景。图片文件已移除 JPEG 元数据段，未改像素。保留原文件名用于对应，不将其等同于商业授权凭证。
