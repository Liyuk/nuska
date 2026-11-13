# Google Research Harness² 调研

调研日期：2026-11-12。依据 Harness² 官方仓库、仓库实验/安装文档及随附 arXiv 论文；论文为 2026-10-09 提交的预印本。

## 范围与方法

以项目仓库 README、SETUP、EXPERIMENTS 为实现和运行说明的一手来源，以 arXiv 论文正文与附录为方法、实验和失败案例的一手来源；结论均附直接来源链接。下文的流程、分数、配置和限制是作者/仓库报告的内容；“我的判断”和“与本项目的关系”是基于这些材料对适用范围的分析，不是论文实验证明。没有独立运行基准或验证论文数据；论文结果应理解为预印本所报告的结果。

## 结论

Harness² 是一套面向专业任务的 agent harness 在线改进框架。它保持基础模型权重不变，针对当前任务修改 agent 的外围运行配置，并把这轮修改的证据与经验存入持续改进库，供后续任务使用。重点是“改 prompt、guardrail、skill、script、工具与控制流”，而不是训练模型或提供一个面向终端用户的通用 agent 产品。[仓库 README](https://github.com/google-research/harness2) [论文](https://arxiv.org/abs/2610.14224)

适合研究/工程团队评估“执行轨迹能否指导 agent harness 适应新任务”的方法。若直接用于生产，要额外解决成本、无真值反馈下的误选，以及执行器网络隔离和工具权限边界。

## 工作机制

论文把流程分成两个递归层级：

1. **任务级递归（Propose–Probe–Compose）**：先有基线执行记录；改进器分别提出通用流程类（invariant）和领域类修改，使用相同任务探测修改后行为，再由 Composer 根据执行轨迹和产物的差异挑选、组合有效改动。过程不把 benchmark 的标准答案或分数交给改进器。
2. **改进级递归**：任务结束后，Reflector 记录被采用的 harness 及有执行证据支撑的可迁移经验。后续任务仍从共同的基础 harness 开始，由持续改进库指导提案，而非直接沿用前一任务的专用配置。

任务级有两种预算扩展方式：**parallel** 同时探测多个通用/领域候选，再做多次组合，探索更广；**sequential** 将每一步的 harness 和执行证据带到下一步，逐次深化。实验文档说明，同一领域内任务按顺序读取前序经验，不同领域可并行。[论文 §2](https://arxiv.org/html/2610.14224) [实验指南](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md)

可编辑 harness 共八类：system prompt、guardrails、memory、skills、tool guidance、scripts、subagents、middleware plugin。其设计思想是按故障类型选择最小有效部件：例如重复确定性转换用 script，多步且按需触发的流程用 skill，重复工具环路问题才考虑 plugin。[论文 §2 / 附录 D](https://arxiv.org/html/2610.14224)

### 算法细节：比较的是行为证据，不是正确性标签

一轮任务级改进可以拆为以下过程：

1. **建立参考执行**：用当前 harness 跑当前任务，保存工具轨迹和交付物。它只说明 agent 实际怎么做、产出了什么，并不说明产物正确。
2. **提出两种候选**：一个 invariant editor 处理跨领域可能重复的 agent 流程问题（规划、工具使用、上下文管理、委派）；一个 domain editor 处理当前领域的知识、步骤和约束。候选本质上是对 harness 文件的可执行修改。
3. **配对探测**：候选在同一任务、同模型和同环境设置下运行。与参考轨迹和产物对比，观察目标故障是否减少、行为是否没变、或出现回归。这是控制条件下的行为对比，仍会受采样波动影响。
4. **组合并复跑**：Composer 阅读参考与候选运行、候选之间的 diff 和已有证据，选择性合并、修订冲突、只采纳一项，或保留原 harness；随后实际运行组合后的 harness。决定应能对应到具体观察，而不是臆测“分数应该更高”。
5. **跨任务反思**：任务交付后，Reflector 阅读整轮记录，为有证据支持的修改写适用条件与经验；库保存被采用的 harness 以及经验条目。证据不足时可以不增加经验。

有一个容易误解的细节：当 `k > 1` 时，最终 selector 看的是匿名化交付物与任务请求/来源材料，无法看到对应 harness，也不生成新内容；它是在选择交付物，不是在确认哪条 harness 修改导致提升。因此作者把星号标为“采用”，不代表“已验证最优”。后续反思要回看全部候选与轨迹，不能只把获选候选里的每个改动都归功为有效。[论文 §2.2–2.3 与附录 H](https://arxiv.org/html/2610.14224)

### 两种递归模式的预算含义

| 模式 | `k` 的含义 | 优势与代价 |
| --- | --- | --- |
| Parallel | 先跑 `k` 个基线参考；提出并探测 `k` 个通用候选与 `k` 个领域候选；再各自用完整候选池生成 `k` 个组合和后续执行 | 候选覆盖广，探测/组合可并行；总计算显著增加。论文实现中这是一次 population update，`k` 控制宽度，不是多代进化。 |
| Sequential | 先取得 `k` 个基线执行，然后做 `k` 次连续的 Propose–Probe–Compose；后一步使用前一步 harness 和累计的执行历史 | 把每轮修订串起来，探索深度更强；早期错误或随机波动也可能影响之后的步骤。 |

`k=1` 时两种模式都退化为一个基础对比步骤，不需要最终多候选择器。每个任务完成之后，不论本任务采用哪种模式，改进库才更新；当前任务内不会边改 harness 边改进 improver。任务流内同一领域按顺序运行，以便后续任务只读到较早任务的库记录；不同领域可并发。[仓库实验指南](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md) [论文 §2.2](https://arxiv.org/html/2610.14224)

## 实验设计与结果解读

### 评测设置

论文研究的是**任务流中的在线、逐任务适配**：每项任务开始时都从共同的基础执行 harness 出发；刚完成的任务不会在之后重跑；没有 ground-truth 答案或带标签验证反馈提供给 harness improver。改进库按 benchmark stream 起始为空，再逐任务积累。主结果覆盖两种冻结执行模型（Gemini 3.5 Flash、GLM-5）与两种起始 harness（OpenCode、Codex），默认改进器是运行在 OpenCode 下的 Claude Opus 4.8。主表是单步 `k=1`，`+ Recursion` 是 parallel `k=5` 相对于单步的均值变化；均值与标准差来自三次打乱任务顺序的运行。[论文 §3.1](https://arxiv.org/html/2610.14224)

主要对照组分别代表：固定 harness 直接运行；从过去轨迹检索策略但不改 harness（ReasoningBank）；在训练集离线搜索 harness（Meta-Harness）；以及对每条评估实例加推理预算并改 harness、但不跨实例保留状态（Harness Scaling）。因此实验比较的不只是“有无额外 token”，还比较是否跨任务积累和如何利用执行证据。但论文说明这些方法具体预算与目标不同，基准分数也不能单独证明机制在生产分布上的因果收益。[论文 §3.1、附录 C](https://arxiv.org/html/2610.14224)

### 代表性分数

下面列出可直接对应论文主表的例子。括号中是论文报告的跨运行标准差；WorkBuddy Avg 是 Code/Web/Office 的宏平均，LAB Partial 是逐条 criterion 的通过率。

| 执行模型 / 起始 harness | 基线 | Harness² `k=1` | Parallel `k=5` 相对 `k=1` 的变化 |
| --- | ---: | ---: | ---: |
| Gemini 3.5 Flash / OpenCode，WorkBuddy Avg | 72.4 (0.9) | 77.5 (2.5) | +3.3 |
| Gemini 3.5 Flash / OpenCode，JobBench | 31.5 (1.1) | 36.0 (2.3) | +3.0 |
| Gemini 3.5 Flash / OpenCode，LAB Partial | 79.9 (0.6) | 81.9 (0.6) | +2.6 个百分点 |
| GLM-5 / OpenCode，WorkBuddy Avg | 64.2 (1.4) | 75.7 (2.2) | +3.9 |
| GLM-5 / OpenCode，JobBench | 20.6 (2.0) | 24.2 (0.9) | +4.2 |
| GLM-5 / OpenCode，LAB Partial | 59.6 (2.7) | 71.4 (2.9) | +6.7 个百分点 |

论文摘要所说的最高单步增益（WorkBuddy +11.5、JobBench +4.5、LAB +11.8 个百分点）来自各配置中相对各自 base 的最大值，并非上表某一行统一设置的效果。递归增益则是已应用一次 Harness² 后，再从 `k=1` 扩展到 `k=5` 的增量；不要把摘要的“最高增益”和表中某一配置混为一谈。[论文主表 1–2](https://arxiv.org/html/2610.14224)

### 机制消融与额外分析

在 Gemini 3.5 Flash + OpenCode、`k=1` 的消融中，移除改进库会使 WorkBuddy 平均分从 77.5 降到 74.4、JobBench 从 36.0 降到 34.2；移除通用/领域候选分工，分别降到 74.6 和 32.3；移除组合步骤，分别降到 75.9 和 34.1。这个结果支持三项设计在该实验条件下有贡献，但消融不能证明它们在所有任务上都必要或彼此作用可简单相加。[论文表 3](https://arxiv.org/html/2610.14224)

组件消融进一步显示，完整 `k=5` harness 在 WorkBuddy 的 Code/Web/Office 得分为 80.8/78.3/83.4；移除 skills 后平均下降 5.3 分，移除 scripts 后平均下降 3.7 分。Skills 对 Code/Web 尤其重要，scripts 对 Office 影响最大。说明改进可能落在执行机制与自动化工具上，不只是扩充 system prompt。[论文附录 E.1](https://arxiv.org/html/2610.14224)

作者报告 parallel 与 sequential 在 WorkBuddy Code 和 Office 上随 `k` 增至 5 得分总体提升；不过预算曲线并非所有任务、所有设置都相同，`k` 的增加也意味着更高计算量。跨任务测试中，从 JobBench 累积的经验库转到 WorkBuddy，可带来 Code/Web/Office +0.6/+0.5/+2.9 分；这是论文的回顾性迁移实验，作者明确指出它不是在线跨 benchmark 学习的证明。工具错误率在三基准下降，但 JobBench、LAB 的工具调用次数反而上升，说明可靠性提高不等于执行更短。[论文 §4、附录 E](https://arxiv.org/html/2610.14224)

## 工程实现与复现要点

### CLI 和运行产物

仓库把研究流程包装成 Python CLI：`harness2-setup` 安装基准，`harness2-check` 检查依赖/配置，`harness2` 跑 refinement，`harness2-judge` 评分，`harness2-report` 汇总；`harness2-demo` 用确定性编辑器与真实 Python 执行演示两种模式，不需要模型凭据。模型版默认走 Vertex AI 配置，也支持 Codex substrate。运行结果落在 `runs/`，包括任务摘要、交付物、采用的 harness、反思记录和评测输出；相同配置可续跑，改模型或任务选择时建议换 `HARNESS2_RUNS_DIR`。[README](https://github.com/google-research/harness2) [SETUP](https://github.com/google-research/harness2/blob/main/docs/SETUP.md) [实验指南](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md)

### 最小可复现实验路径

先在 Linux + Python 3.12 环境跑本地 demo，确认输出记录结构，再选一个 benchmark 的一个 domain 和一个任务做 dry run / 小规模模型实验。模型实验需要 Node.js 20+、Google Cloud CLI 和 Vertex 模型权限；LAB 额外需要 Pandoc、Poppler，WorkBuddy 需要 Docker。`--max-tasks` 是**每个 domain 的任务上限**，不是全局上限。每次比较 mode 或 `k` 时固定任务、执行器、改进器、judge 和网络策略；refine、judge、report 也必须用同一个 benchmark、executor、subset、k、mode、seed。`--seed` 只控制任务顺序，不控制模型采样，所以三次重复仍可能有模型随机性。[README](https://github.com/google-research/harness2) [安装指南](https://github.com/google-research/harness2/blob/main/docs/SETUP.md) [实验指南](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md)

JobBench 数据集在下载时解析而非固定到仓库提交；实验指南要求记录下载 revision。工作目录还包含第三方代码、模型配置、凭据、数据和生成产物，它们的许可证与 Harness² 的 Apache-2.0 不完全相同；WorkBuddy 上游许可对欧盟境内使用有地域限制。应分别检查 benchmark 与数据集许可证，不能只依据主仓库许可证判定整套运行都可用。[依赖与第三方说明](https://github.com/google-research/harness2/tree/main/dependencies) [实验指南](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md)

### 关键风险

- **rubric 泄漏**：基准与评分标准公开；JobBench 的 `RUBRICS.json` 可从 Hugging Face 下载。仓库记录过 Codex rollout 在未被指示时下载 rubric 的情况，因此默认网络环境不满足干净评测假设。依赖 executor 层网络策略阻断 Hugging Face、GitHub 等基准数据源，并在报告中披露限制；Codex sandbox disabled，不能把工具层设置当作网络隔离。[实验指南 Web access](https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md)
- **自评偏差**：行为差异能提示“这次怎么变了”，不能证明输出符合真实需求；selector 看任务和产物也可能选中较差候选。论文失败分析中，错误候选选择导致 WorkBuddy Code 出现 55 分候选胜过 95 分候选的反例，LAB 也有覆盖变窄使得分从 54 降至 26 的案例。[论文附录 E.6](https://arxiv.org/html/2610.14224)
- **错误假设扩散与归因不清**：多个候选可能共享同一个错误前提；一次 rollout 波动或同时修改多个组件时，无法可靠断言是哪条编辑导致改善。论文建议探测对共享假设提出挑战、重复执行以区分编辑效果和随机性。
- **费用/等待**：一个任务包含参考执行、候选提案与探测、组合、再执行和反思；递归预算会增加模型调用与 API 花费。parallel 主要降低可并发部分的等待时间，并不减少总工作量；论文没有给出适用于所有任务的最优 `k`。
- **经验库生命周期**：当前库是简单索引式持久化，论文将去重、过时经验淘汰、检索质量和按任务难度动态分配递归预算列为后续方向。积累数据多不自动等于经验质量更高。

## 与本项目的关系

对 nuska 而言，Harness² 可借鉴的是“把任务执行轨迹变成可审阅的 harness diff 和有证据的可迁移经验”，并把**提出修改、探测、采纳、写入经验库**作为几个独立阶段观察。它不等于把前序任务的全部配置永久叠加，也不提供通用工作流编排或产品级安全审批。若评估其思路，建议先选有可重复任务的小样本：记录基线与修改后行为、独立人工/程序 verifier 的结果、调用成本和任务耗时；只有独立验证信号支持的改动才考虑持久化。这样能检验它相对 nuska 已有的计划/执行/验证机制究竟增加了什么，而不是只对比更长的模型推理是否产生更好结果。
