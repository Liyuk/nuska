# Tobs 的交付能力评估证据：有机制回归，缺交付评测

状态：公开材料核验 · 2026-10-29。对象为 Tobs（BotHarness/DeepSeekBot）`main`（[`1e48294`](https://github.com/BotHarness/DeepSeekBot/tree/1e48294d86c681e308e989a8be967ecac21242b6)）。只读仓库、CI 配置、QA 文档与公开网页；未运行 Tobs，未获得任何内测数据。结论区分"公开可核对的机制"与"未找到的评估"。

## 问题和范围

Tobs 的**交付能力**被评估过吗？如果评估过，评的是什么、能支持什么结论；如果没有，缺什么、怎么补。

本文把"交付能力"限定为：任务是否按最新目标完成、产物是否可用、是否虚报完成、用户是否需要反复催促、中断后能否恢复。机制正确性（消息是否送达、成员是否被唤醒）不等于交付能力。

## 材料和方法

- 仓库固定快照 `1e48294`：`.github/workflows/llm-e2e.yml`、`scripts/e2e-llm-scenarios.mjs`、`docs/qa/`、`docs/evidence/`、`docs/agents/verification-inventory.md`、`PRD.md`、`docs/adr/`。
- 公开检索：GitHub 仓库内文档与代码搜索、项目 README/站点、第三方评测站点与比较文章（检索日期 2026-10-29）。
- 判定口径：一份"交付能力评估"至少要能回答——任务集是什么、成功/失败如何判定、是否独立于模型自述、样本量与波动、是否保留轨迹与产物。机制回归和功能验收不自动满足这些条件。

## 发现与证据

### 1 已有的最接近的一层：真实模型多 Bot E2E

Tobs 有 nightly 的真实模型场景套件：

- [`.github/workflows/llm-e2e.yml`](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/.github/workflows/llm-e2e.yml)：每晚 19:00 UTC 跑；只在 main 相关路径变更、打 `ci:llm-e2e` 标签或手动触发时跑；**不在 required verify 里**；运行需要配置相应模型服务凭据。
- [`scripts/e2e-llm-scenarios.mjs`](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/scripts/e2e-llm-scenarios.mjs)：13 个场景，断言"规范 Channel 状态"（mention、delivery、reply、产物文件、最终消息），不比对措辞。关键场景包括：
  - `delegate-and-report-back`：管理员派活 → 成员完成 → @ 回报 → 唤醒管理员（完整往返）；
  - `worker-to-worker-chain`：A → B → 协调者的多跳接力；
  - `long-task-reports`：三阶段任务（含 `sleep 60`），要求开工回执、中途进度、最终结果；
  - `department-task`：四个 Bot 协作出"最终方案"，检查每人贡献、两轮修改、最终方案后群安静；
  - `review-rounds`：三轮"提要求 → 修改 → 回报"；
  - `unmentioned-stay-asleep`：没被 @ 的成员不能被唤醒。
- 运行口径：`--attempts n`（默认 2，任一尝试通过即算过）是**回归口径**；`--runs n` 才是"每个模型跑 n 次、统计 pass rate 波动"的**测量口径**。报告可与 baseline 比较。

这已经是相当认真的工程验证：它能在固定模型与 commit 下，证明"多 Bot 协作路径没有静默坏掉"，并给出通过率和机制回归结果。

### 2 功能验收与覆盖报告

- `docs/qa/`、`docs/evidence/`、`docs/agents/*-qa.md` 有大量真实 DSH profile、真实模型、审批与截图的验收记录，例如 DM composer 的 Assignment 写文件、群工作区授权、Orchestrator 回复送达。这些是**功能/集成**验收，不是交付质量评估。
- [`docs/agents/verification-inventory.md`](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/agents/verification-inventory.md) 是覆盖度报告，但它自己明确：**functional-path coverage 和 verified-behavior rate 仍是 unknown**（分母不完整），报告检查的是报告/引用完整性，不是产品验收。
- `PRD.md` 的 AC-2.x 定义了委派、Assignment、报告、并发上限等功能验收标准；PRD 已标为历史草稿，且这些标准仍是"功能存在"，不是"交付成功"。

### 3 关键的一层缺失

把上面的证据与"交付能力"的定义对照，缺的是：

1. **对产物质量的检查。** 场景断言"有人发言/文件写了/最终消息出现"，不检查报告内容是否正确、代码是否通过独立测试、结论是否有来源支撑。
2. **长时程与真实纠偏。** 场景是分钟级合成任务；没有跨小时任务、用户中途改目标、失败后恢复、重复派发与虚报完成的统计。
3. **虚报完成（claimed done but failed）指标。** 没有把"模型说完成"与"独立检查通过"分开计数——这恰好是 Nuska 最关心的指标。
4. **样本与波动。** 默认 `--attempts 2`、任一通过即算过；`--runs` 虽支持 pass rate，但不是默认，也没有公开的长期结果。
5. **公开结果。** 报告只留在 CI artifact（3 天保留），没有公开的基准表、数据集或复现实验；外部无法核对趋势。
6. **独立评测。** 本次检索未找到第三方对 Tobs 交付能力的独立评测；找到的多是比较/营销文章与自动生成的仓库页，不能作为评估证据。

Tobs 自己的文档也承认边界。[`docs/qa/orchestrator-reply-delivery.md`](https://github.com/BotHarness/DeepSeekBot/blob/1e48294d86c681e308e989a8be967ecac21242b6/docs/qa/orchestrator-reply-delivery.md) 写："Finite repetitions measure regressions but cannot guarantee models will never omit a send." 这句话针对"回复送达"，但同样适用于整条交付链。

### 4 Tobs 自己的完成语义：报告 ≠ 验收

ADR-0045 明确把"执行活动"与"语义报告"分开：Assignment Directory 的 `activity`/`lastRun` 是 DSH 派生事实，`report_to_orchestrator` 是模型写的不可变 Source Event；lifecycle notice 又是 Host 写的另一类事实。三者分开，正是为了不把"模型说完成"当成"完成"。

但公开文档没有描述自动验收器：报告是给 Orchestrator/Human 判断的材料，不是判定结果。Tobs 的设计目标是"让状态可审计"，不是"证明交付成功"。

## 局限和未解问题

- 未运行 Tobs；上述场景是否稳定通过、pass rate 多少，本文没有数据。
- 仓库在活跃开发，`main` 的 scenario 集、CI 频率、artifact 保留期都可能变化；引用应固定 commit。
- "没有独立第三方评测"是本次检索范围内的负结果，不等于不存在；可能有未公开的内测或用户报告。
- 功能 QA 文档里可能包含个别交付相关的验收（例如 Assignment 写文件、报告回传），但它们不是系统性交付评估。
- Tobs 的公开 README/发布说明可能宣称"后台任务结果唤醒空闲 Bot、报告回来"等能力；这些是能力声明，不是完成率证据。

## 对 Nuska 的意义

- **不要把 Tobs 当成"交付已被证明"的参照。** 它是"身份/多房间/控制面"的强参照，也是"机制回归可以做到什么程度"的参照；交付能力仍需独立评测。
- Tobs 的 E2E harness 可以复用场景驱动、通过率和报告对比；需要补充独立 checker、长任务、用户纠偏、故障注入与虚报完成统计。
- 如果 Nuska 要做评测，最小可行方案不是新建大基准，而是把 Tobs/DS Bot/单 Bot 放进同一套 3 个真实任务 + 独立检查器 + N=5 的对照，先回答"结构差异是否真的影响 verified completion"。

## 下一步

1. 在隔离环境跑 Tobs 的 `llm-e2e`（至少 `long-task-reports`、`department-task`、`review-rounds`），记录通过率与失败模式；固定 commit、模型与 DSH 版本。
2. 设计 3 个可用机器检查的交付任务（研究/工程/外部依赖），各含一次用户改向、一次失败注入、一次重启；对单 Bot / ds-bot / Tobs 跑 N=5。
3. 指标按产物判：verified completion、claimed_done_but_check_failed、user nudges、dispatch drift、duplicates、pauses、recovery rate、wall clock；独立 checker 判卷，不用模型自述。
4. 若 Tobs 的 `--runs` 报告与独立检查结果不一致，记录差异并回查场景断言是否只检查了"消息存在"。
