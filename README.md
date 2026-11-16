# PULU｜扑噜

Milestone 01 · Make PULU Alive

以真实银灰虎斑、白胸白爪、红铃铛小猫为原型的跨设备虚拟伙伴项目，先验证桌面自然陪伴。

**开发与审核第一入口：[CORE_PRINCIPLES.md](CORE_PRINCIPLES.md)。** 需求、设计、编程、修复、测试、派工及返工均遵从这12条；AGENTS与PR模板引用同一正文。关键项未验证时不宣称最终验收通过。

- [实际任务队列](docs/TASK_QUEUE.md) / [继续工作](CONTINUE.md)
- [M01完整设计包](docs/milestones/m01/README.md)
- [已获用户公开授权的照片](docs/milestones/m01/references/REFERENCE_INDEX.md)

当前代码是研发预览，不是正式产品。Three.js GLB角色研究版与10个动作已导出/重新导入；Electron应用入口可体验。角色待视觉签收、材质与绘制调用预算未达标；没有云端AI、语义长期记忆或跨端同步。设置和有限偏好/互动摘要留在本地，可查看、删除或主动导出。

```sh
npm ci
npm run check
```

macOS Apple Silicon 本地预览：

```sh
node scripts/package-preview.mjs
node scripts/verify-preview.mjs artifacts/PULU.app
```

在Finder打开生成的app。CLI `npm start` 目前仍可能SIGABRT；应用入口已运行不代表CLI问题解决。未签名/公证，非正式安装包。右键小猫或菜单栏/托盘打开控制面板；退出/隐藏入口独立于角色。

默认无云AI、遥测、截图/桌面文本读取、声音或自动启动。全屏避让暂用手动隐藏/演示模式。公开仓库不意味着角色、照片或代码获任意第三方商用许可；正式许可待项目负责人决定。
