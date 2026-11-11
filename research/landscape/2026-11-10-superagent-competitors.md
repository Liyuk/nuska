# LobeHub 与通用 Agent 竞品：任务执行、工作空间和可部署性

状态：一手资料案头调研 · 2026-11-10。本文以 LobeHub 的 Agent 工作空间及其 Chief Agent Operator（CAO）为参照，比较可以接收自然语言目标、使用工具并交付多步骤工作的产品。Super Agent 在这里是产品类别描述，不假定它是 LobeHub 的正式产品名；Genspark 的 Super Agent 则是具体产品名。本文没有实际运行产品，也没有进行统一任务评测。

## 结论

最直接的比较对象有两组。**Manus、Genspark Super Agent、Claude Cowork、ChatGPT Work 和 Perplexity Computer**争夺把工作直接委派给 Agent 的用户；**Kortix/Suna 和 OpenClaw**则更接近 LobeHub 的可配置、可自部署平台路线。OpenHands 对编程 Agent 的执行和协调尤其相关，但不是一般办公场景的完整替代品。分类是本文依据公开定位做的判断，不表示产品边界固定。

多 Agent、任务看板和自我检查已经是多个产品的公开功能或设计方向。Nuska 不宜仅以这些部件的存在作为差异化；更值得验证的是用户改变目标后，系统如何更新计划及既有产物、依据什么判断交付完成，以及用户实际花多少时间审查和纠错。

## 比较范围和证据

比较的是用户可获得的产品或可运行平台，而非纯粹的 Agent SDK；优先阅读厂商产品说明、帮助文档和公开代码。表中“能力”指官方描述或源码可见机制，并非独立验证的效果。部署列区分运行环境和软件授权：本地执行不意味着模型推理或所有数据处理都发生在本地。

| 产品 | 面向的工作与可见机制 | 部署及可研究的区别 |
| --- | --- | --- |
| **[LobeHub / CAO](https://landing-staging.lobehub.com/changelog/page/2)** | 官方描述 CAO 能复查工作、决定下一步、必要时请求用户判断，并为较大任务委派子 Agent；LobeHub 提供 Agent、任务、知识和渠道。 | 云端及[自部署](https://github.com/lobehub/lobehub/blob/canary/docs/self-hosting/start.mdx)；重点研究任务、Agent 身份、会话和产物如何连接。[详细笔记](2026-11-10-lobehub.md)。 |
| **[Manus](https://help.manus.im/en/articles/17768086-what-are-the-differences-between-chat-mode-and-agent-mode)** | Agent 模式面向自主规划和复杂任务，可生成网站、幻灯片和视频等。 | 成品云服务；重点观察任务分解、执行可见性和最终交付物。官方说明不能证明每种任务都可靠完成。 |
| **[Genspark Super Agent](https://www.genspark.ai/helpcenter/super-agent)** | 用户描述期望结果并添加文件，Agent 在云计算环境中规划和执行，可交付报告、演示文稿、表格或网页等。 | 成品云服务；新模式按项目配置云计算机，官方称长任务可在关闭标签页后继续。适合比较输入门槛、产物与运行期间的交互。 |
| **[Claude Cowork](https://www.anthropic.com/research/how-we-contain-claude)** | 跨用户选择的工作目录和连接应用执行多步骤工作；可在需要信息时暂停。 | 桌面工作空间，本地文件访问与托管模型服务并存；适合观察文件权限、澄清与人工交接。[Anthropic 的工作示例](https://www.anthropic.com/news/claude-for-small-business)。 |
| **[ChatGPT Work](https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt)** | 面向较长、多步骤任务和交付物；云浏览器能操作支持的网站，在需要登录或确认时暂停。 | 托管产品与云浏览器；重点观察后台工作、登录接管及授权流程。原 ChatGPT agent 模式已由 Work 替代，勿把旧名称当作当前独立产品。[产品说明](https://help.openai.com/en/articles/11752874-chatgpt-agent)。 |
| **[Perplexity Computer](https://www.perplexity.ai/products/computer)** | 官方描述它能委派子 Agent、浏览研究、连接工具、产出内容，以及安排持续任务。 | 提供云端产品，也公布了支持的 Mac 本地模式；重点观察多模型编排、研究到执行和持续监控。[本地模式说明](https://www.perplexity.ai/en-GB/changelog/teammates-fully-local-computer-on-mac-and-voice-mode)。 |
| **[Kortix / Suna](https://github.com/kortix-ai/suna)** | 将 Agent、技能、记忆、连接器和触发器组织在项目中；文档描述每次会话使用独立沙箱及分支，通过 change request 审阅变更。 | 云端和自部署；适合研究配置版本化、工具权限、运行隔离和成果审阅。项目文档称工具审批门默认关闭，必须主动配置，不能假设所有外部动作默认等待批准。 |
| **[OpenClaw](https://github.com/openclaw/openclaw/blob/main/docs/index.md)** | 运行在用户设备，通过消息渠道接入，提供工具、会话、记忆和多 Agent 路由。 | 自部署、MIT 授权；更偏持续在线的个人助理和多渠道网关，部署在本地不代表所接模型服务也在本地。 |
| **[OpenHands](https://github.com/OpenHands/docs/blob/main/openhands/usage/agent-canvas/first-time-setup.mdx)** | Agent Canvas 可连接内置 Agent、Claude Code、Codex 等；公开文档定位内置 Agent 适合编程与探索。 | 可连接云端或本地／自部署后端；适合研究编码 Agent 工作台与执行后端，而非直接等同于完整通用办公平台。 |

## 各产品的关键取舍

### 面向结果交付，还是面向 Agent 运营

Manus 和 Genspark 的入口都是让用户描述想要的结果，再由产品组织执行和返回文件；Perplexity Computer 也将研究、浏览和执行组合成工作流。LobeHub 则显式暴露 Agent、任务和工作空间；Kortix 将 Agent、技能和配置放进项目仓库。这是根据官方界面和文档做的产品定位归纳，不是对底层架构或实际效果的排名。[Manus](https://help.manus.im/en/articles/17768086-what-are-the-differences-between-chat-mode-and-agent-mode) · [Genspark](https://www.genspark.ai/helpcenter/super-agent) · [Perplexity](https://www.perplexity.ai/products/computer) · [LobeHub](https://lobehub.com/task) · [Kortix](https://github.com/kortix-ai/suna)

对 Nuska 的问题是：用户只想交付工作时，应暴露多少任务和 Agent 细节？需要比较省去配置的效率，以及复杂任务发生错误时这些细节能否帮助人理解和干预。

### 执行环境决定可做的事，也决定运维边界

Genspark 官方称新 Super Agent 为项目提供云计算机；Kortix 文档描述每个会话有独立沙箱；Claude Cowork 使用用户授权的工作目录；OpenClaw 提供用户设备上的网关。它们在文件、网络、凭证和计算资源的边界不同；“能连接工具”本身不能说明工具权限足够细，也不能说明副作用能被恢复。[Genspark](https://www.genspark.ai/helpcenter/super-agent) · [Kortix](https://github.com/kortix-ai/suna) · [Cowork](https://www.anthropic.com/research/how-we-contain-claude) · [OpenClaw](https://github.com/openclaw/openclaw/blob/main/docs/index.md)

实际选择时需要逐项检查哪些文件离开本地、凭证由谁保管、Agent 能否写入外部系统、任务中断后有哪些已发生的副作用。上述问题不能仅由部署形式推断。

### 公开源码与可商用不是同义词

LobeHub 主仓库的 [Community License](https://github.com/lobehub/lobehub/blob/canary/LICENSE) 对开发并分发衍生作品设有商业授权条件；Kortix/Suna 的 [Elastic License 2.0](https://github.com/kortix-ai/suna/blob/dev/LICENSE) 限制以托管或管理服务向第三方提供软件的实质功能，项目另列白标授权条件。OpenClaw 的文档列出 MIT 授权。许可证、组件和版本各自独立；实际采用或分发前应检查选定版本的完整条款和依赖，必要时向项目方确认。

## 对 Nuska 的研究启发

1. **目标变化和成果的关系**：在工作过程中补充限制或改变方向，观察产品是否更新计划、标识受影响的既有结论，以及避免交付过期产物。当前资料不证明任何产品已解决这些问题。
2. **完成声明和验收证据分开**：LobeHub 描述了自我复查，Kortix 描述了供人审阅的 change request；两者都不自动证明结果正确。应记录每条要求对应的来源、测试或人工判断，比较错误放行和误拒绝。[LobeHub CAO](https://landing-staging.lobehub.com/changelog/page/2) · [Kortix](https://github.com/kortix-ai/suna)
3. **任务、会话、身份和执行记录分层**：同一个 Agent 可以有多次工作，一个任务也可以委派给多个参与者；研究用户如何追溯决定、查看子任务并接手，而不是只比较角色数量。
4. **中断与副作用**：记录系统在用户离线、工具超时和授权过期后如何继续；外部写入成功但结果未记录时，检查是否重复执行或错误报告。持久状态不等于副作用安全恢复。
5. **用户总成本**：除成功率和模型费用外，统计等待、澄清、审阅、修复及配置时间。复杂界面可能增加可观察性，也可能增加维护负担；二者需要实测。

## 建议的对照实验

首轮选 **LobeHub、Kortix、Manus 和 Claude Cowork**：前两者覆盖可配置平台，后两者覆盖面向成果的云端与桌面工作。每个产品固定可用版本、模型、付费方案和权限；能力受模型、计划与部署设置影响，不应将一次运行的差异直接归因于产品架构。

| 场景 | 统一输入及中途事件 | 可观察指标 |
| --- | --- | --- |
| 有来源的竞品报告 | 提供主题、来源范围、字数和可编辑格式；开始后要求排除一个来源。 | 来源有效率、约束遵循、旧内容是否被修订、人工纠错时间。 |
| 文件处理与交付 | 提供相同文件和输出模板；工具或文件访问在执行中短暂失败。 | 产物可打开性、失败提示、恢复后的重复或遗漏、人工介入次数。 |
| 有权限边界的外部操作 | 在隔离测试环境中要求准备变更，再明确要求审阅后执行。 | 是否区分准备与执行、权限提示、操作记录、最终环境状态。 |
| 多参与者分工 | 相同研究任务拆成可并行部分，并在中途更改一条关键要求。 | 任务分工和交接可见性、变更是否传播、整合结果是否一致。 |

对每个条件重复运行并保存输入、时间线、工具调用与最终产物；采用事先定义的验收规则，分别记录完成率、错误完成声明、时间、费用和人的工作量。不同产品的沙箱、集成和模型可能无法完全匹配，报告中应保留这些限制；此处只是实验方案，并非已开展的实验。

## 局限与后续

本报告是截至访问日的官方资料抽样，不是完整市场清单。产品文档会改变，也可能包含营销承诺；未部署、未实测、未核验定价和区域可用性，因此不对稳定性、性能、数据处理或性价比排序。下一步应实施上述同任务比较，并固定产品版本及证据，避免把源码中存在的机制当作实际可靠性的证明。
