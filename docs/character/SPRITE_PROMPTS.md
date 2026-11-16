# 帧源出图模板（GPT Image）

配套：`docs/decisions/ADR-001-2d-sprite-character.md`、`docs/character/SPRITE_SPEC.md`。

## 硬性要求（先看这条）

**背景必须是与猫配色无关的纯色，或直接要透明。** 实测教训：米色背景 + 白胸猫，事后抠图会把白胸抠穿、边缘染成粉色（`work/art/sliced-preview.png`）。推荐的背景色：

| 候选 | 评价 |
|---|---|
| 透明（`transparent background`） | 最好，工具支持就直接要 |
| 纯绿 `#00FF00` | 可用，猫身上没有绿；边缘可能有绿溢，需 despill |
| 纯蓝 `#0044FF` | 可用，但项圈红色与蓝色边缘交界处要小心 |
| 米色/白/浅灰 | **禁用**，与白胸白爪冲突 |

## 身份锁定块（每条提示词都要带）

```
Character: the exact kitten from the attached reference sheet — silver-grey
tabby with soft silver and ivory-cream tones, white chest, white paws, big round
amber eyes with dark pupils and a small white catchlight, tiny pink nose, thin
red collar with a small round red bell bearing a white paw print, solid
dark-grey tail. Chibi proportions: head about half of total height, short legs.
Semi-realistic 3D-render look with soft fur, not flat cartoon, not pixel art.
```

## 输出格式

- 单帧：`1024×1024`，角色居中、脚底贴画面底部 92% 处，**纯绿背景**。
- 姿态条带：`2048×512`，横向 N 格等分，每格角色姿态不同、**同一角色、同一光照、同一缩放**。
  条带比单帧更省调用，但格间一致性依赖模型；第一次先试 4 格，不行再退回单帧。

## 每个 clip 的姿态描述

| clip | 帧数 | 姿态序列 |
|---|---|---|
| idle_observe | 4–6 | 坐姿呼吸：肩略起伏、尾巴尖轻摆、偶尔眨眼 |
| walk_in_place | 4 | 原地踏步：左前爪抬起 → 落下 → 右前爪抬起 → 落下 |
| sleep_enter | 3 | 坐姿 → 头低垂 → 蜷起闭眼 |
| sleep_loop | 3 | 蜷睡，缓慢呼吸（三帧差异极小） |
| stretch_exit | 4 | 睁眼 → 前爪前伸 → 伸懒腰弓背 → 回到坐姿 |
| cursor_watch | 4 | 坐姿，头依次朝：正前 → 左侧 → 正前 → 右侧 |
| pet_react | 4 | 被摸：眼睛眯起 → 头微仰 → 耳朵后压 → 恢复 |
| micro_groom | 3 | 低头舔前爪 → 抬头 → 恢复 |
| micro_ear_tail | 3 | 耳朵抖一下 → 尾巴甩一下 → 恢复 |
| intro_peek | 3 | 从画面下缘探头 → 露出上半身 → 坐好 |

合计约 35–39 帧。按 `SPRITE_SPEC` 的懒加载策略，先出 `idle_observe` 验证画风，再批量。

## 一致性技巧

1. 先出**一张主参考帧**（idle 第一帧），确认画风后再用它作为 `--ref` 逐帧生成。
2. 条带生成时在提示词里写明"same character in all cells, identical lighting and scale"。
3. 每次生成只改姿态描述，身份块与背景要求**一字不改**。
