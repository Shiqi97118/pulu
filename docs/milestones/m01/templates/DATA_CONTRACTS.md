<!-- 公开仓库文档副本；私人照片不上传。原1.0.0描述的是历史设计包，当前进展以仓库根目录CONTINUE.md为准。 -->

# 数据与接口契约草案

状态：设计级schema，非实现代码、非已校验JSON Schema。选定语言/存储后由Data Agent转成类型与运行时校验，变更需ADR。

## 公共类型

| 类型 | 字段与约束 |
|---|---|
| PetSnapshot v1 | schemaVersion=1；petId=本地随机UUID；revision=非负递增整数；memoryEpoch=非负整数；personalitySeed=整数；traits=0..1；behaviorState=状态枚举；settings=见下；updatedAt=UTC ISO8601 |
| Placement | displayId=OS不稳定标识仅作提示；normalizedX/Y=0..1相对workArea；scaleCssPx=120..240；恢复时重新校验 |
| Settings | paused/hidden/sound/reducedMotion/lowPower/cloudAI/diagnosticsUpload/autostart=布尔；activityLevel=low/normal；cloudAI等默认false |
| Event | eventId=UUID；type=白名单；monotonicMs=会话内；occurredAt=UTC；source=user/rule/lifecycle；payload=按type有界校验；不存原始轨迹 |
| MemoryRecord | memoryId、petId、kind=explicitPreference/interactionSummary；value=结构化白名单字段；source=userConfirmed/localAggregate；createdAt/updatedAt；retentionUntil；consentScope；epoch |
| DeletionMarker | petId、memoryEpoch、deletedIds或clearBeforeRevision、createdAt；不得存被删除的原内容 |
| IntentProposal | requestId、petId、expectedRevision、memoryEpoch、intent=observe/rest/approach/micro；expiresAt；reasonCode=枚举；禁止脚本和OS命令 |

## 接口与错误语义

- dispatch(event)：仅事件白名单，按eventId去重；返回accepted与reasonCode，不承诺每个输入都触发动作。
- getSnapshot()：返回不可变快照；渲染层不持有写权限。
- applySettings(patch, expectedRevision)：校验字段和版本；成功revision+1并持久化，失败返回VALIDATION/CONFLICT/STORAGE，不先显示已保存。
- listMemory() / saveExplicitPreference(value, confirmed, expectedRevision)：自由文本如未来添加需长度/敏感项规则；P0仅固定偏好字段；未确认不存长期记录。
- deleteMemory(ids或all, expectedRevision)：事务删除、推进epoch、取消在途、清理缓存与对应备份；失败返回明确错误，UI不得假报成功。
- exportLocalData(scope, userChosenPath)：宿主授权文件保存，限定schema、大小与字段，不暴露任意路径写接口。
- proposeIntent(context)：可选适配器返回不可信建议；校验白名单/时效/revision/epoch/预算后仲裁，任何失败回规则，不影响帧更新。

统一错误：VALIDATION、CONFLICT、STORAGE、RESOURCE、TIMEOUT、UNAVAILABLE、STALE_EPOCH、BUDGET、FORBIDDEN；日志只记录错误码和必要诊断。事件队列设有界长度，连续指针事件合并，生命周期事件优先。

未来同步需另定义鉴权、设备撤销、冲突合并和删除传播；本schema仅为本地M01预留，不是跨端同步协议。
