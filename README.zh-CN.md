# agent-kit

**把有用的工程工作流带到不同的 coding agent，并让配置可以复现。**

用它比较两种设计方向，跑一次边界实验，或把项目交给另一个 Agent 接着做。可复用的技能和配套文件放在一个版本化仓库里，按眼前的任务选择。

[交给当前 Agent 配置](#交给当前-agent-配置) · [先试一个任务](#先试一个任务) · [English](README.md)

## 交给当前 Agent 配置

把下面这句话发给能执行本地命令的 coding agent：

```text
读取 https://github.com/cubxxw/agent-kit/blob/main/docs/bootstrap.md ，按当前任务为我正在使用的 Agent 配置最小适用套餐；保留已有环境，先展示完整变更计划，再验证一个技能能实际使用。如果技能已有其他管理器负责，就沿用它的接入路径，说明我能做什么以及还需处理什么。
```

Agent 会识别宿主，选一个小套餐，读完整变更计划，再报告验证结果。一般工程任务从 `developer` 开始；设计或实验按下面的任务选。

**已经用 CC Switch 管技能，就继续由它分发。** 添加 Agent Kit 技能仓库，选择需要的技能，照 [CC Switch 接入说明](docs/integrations/cc-switch.md) 操作。同一批技能目录无需再叠加原生安装器。

## 先试一个任务

| 想做什么 | 最后拿到什么 | 从哪里开始 |
|---|---|---|
| 找设计方向 | 两版可见的设计、比较证据，以及各自的产品判断 | `design` 中的 `deepen-design` |
| 验证一个不确定的边界 | 能跑的实验、正常与边缘及失败案例，还有对应证据的结论 | `prototyping` 中的 `boundary-demo` |
| 换 Agent 接着做项目 | 一份交接文件，写清当前状态和决策，记录已做验证与下一步 | [项目交接模板](examples/project-handoff/) |

已有首页，可以这样试：

```text
用 deepen-design 为这个项目比较两种明显不同的首页方向。从受众和产品事实出发，保留当前实现，给出原版与 A/B 的可见证据。先停在方向比较，让我选定后再做完整实现。
```

想先跑一个小实验，可以这样试：

```text
用 boundary-demo 比较订单提交重试时，有幂等键和没有幂等键的差别。在新的本地目录使用确定性的假适配器，覆盖正常提交、重复请求和提交成功后超时的案例。展示状态与执行轨迹，最后停在 supported、rejected 或 inconclusive。保持为一次性实验。
```

换 Agent 时，把项目和填好的 [交接文件](examples/project-handoff/) 一起交给它。Agent Kit 不会自动同步不同 Agent 的记忆和会话历史。

[首次使用指南](docs/first-run.md) 给出了 Claude Code 和 Codex 的完整操作，也写明每一步应该看到什么。

## 自己安装时，先选一个小套餐

原生安装器适合由 Agent Kit 管理技能链接的机器。先准备 Git、Python 3 和 coding agent。下面只配置 Codex；用 Claude Code 就把 `codex` 换成 `claude`。

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"

./bin/agent-kit doctor --strict
./bin/agent-kit plan --profile developer --tool codex --json
./bin/agent-kit install --profile developer --tool codex --dry-run
./bin/agent-kit install --profile developer --tool codex
./bin/agent-kit status --profile developer --tool codex
```

先读计划，再安装。`plan` 不改目录，返回 `ready`、`actions` 和 `conflicts`，逐项列出源文件与目标路径。有冲突时退出状态为 `2`；已有目录和外部链接要保留，不能强行覆盖。

首次使用要过三步。先确认文件链接正确，再确认当前 Agent 发现了技能，最后用一个任务检验结果。`status` 只验证文件链接，后两步见 [首次使用指南](docs/first-run.md)。

## 套餐按任务选

| 套餐 | 用来做什么 |
|---|---|
| `developer` | 一般工程与 Agent 集成；包含管理技能、`mcp-builder` 和 `source-driven-development` |
| `design` | 比较设计方向并检查界面；包含 `deepen-design`、`ui-ux-pro-max` 和 `design-taste-frontend` |
| `prototyping` | 用 `boundary-demo` 验证一个契约、状态变化或交互 |
| `writing` | 可选的 Threads 口述笔记工作流 `threads-oral-notes` |
| `base` | 只有 `manage-agent-kit`，负责管理配置，不包含任务技能 |

每个套餐都包含管理技能。已有的大套餐仍保留：`full-stack` 合并工程、设计和实验；`top` 再加可选写作；`all` 是 `top` 的兼容别名。先让一个小套餐在实际任务中有用，再决定是否扩大。

[`catalog.json`](catalog.json) 记录套餐和已接纳技能，也记录上游版本与许可证。[Top Skills Radar](docs/top-skills.md) 供发现新技能，本身不安装任何内容。

## 六种宿主的兼容路径需要在本机验证

原生安装器提供以下六种宿主的发现路径。兼容路径不代表六种宿主都经过完整端到端实测；请在自己使用的宿主里验证技能发现和任务结果。

| 宿主 | `--tool` | 默认技能目录 |
|---|---|---|
| Claude Code | `claude` | `~/.claude/skills` |
| Codex | `codex` | `~/.agents/skills` |
| Qwen Code | `qwen` | `~/.qwen/skills` |
| OpenCode | `opencode` | `~/.config/opencode/skills` |
| Pi | `pi` | `~/.pi/agent/skills` |
| OpenClaw | `openclaw` | `~/.openclaw/skills` |

`--tool core` 同时选择 Claude Code 和 Codex；只有明确要配置全部六种宿主，才用 `--tool all`。原生链接指向同一个本地仓库，更新该仓库会改变宿主读取的技能内容。

其他宿主可通过开放的 [skills CLI](https://github.com/vercel-labs/skills) 发现技能，再按名称选择。每个目标目录只用一个分发管理器。

## 密钥和运行状态留在本地

这个公开仓库存放技能与安全指令，也存放模板、已审查的 hook 代码和上游版本。密钥与认证留在本地；供应商、模型、会话、私人记忆和机器覆盖配置也留在本地。CC Switch 可以继续管理这些运行状态。

[`config/`](config/) 里的文件是供合并的示例，不能直接替换已有宿主配置。原生安装器拒绝覆盖已有目录和外部链接。升级要求工作区干净，且只做快进更新。

## 日常维护与验证

```sh
./bin/agent-kit doctor --strict
python3 -m unittest discover -s tests -v
./bin/agent-kit status --profile developer --tool codex
./scripts/check_upstreams.py
./bin/agent-kit uninstall --profile developer --tool codex --dry-run
```

自动配置可用 [`scripts/bootstrap.sh`](scripts/bootstrap.sh)，通过 `AGENT_KIT_PROFILE` 和 `AGENT_KIT_TOOL` 选择套餐与宿主。具体操作见 [配置协议](docs/bootstrap.md) 和 [维护手册](docs/maintenance.md)。

[架构](docs/architecture.md) · [工程实践](docs/best-practices.md) · [技能取舍](docs/skill-selection.md) · [质量审查](docs/quality.md) · [贡献指南](CONTRIBUTING.md) · [安全政策](SECURITY.md) · [第三方声明](THIRD_PARTY_NOTICES.md)

## 许可证

自有代码和文档使用 MIT 许可证。引入的第三方技能保留原许可证和署名，见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
