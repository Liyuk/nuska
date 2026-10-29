# GitHub 仓库配置

Nuska 目前以研究和实验为主，社区入口保持简单，随着实际贡献和工程实现增长再调整。

## 参与入口

- Discussions：开放式研究想法、使用体验、问题与交流。Ideas 和 Q&A 提供可选背景字段，帮助交流，不要求先形成完整方案。
- Issues：具体研究任务、可执行的实验与验证、错误报告；也允许不套用模板的 Issue。
- Pull requests：提交文档、研究或实现，依照仓库现有模板说明变更和验证。

## 自动化与设置

- Documentation 工作流检查仓库内 Markdown 相对链接，以及提交或整个 PR 相对基线的空白问题。它不验证外部链接内容或研究结论。
- Dependabot 每月检查 GitHub Actions 的版本更新，更新仍需人工审阅。
- Issues 和 Discussions 已开放；不强制分支保护或自动合并，以适应当前项目阶段。
- 尚未声明许可证。公开可见并不等于已经授予开源许可，许可证需另行选择。

## 参考项目

以下为配置层面的参考，项目能力和适用范围各不相同：

- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)：Discussions、PR 模板及自动化配置。
- [DeepSeekBot](https://github.com/BotHarness/DeepSeekBot)：按讨论类别提供表单，收集问题背景与证据。
- [DS-Bot](https://github.com/Fei2411/DS-Bot)：Issue 模板及将提问引导至 Discussions。
- [AutoGen](https://github.com/microsoft/autogen) 和 [Pi](https://github.com/badlogic/pi-mono)：开放 Issues 和 Discussions 的社区入口。

实际配置可能随上游项目变化；Nuska 的设置按自身研究阶段选择，而非声称与它们一致。
