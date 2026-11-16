<!-- 公开仓库文档副本；私人照片不上传。原1.0.0描述的是历史设计包，当前进展以仓库根目录CONTINUE.md为准。 -->

# 来源与证据边界

资料核对日期：2026-11-16。外部资料仅用于约束方案；未运行其中示例代码，未保证与未来选定版本兼容。

## 用户来源

[探索猫咪商业价值](chatgpt-conversation://6afa5328-643c-83ec-951c-8f6ccee8ff13)：已通过read_thread读取近期与历史两页。用户明确谈及目标人群、桌面/手机/H5或小程序、猫狗可扩展、品牌偏好、用真实小猫作原型，并要求推进与打包。对话助手提出的商业判断、数值与路线建议不是独立验证证据。当前用户请求是本包范围的最高优先级输入。

附件IMG_3763.jpeg、IMG_3758.jpeg、IMG_3755.jpeg在本轮可访问且已目视检查；见references。V0.1生成图、三视图、模型、代码或既有仓库没有可访问交付输入，不将图像搜索占位当成已拥有的设计资产。

## 技术一手资料

| 来源 | 本包使用范围 | 未验证项 |
|---|---|---|
| [Electron Custom Window Styles](https://www.electronjs.org/docs/latest/tutorial/custom-window-styles) | 透明窗口的限制 | 目标OS/GPU上的实际表现 |
| [Electron Custom Window Interactions](https://www.electronjs.org/docs/latest/tutorial/custom-window-interactions) | 点击穿透机制设计参考 | 动态命中、纯穿透唤回与底层操作 |
| [Electron Security](https://www.electronjs.org/docs/latest/tutorial/security) | 权限、导航与IPC边界参考 | 当前工程的真实安全配置 |
| [Electron Context Isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation) | 渲染器隔离设计 | 具体preload接口审查 |
| [Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html) | glTF导入路线 | 导出器/扩展/资源兼容性 |
| [Three.js AnimationMixer](https://threejs.org/docs/pages/AnimationMixer.html) | 动画调度路线 | 表演质量、混合与性能 |
| [HyperFrames候选仓库](https://github.com/heygen-com/hyperframes) | HTML视频内容生产候选 | Q04身份确认、固定版本许可、输出能力与生产质量 |

HyperFrames存在同名网站/项目；本包不默认同名AI视频聚合服务就是用户指向的工具。候选仓库公开说明涉及HTML/CSS及可寻址动画到视频的渲染，仅据此安排探针，不推断它支持GLB骨骼动画生成。

## 法律一手资料

[网信办《人工智能拟人化互动服务管理暂行办法》全文](https://www.cac.gov.cn/2026-04/10/c_1777558395078289.htm)：核对施行日期和适用范围，用于提出后续适用性核查，不认定动物角色天然适用或豁免。其他发布、个人信息、支付、AI标识、知识产权等议题在08中列为待核查事项，尚未完成逐项法律研究。

## 证据分层

本包完成了来源读取、照片目视核对和文件检查；没有实现证据、真机性能证据、用户验证数据、正式合规或权属审查。对事实、设计提案、运行结果与正式审查分别记录，不能互相替代。网页信息可能变动，开发前记录固定版本和访问日期，发版前重新核对。
