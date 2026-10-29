# DSH 原语核验：安装版本、profile 组合与会话可用性

状态：静态核验（只读安装包与 profile 文件）· 2026-10-29。核验对象是 DSH `0.2.1-rc.2` 的本机安装、一个启用 `agent-team-profile` 的 web profile，以及 ds-bot `0.2.3`。未启动 DSH，未运行任务；"profile 启用"不等于运行时可用。

## 问题和范围

要回答的是：[多 Bot 群聊与交付](2026-10-29-dsh-multi-bot-composition.md)中关于八个 DSH 原语的说法，在**实际安装的版本**上是否成立，哪些需要修正；同时核对三件容易被文档层级混淆的事：profile 启用与 Bot 会话可用、群聊与记忆的归属、"消息已处理"是否存在。

范围限定在 DSH 包契约与静态组合：不评价模型效果，不比较 Grok Bot，不展开 ds-bot 的群回合与派活实现。被核验文档核对的上游快照是 `f3803c96`，安装版本是 `0.2.1-rc.2`，两者关系见下节。

## 材料和方法

行为证据全部来自本机安装；网络只用于核对被核验文档引用的快照版本（见版本对照），不用来支持行为结论。材料包括：

- `@deepseek-ai/dsh` 安装包及其 `node_modules/@deepseek-ai` 下的 305 个包：随包 `README.md`、编译产物 `lib/*.js`、`lib/types/*.d.ts`、`cordis.patch.yml`、`presets/*.patch.yml`。
- 一个启用 `@deepseek-ai/dsh-experimental-agent-team-profile` 的 web profile：`package.json` 的 `dsh.profile.bundles`、profile 自身的 `cordis.patch.yml`。
- 该 profile 安装的 ds-bot `0.2.3`：`README.md`、`src/host/*.js`。

方法：逐条阅读被核验文档的说法，再在安装包中定位支持或反驳它的原文；对"是否存在"类问题，用全文检索整个包集合的 README（例如 `group chat`、`MEMORY.md`、memory 包名），负结果按检索范围表述。只在关键处核对编译产物，例如 plan mode 是否注册工具拦截、Team 工具的作用域注册。本报告只判断"文档说法是否被安装包支持"，不判断该能力是否适合 Nuska；适合性放在最后一节，且写成候选。

证据形态有一处限制要先说明：npm 发布包只有编译后的 `lib/*.js` 和 `.d.ts`，没有上游 `src/*.ts`。因此下文 `file:line` 指向安装包内的 README 或编译产物，不指向 GitHub 源码；README 随包分发，与实现同源，但不保证逐行同步。

路径写法：

| 写法 | 含义 |
| --- | --- |
| `dsh-goal/README.md:32` | 安装包 `@deepseek-ai/dsh-goal` 的 README 第 32 行；同一文件后续行号写作 `:98` |
| `dsh-experimental-agent-team-profile/cordis.patch.yml:4-14` | 同名 bundle 的 patch 行 |
| `ds-bot/src/host/roster.js:70-74` | 该 profile 安装的 ds-bot 0.2.3 包内文件 |
| `web profile 的 package.json` | 被核验 profile 的清单；不写用户目录 |

GitHub 链接只用于固定上游快照。DSH 的安装包没有 commit 可供固定，因此凡涉及安装版本的证据只给"包名 + 文件 + 行号"。

## 发现与证据

### 版本对照：文档快照与安装版本不是同一个发布

| 项 | 值 | 依据 |
| --- | --- | --- |
| 被核验文档引用的 DSH 快照 | `f3803c96`，该提交的发布版本是 `0.2.2-alpha.2` | [`f3803c96`](https://github.com/deepseek-ai/deepseek-harness/commit/f3803c96974ad4a94195fb97e5c637e9c2a3afe3)；[该提交的 `apps/cli/package.json`](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/f3803c96974ad4a94195fb97e5c637e9c2a3afe3/apps/cli/package.json) |
| 本机安装的 DSH | `0.2.1-rc.2` | 安装包 `package.json:4` |
| 安装包是否带 commit 指纹 | 否。`dsh`、`dsh-goal`、`dsh-experimental-agent-team`、`dsh-workflow`、`dsh-tool-ralph` 的 `package.json` 均无 `gitHead` | 包内 `package.json` |
| ds-bot | `0.2.3`，对应 tag `v0.2.3` = commit `4a7b550` | [DS-Bot 仓库 `4a7b550`](https://github.com/Fei2411/DS-Bot/tree/4a7b55069ad300eae8be42a74f31bc170b40ead7) |

结论分三点：

1. 被核验文档第 3 行的"核对的 DSH 上游源码版本为 `f3803c96`"只说明它读的是 `0.2.2-alpha.2` 的快照，不能当作"已核对本机安装版本"。
2. 本机安装是 `0.2.1-rc.2`，与 `f3803c96` 不是同一发布；按 semver，`0.2.2-alpha.2` 的版本号更高，但两者的发布先后不能从包内判断。
3. 被核验的这些包不带 `gitHead`，**不能从包内确认安装版本对应哪一个 git commit**。要固定证据，只能固定版本号（`0.2.1-rc.2`）与包内文件行号；若按文档给出的 GitHub 链接去读，个别默认值和包结构可能与本机不同，不能互相替代。

下文所有"实际"都按 `0.2.1-rc.2` 重新取证；与被核验文档重合的部分，结论基本一致。

### 八个原语的逐条核验

表中的"实际"是包内契约与静态组合的读解，不是运行时行为。

| 原语 | 文档说法 | 实际（带 file:line） | 是否需要修正 |
| --- | --- | --- | --- |
| Goal 域、goal 工具与 round driver | 同会话单个当前目标、修订与状态；Agent 空闲后准入后续 round；不自带跨 Bot 目标、重启自动续跑或独立验收 | 成立。单目标与"会话日志是唯一权威"见 `dsh-goal/README.md:12`、`:159-160`；变更必须带精确 `{id, revision}`（CAS）见 `:98`；driver 只在整体 idle、必要时等后代收敛后开轮，上限记稳定码 `round-limit`，resume/fork 后 active goal 一律 disarm，见 `dsh-goal-round-driver/README.md:53`、`:57`、`:125`；子 Agent 不能 create/edit 见 `dsh-tool-goal/README.md:55`。默认轮次上限 256 见 `dsh-goal/README.md:12`，连续 3 个 round 才允许自动 block 见 `dsh-tool-goal/README.md:12` | 否。把原文"额度耗尽与停止语义需按当前版本验证"替换为 256、`round-limit`、连续 3 轮 |
| Plan Mode | 自愿进入计划模式，探索后提交计划供人审核；状态可在恢复和 fork 后重建；只是提示引导，不自动阻止工具 | 成立。包内只注册一个 prompt section 和一个 `exit_plan_mode` 工具，以文本约束而非过滤能力，README 自述"Guidance, not enforcement" — `dsh-plan-mode/README.md:81`、`:184`；进入/退出由 `/plan` 与 Approve/Keep planning 驱动，见 `:12`、`:61`；状态是唯一的 log-only 全量替换事件 `plan/mode`，resume/fork/compaction 靠折叠日志恢复 — `:81`；fork 的 Agent 继承日志里的 plan 状态，新 spawn 的 Agent 从 inactive 开始 — `:186`。另核对编译产物：`dsh-plan-mode/lib/index.js` 未出现 `pre-execute` 或工具 guard 挂点 | 否。可补 fork 与 spawn 的差异 |
| Repeat Tool Reminder | 基础 bundle 默认启用；同 Agent、同工具、规范化参数相同时，默认第 3、5、8 次提醒；只建议不阻止；不检测变形重复、无进展对话或跨 Agent 循环 | 成立。`dsh-base` 的 patch 直接挂载该行 — `dsh-base/cordis.patch.yml:448-449`；默认阈值 `[3, 5, 8]` — `dsh-repeat-tool-reminder/README.md:49`；第 3 次是简短提醒，第 5、8 次是带工具名与参数预览的详细提醒 — `:58`；`Advisory, not veto` — `:74`；精确匹配、变形可绕过 — `:168`；父子 Agent 不共享链 — `:171`；超过最高阈值后静默 — `:173`；被 deny 的调用也计数（挂在 `tools/post-execute`）— `:75` | 否。补"精确计数触发、超阈值静默"与"3 次温和、5/8 次详细" |
| Agent Team | Lead 与具名 teammate、直接 inbox 消息、持久 roster 与共享任务板；任务有依赖并可由成员 claim，更新用 revision 防止覆盖；实验性、单进程、共享 cwd；owner 不自动释放；消息入 inbox 不等于已处理 | 成立。Lead 身份、永久名字与 roster 状态 — `dsh-experimental-agent-team/README.md:12`、`:60-62`；发送成功只表示目标 inbox 接受 — `:70`，工具侧同一句见 `dsh-experimental-tool-agent-team/README.md:68`；任务依赖、claim 与 CAS 拒绝过期 revision（`TEAM_TASK_STALE_REVISION`）— `dsh-experimental-agent-team/README.md:74-76`、`:136`；实验性、单进程、共享 cwd、owner 不自动释放 — `:202-207`；历史 `team/message/queued`、`delivered` 只读兼容，Team 不再写入或投递 — `:144`、`:146`。该 profile 的 patch 把 `maxMembers` 配成 8（默认 16，见 `:51`）— `dsh-experimental-agent-team-profile/cordis.patch.yml:20-23` | 否。补成员上限 8，以及"无已处理语义"是结构性缺失 |
| Agent Team Profile | 在具备 base 的 profile 上组合 Team、工具和 Web 成员/任务板；默认关闭；其组合会禁用部分同名普通 subagent 工具 | 上游默认关闭成立：内置模板不含该 bundle（`dsh-app-boot/lib/index.js:551-559`），它被列入 `OPTIONAL_BUNDLES`（同文件 `:570-588`），bundle README 也要求显式启用（`dsh-experimental-agent-team-profile/README.md:12`）。但在一个启用该 bundle 的 web profile 上，`dsh.profile.bundles` 已列出它；按 patch 语义，根组合插入 `agent-team`、`tool-agent-team`、`ui-agent-team`，并把四条 legacy subagent 行置 `disabled: true`（`dsh-experimental-agent-team-profile/cordis.patch.yml:4-14`、`:16-32`）。同时 Web 的 `standard` preset 在 preset 内重挂同名工具（`dsh-web-app/presets/standard.patch.yml:89-103`），Bot 会话在 `standard` 可用时绑定该 preset（`ds-bot/src/host/roster.js:70-74`），preset 的插件决定模型可见工具（`dsh-agent-preset-registry/README.md:85`） | **是**。改为"上游默认关、该 profile 已启用"，并说明根层 disabled 不覆盖 preset 作用域 |
| Ralph | 不可变目标；每轮新子 Agent；共享工作区；有界交接报告；前台执行；完成与证据是 worker 报告 | 成立。每轮一个 fresh child，父对话与上一轮子会话不复制 — `dsh-tool-ralph/README.md:12`；每轮只拿 objective、轮次、workspace-as-authority 指令与上一轮 handoff — `:36`；`maxHandoffChars` 默认 16384，非法或超限直接失败 — `:43-45`；前台、无 job id、无恢复检查点 — `:162`；完成是 worker 自述、无独立评估器 — `:161`；实现上是架在 `ctx.workflowEngine` 与 `ctx.subagents` 上的固定脚本 — `:61`。该 profile 启用的 ralph bundle 把 `maxRounds` 配成 64（README 默认 256）— `dsh-experimental-ralph-bundle/cordis.patch.yml:16` | 否。补本机 64 与"架在 workflow 引擎上" |
| Workflow | 脚本可调用 `agent()`、`parallel()`、`pipeline()`；可对结构化子结果做 schema 校验；只支持前台收集；重启不恢复进度 | 成立。另有 `phase()`、`log()`，脚本是纯 JS 体并支持顶层 await — `dsh-workflow/README.md:36`；带 schema 的 `agent()` 返回已校验的结构化值，hook 误用时整脚本失败而非静默 `null` — `:57`；结果永不 reject，脚本错误为 `stopReason: 'error'`，调用方必须 `dispose()` — `:53`；仅前台收集 — `:126`；无 journaling/resume — `:127` | 否。补"结果不 reject、须 dispose" |
| Skill | 提供可复用指引与模板，可让 Agent 在适合场景读取；指引不是强制执行或验收保证 | 成立。首个请求前注入耐久 catalog（名称 + 截断描述），模型用 `skill` 工具加载全文，用户也可用 `/name` 注入 — `dsh-tool-skill/README.md:12`；加载结果以 `<skill_content>` 块作为普通工具历史 — `:54-55`；`dsh-tool-skill/lib/index.js` 未见 `pre-execute` 或工具 guard 挂点，指引没有强制层 | 措辞微调。改为"系统预注入目录、模型自加载；不加载即不生效" |

八条中，六条成立（Goal、Plan Mode、Repeat Tool Reminder、Agent Team、Ralph、Workflow），一条只需措辞微调（Skill），一条需要实质修正（Agent Team Profile）。成立不等于可以原样搬用：其中两条（Team 成员上限、Ralph 轮次上限）的配置值与本机安装不同，另有一条的关键限制（消息无"已处理"语义）在原文档中只写成了现象，没有写成结构性缺口。

### 需要修正或补充的具体条目

- 版本（文档第 3 行）：把 `f3803c96` 从"核对的版本"改为"引用的上游快照"，另注本机安装 `0.2.1-rc.2`、包内无 commit 可固定。
- Goal（第 15 行）：把"额度耗尽与停止语义需验证"落定为默认 256 轮、稳定码 `round-limit`、连续 3 轮才允许自动 block；补一句子 Agent 不能创建或编辑目标。
- Repeat Tool Reminder（第 17 行）：补第 3 次温和、第 5/8 次详细、超阈值静默、被 deny 的调用也计数。
- Agent Team（第 18 行）：补该 profile 的 `maxMembers: 8`（默认 16）；把"消息入 inbox 不等于已处理"升级为"没有已处理事件"的结构性判断。
- Agent Team Profile（第 19 行）："默认关闭"改为"上游默认关闭、在一个启用该 bundle 的 web profile 上已启用"，并说明根层 `disabled` 不覆盖 `standard` preset 的重挂。
- Ralph（第 20 行）：补该 profile 的 `maxRounds: 64`（默认 256）与"架在 workflow 引擎和 subagent 之上"。
- 群聊层（第 41 行）：补一句群聊、Bot 身份与群记忆由 ds-bot 提供，DSH 没有原生群聊或记忆。
- Skill（第 22 行）：改为"系统预注入 catalog、模型调用 `skill` 加载全文；不加载即不生效；无强制与验收"。

### 文档漏掉的已装原语

以下包都存在于被核验安装的包集合中；每条一句，证据指向包内文件。

1. **事件溯源会话日志**：每个 session 是一份 append-only 事件日志，模型可见历史由日志派生，compaction 只隐藏不删除 — `dsh-session/README.md:12`。
2. **会话持久化与崩溃恢复**：默认 Zstandard 分帧的 `session.v<gen>.jsonl.zstd`，每次追加在返回前 fsync，崩溃后丢弃残缺行与残帧 — `dsh-session-persistence-jsonl/README.md:12`、`:77`；磁盘布局见 `:66-70`。
3. **会话 fork**：`ctx.sessions.fork(source, boundary?, childSessionId?)` 复制精确闭区间的事件前缀，只补开放 step 的缺失 tool result，并以 `forked` 原因关闭 — `dsh-session/README.md:80-82`。
4. **跨会话只读检索**：五个只读工具（会话检索、事件检索、会话追踪、事件追踪、事件读取），仅当目标 session 的 cwd 与调用者完全相等才授权 — `dsh-tool-session-query/README.md:12`、`:53`。
5. **定时提醒**：Host 级持久提醒，投递为原 Session 的 follow-up 消息，Host 重启后仍在 — `dsh-schedule/README.md:12`、`:26`；模型侧四个工具由 preset 决定可见性 — `dsh-tool-schedule/README.md:12`。
6. **todo_write**：per-session 单一任务列表，整表替换，只有所属 Agent 能改，跨轮与重开会话保留 — `dsh-tool-todo/README.md:12`、`:32`。
7. **后台作业**：`job_output`、`job_list`、`job_kill`，作业完成会给属主 Agent 一个 in-session 通知，忙的下一步收到、闲的被 follow-up 唤醒 — `dsh-tool-jobs/README.md:12`、`:40`。
8. **worktree 隔离**：从本地 commit 建新分支和新目录并把当前 Session 切过去，源 checkout 不动 — `dsh-experimental-worktree/README.md:12`。
9. **交付物 `present`**：把已存在的文件声明为最终交付物，只记路径与描述，不复制内容 — `dsh-tool-present/README.md:12`。
10. **用户交互**：`ask_user_question` 默认等待回答，`mode: timed` 可设截止时间让模型先做独立工作；活着的子 Agent 不能调用 — `dsh-tool-ask-user/README.md:12`。
11. **上下文压缩**：接近上下文上限时把最旧历史压成摘要，溢出错误后压缩重试，`/compact` 可手动触发；不能压缩系统提示、工具或 session 前缀 — `dsh-compaction-basic/README.md:12`。
12. **权限、沙箱与审批**：权限预设把 sandbox mode 与 approval policy 捆成用户可选档位；沙箱默认 `read-only`，切换写入日志并按 replay 恢复；approval 是一次性决策，应答器缺失即 fail-closed — `dsh-permission-presets/README.md:12`、`dsh-sandbox-policy/README.md:36`、`dsh-user-approval/README.md:12`。

这些原语不是一套并列的编排器。goal 是同一 Agent、同一会话的续跑，不 spawn 新 Agent（`dsh-goal-round-driver/README.md:126`）；workflow 的每个 `agent()` 落到 subagent provider（`dsh-workflow/README.md:36`）；ralph 架在 workflow 引擎与 subagents 之上（`dsh-tool-ralph/README.md:61`）；team 的成员由 subagent provider 创建（`dsh-experimental-agent-team-profile/cordis.patch.yml:25-29`）；todo 只是当前会话的清单（`dsh-tool-todo/README.md:32`）。只有 workflow 和 ralph 提供脚本级控制流，包集合中没有统一编排器。

### 关键发现

#### 1. profile 层启用 Team，与 Bot 会话能否使用 Team 是两件事

在一个启用 `@deepseek-ai/dsh-experimental-agent-team-profile` 的 web profile 上核对：`dsh.profile.bundles` 共 16 项，其中包含该 bundle；profile 自身的 patch 未覆盖 Team 行，后续 bundle 也没有把四条 legacy subagent 行重新启用。按该 bundle 的 patch，根组合插入 `agent-team`、`tool-agent-team`、`ui-agent-team`，并把 `tool-subagent-control`、`tool-subagent-list-agents`、`tool-subagent`、`tool-subagent-fork` 置 `disabled: true`（`dsh-experimental-agent-team-profile/cordis.patch.yml:4-14`、`:16-32`）。在这个 profile 里，Web 自己的 patch 也已在根层关掉这四行（`dsh-web-app/cordis.patch.yml:555-565`），Team bundle 的四条是重复声明；真正决定 Bot 会话可见工具的是下一段的 preset。

但 Bot 会话的可见工具不由 profile 根层决定。Web 的 `standard` preset 在 preset 内重新挂了一套同名 legacy subagent 工具（`dsh-web-app/presets/standard.patch.yml:89-103`）；ds-bot 在 `standard` 可用时给每个 Bot 绑定 `agentPreset: 'standard'`（`ds-bot/src/host/roster.js:70-74`）；preset 的插件才决定该 Agent 的模型可见工具与提示段（`dsh-agent-preset-registry/README.md:85`）。Team 工具本身是 Agent 作用域注册（`dsh-experimental-tool-agent-team/lib/index.js:222`）。

因此，"profile 启用 Team"只能证明根组合里有 Team 服务、工具与 UI；Bot 或 Lead 会话是否拿到 `spawn_teammate`、`team_task_*`、`wait_agent`，取决于该会话所用 preset 与 Agent 作用域，**需实测**。同一层逻辑也适用于其他原语：外层插件可以再做工具级过滤，例如 ds-bot 对 Bot 会话隐藏 goal 三工具并主动 block 已存在的 active goal（`ds-bot/src/host/tools.js:17-20`、`:760-764`）。

若上述推断成立，Bot 会话的工具表应出现 legacy 的 `subagent` / `subagent_fork` / `list_agents`，而不出现 Team 的 `spawn_teammate` / `team_task_*`。

**这条预测已被一次观察推翻（2026-10-29 更正）**：在一个 ds-bot Main Bot 的会话中，工具表同时包含 Team 的 `spawn_teammate`、`team_task_create/get/list/update`、`list_agents`、`wait_agent`、`send_message`，以及 ds-bot 的 `create_bot`、`post_to_group`、`message_bot` 等群/Bot 工具；同一会话的 `list_agents` 能返回该 Team 的 Lead。也就是说，**Bot 会话拿到 Team 工具是可能的**，`agentPreset: 'standard'` 不是唯一决定因素——该会话本身可能同时被当作 Team 的 Lead 会话装配。

因此正确的表述是：Team 工具是否可见取决于会话的实际装配路径，**同一功能（Bot 会话）里也可能有两种结果**，必须逐会话核验，不能用"Bot 会话"这一个条件推断。上面那条预测应改写为"在某些 Bot 会话里可能只有 legacy subagent 工具"，而不是"应该只有"。

#### 2. 群聊与记忆不来自 DSH，而来自 ds-bot

在被核验安装的 305 个包中检索 README，`group chat` / `群聊` 无命中；唯一带 group 的包是 `cordis-plugin-group`，它是 Cordis 的插件分组加载器，与聊天无关（`cordis-plugin-group/README.md:1-12`）。包集合里也没有 memory 包。

ds-bot 的 README 写明它把 dsh 变成 "a team of long-lived Bots that talk to you, to each other and in group chats"（`ds-bot/README.md:3`）；群聊工具 `create_group`、`update_group`、`delete_group`、`post_to_group`、`group_relay`、`read_group_chat`、`read_own_chat` 由 ds-bot 注册（`ds-bot/src/host/constants.js:65-72`，实现见 `ds-bot/src/host/groups.js:2`、`:575`、`:738`）。记忆也是 ds-bot 的：Bot / 群 / 团队三个作用域，以及每轮后的自动 memory review（`ds-bot/src/host/memory.js:3-8`、`:17-20`；`ds-bot/README.md:92-98`）。

结论：群聊、Bot 身份、群记忆与 Bot 间消息是外层插件能力，不是 DSH 原语。被核验文档把"群/Bot 交互层"写成候选待建时，应明确这一层已由 ds-bot 提供；DSH 侧只提供会话、工具、Team 等底座。

#### 3. DSH 全域没有"已处理"语义

Team 的发送只保证 inbox 接受：`Success means inbox acceptance, not model processing or a separate synchronous storage flush`（`dsh-experimental-agent-team/README.md:70`）；工具侧只说 `{ "sent": true }`，并明确 "A successful send does not mean the recipient has processed it"（`dsh-experimental-tool-agent-team/README.md:68`；`dsh-experimental-tool-agent-team/lib/index.js:29`）。历史事件 `team/message/queued`、`team/message/delivered` 只读兼容，Team 不再写入、投递或确认（`dsh-experimental-agent-team/README.md:144`、`:146`）。

legacy subagent 控制同理：送达消息"没有独立结果"，只返回 inbox `messageId`（`dsh-tool-subagent-control/README.md:168`、`:137`）。最接近"进展"的 `wait_agent` 只等待下一次 Team 变化或超时，不唤醒成员，调用方醒来后要重新读状态（`dsh-experimental-tool-agent-team/README.md:61`、`:68`）。

在被核验的安装中，没有包提供"对端已处理/已消费"的事件或查询。这是结构性缺失：不能靠重试或补事件解决；要确认处理，只能依赖任务板 revision、成员状态（`running`/`inactive` 仍不等于结果）或产物检查。

## 局限和未解问题

- 全部结论来自静态阅读与静态组合；未启动 DSH，未运行任务。"实际"是包内契约，不是运行时观测。
- profile 组合是按清单与 patch 语义读出的，没有调用加载器实际合成；若 profile 或 bundle 列表变更，结论需重算。
- 版本：文档快照 `f3803c96`（`0.2.2-alpha.2`）与安装 `0.2.1-rc.2` 不同；包内无 `gitHead`，不能确认安装包对应哪一个 commit。README 与编译产物可能不同步，本报告只在关键处核对代码。
- 未能确认：Bot/Lead 会话的实际工具表（Team 工具是否可见）；Team 与 goal driver 同时运行时的生命周期与权限；中断或重启后 owner 与消息状态；本机沙箱与审批组合的运行时拦截面。
- 负结论的边界："未找到"限定在被核验安装的 305 个包及其 README、编译产物，不等于上游其他版本或未来版本没有。
- 未覆盖：ds-bot 的群回合、派活树、分段续行等实现细节；本报告只核对其与群聊、记忆、goal 过滤相关的边界。

## 对 Nuska 的意义

1. **承载层**：Team 的 roster、任务板、依赖与 CAS 可作为协作底座候选，但它实验性、单进程、共享 cwd、owner 不自动释放，不是现成的群聊或长期 Bot 身份产品。
2. **群与记忆层**：DSH 没有原生群聊和记忆；若 Nuska 需要多 Bot 群聊、Bot 身份与跨会话记忆，这一层需要外层提供（复用 ds-bot 式插件或自建），并明确可见范围与权限。
3. **确认语义**：不要设计依赖"消息已处理"的流程；候选方案应把任务 revision、成员状态与产物/证据检查组合起来，且成员状态不等于结果。
4. **能力边界**：profile 开关只是第一层；preset 与 Agent 作用域、外层插件的 restrict 才决定会话实际可见工具。插件或实验设计应声明目标 preset 与作用域。
5. **版本纪律**：引用 DSH 能力时绑定版本；GitHub 快照与安装版本不一致时，不能互相证明。

## 下一步

1. 在隔离 profile 启动，逐个记录会话的工具表（含 ds-bot 的 Bot 会话与 Team 的 Lead 会话），把"哪种装配路径会拿到 Team 工具"确定下来。第 1 节已有一个反例，说明只看功能类别不够。
2. 用两个 teammate 完成一个真实任务：记录 inbox 接受、实际处理、任务 revision 与产物，检验"无 ack"下如何确认处理。
3. 中途改变目标、中断 owner 并重启：观察 goal disarm、owner 是否释放、消息状态与任务板 revision。
4. 对照 ds-bot 层的同一任务：比较群/Bot 与 DSH Team 在可见性、记录和验收上的差异，决定哪一层承载交付状态。

本报告只做静态核验：未启动 DSH，未运行任何任务。文中"profile 已启用"只表示该 profile 的清单与 patch 如此，不等于运行时可用；上述判断需按"下一步"实验验证。
