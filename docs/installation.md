# 安装与使用

Project Alchemy 的中文名称是“项目资产抢救企划”，技能标识是 `project-salvage`。它从项目文件和开发历史中找回可复用的经验、模块与知识资产。安装同一份 skill 即可，不需要为各应用维护不同版本。

## 一条命令安装

使用 [Vercel Labs 的 skills 安装器](https://github.com/vercel-labs/skills)。准备 Node.js 22.20+，打开终端，按使用的应用选择一条：

```sh
# Codex
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a codex -g --copy -y

# Claude Code
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a claude-code -g --copy -y

# Cursor
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a cursor -g --copy -y

# Gemini CLI
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a gemini-cli -g --copy -y

# OpenCode
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a opencode -g --copy -y
```

`-g` 表示安装到个人目录，供多个项目使用。只想给当前项目安装时，先进入那个项目目录，去掉 `-g`。`--copy` 使用文件复制，避免符号链接的额外配置。要自行选择多个应用，省略 `-a ... --copy -y` 即可进入选择流程。参数见[安装器说明](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

Windows PowerShell 若提示无法运行 `npx.ps1`，将命令中的 `npx` 改成 `npx.cmd`，其余参数不变。

## 下载 ZIP 手动安装

1. 下载[独立 skill ZIP](https://github.com/Usernamethatavailable/project-alchemy/releases/latest/download/project-salvage.zip)。
2. 解压后，将整个 `project-salvage` 文件夹复制到下表中对应的技能目录。若已有同名目录，先备份旧版本，再替换完整 skill 文件夹。
3. 新开一次应用会话，再按下一节试用。

| 应用 | 个人安装位置 | 只给当前项目安装 |
| --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `~/.agents/skills/project-salvage/` | `.agents/skills/project-salvage/` |
| [Claude Code](https://code.claude.com/docs/en/skills) | `~/.claude/skills/project-salvage/` | `.claude/skills/project-salvage/` |
| [Cursor](https://cursor.com/docs/skills) | `~/.cursor/skills/project-salvage/` | `.cursor/skills/project-salvage/` |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `~/.gemini/skills/project-salvage/` | `.gemini/skills/project-salvage/` |
| [OpenCode](https://opencode.ai/v2/docs/skills) | `~/.config/opencode/skills/project-salvage/` | `.opencode/skills/project-salvage/` |

`~` 代表当前用户的主目录。安装器可能使用应用支持的共享 `.agents/skills` 路径；上表给出手动安装可用的位置。

安装后应能直接找到 `技能目录/project-salvage/SKILL.md`，旁边保留 `references`、`assets`、`scripts` 和 `agents`。不要只复制 SKILL.md，也不要把整个仓库套进技能目录。

### Claude 网页版与 Desktop

下载同一份 skill ZIP，在 Claude 的 **Customize → Skills → + → Create skill → Upload a skill** 上传并启用。Skills 需要启用代码执行与文件创建；界面步骤见 [Claude 官方说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)。

Claude 网页版处理上传的文件或连接来源；安装 skill 不会让网页自动读到本机磁盘。要按本机项目路径直接分析，可用具有文件访问权限的 Claude Code，或在支持本地文件访问的模式中授权项目目录。

## 确认安装与调用

通过安装器安装后，运行 `npx --yes skills list -g` 查看个人技能；项目安装则去掉 `-g`。新会话中按应用选择调用方法：

| 应用 | 手动调用 |
| --- | --- |
| Codex | `$project-salvage`，然后写项目路径和要求 |
| Claude Code、Cursor | `/project-salvage`，然后写项目路径和要求 |
| Gemini CLI | `/skills list` 确认已发现，再说“使用 project-salvage 复盘这个项目” |
| OpenCode、Claude 网页版及其他应用 | 直接说“使用 project-salvage，整理这个项目的可复用经验” |

通用试用请求：

```text
使用 project-salvage。项目在 /path/to/project。
先只读分析，生成一份完整复盘：关键开发历史、经验总结、可复用模块、项目规则建议和留存安排。
正文尽量用非技术语言，不修改源项目。
```

支持自动选用的应用，会根据“复盘项目、沉淀经验、留存知识资产、找可复用模块、以前怎么解决”等意图选择本 skill。自动选用是处理当前请求；后台定时执行需要另行配置。

若菜单里找不到技能，先检查 SKILL.md 是否直接位于正确目录、是否安装到了当前项目或当前用户，再重开会话。Gemini CLI 也可以使用 `/skills reload` 刷新。

## 更新与移除

安装器安装的个人版本可运行 `npx --yes skills update project-salvage -g` 更新；项目版本使用 `-p`。移除个人版本可用 `npx --yes skills remove project-salvage -g`，按提示选择应用。手动安装或 Claude 上传版则下载新 ZIP，替换原 skill，或在应用中重新上传。

个人经验库保存在用户指定的位置，独立于安装目录。更新、替换或移除 skill 时，保留这份经验库；不要把项目报告或经验条目放进 skill 文件夹。

## 各应用共用什么

复盘、经验条目、索引和模板使用普通 Markdown。宿主应用负责文件访问、模型调用和技能发现；项目采用 AGENTS.md、CLAUDE.md 或 GEMINI.md 时，沿用现有规则文件。

`agents/openai.yaml` 只提供 Codex 界面设置。随附的 Python 工具只定位可访问的 Codex 本地历史，Python 3.9+、无第三方依赖。其他应用继续使用自身可访问的文件、版本记录和历史来源；读取聊天仍需实际访问权限。

安装命令与路径于 2026-10-31 对照上述官方文档核对。实际安装检查记录见[验证结果](../validation/TEST-RESULTS.md)。
