# Project Alchemy · 项目资产抢救企划

从项目文件和开发历史中，找回可复用的经验、模块与知识资产。

给出项目路径后，这个 skill 会读取相关文件和仍可访问的开发历史，整理关键节点、有效做法、失败原因及可复用模块，交付一份 Markdown 文档，再建议哪些内容适合沉淀到现有知识库、项目文档或指令。项目成功、失败或搁置，都能按实际材料整理。

## 快速安装

支持 Codex、Claude Code、Cursor、Gemini CLI、OpenCode 等使用 Agent Skills 的应用。使用 [skills 安装器](https://github.com/vercel-labs/skills)选择要安装的应用，需要 Node.js 22.20+：

```sh
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -g
```

也可以直接指定应用，下面两条选一条：

```sh
# Codex
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a codex -g --copy -y
# Claude Code
npx --yes skills add Usernamethatavailable/project-alchemy --skill project-salvage -a claude-code -g --copy -y
```

不使用 Node.js 时，下载[独立 skill ZIP](https://github.com/Usernamethatavailable/project-alchemy/releases/latest/download/project-salvage.zip)，按应用复制目录；Claude 网页版可直接上传这个 ZIP。各应用命令、目录、调用方式和更新步骤见[安装指南](docs/installation.md)。

## 如何调用

**手动调用：** Codex 输入 `$project-salvage`；Claude Code、Cursor 输入 `/project-salvage`；其他应用可直接说“使用 project-salvage”。再说明项目路径或要整理的经验。安装目录和技能标识保留 `project-salvage`。

**自动选用：** skill 安装并被 agent 发现后，用户表达“复盘项目”“沉淀经验”“留存知识资产”“找可复用模块”“别再踩这个坑”“以前怎么解决”“提炼用户偏好”“建议修改全局指令”等意图时，agent 可以自行选用，无需记住技能名称。按实际意图判断，普通开发、保存文件或开发“复盘功能”不触发。

这里的自动是对当前请求选用 skill，不是后台定时运行；只要求分析时交付文档与建议。

## 两种文档

**完整复盘**：用一份 Markdown 写清开发历史、经验总结、现成能力、规则建议和留存安排。正文使用通俗语言，代码位置与依赖放附录。

**单次经验整理**：解决一个难题或推翻旧判断后，只生成或更新该主题的一份 Markdown 文档。

可以这样说：

```text
复盘这个项目：/path/to/project。先只读分析，给我一份完整报告。

把这次排查整理成一份 Markdown，给出适合放到知识库或项目文档的具体建议。

这个新案例推翻了旧做法。更新原文档，保留改变判断的原因。

把报告中的处理办法合并到我指定的现有笔记，保留原笔记其他内容。

从这段开发历史提炼我的稳定偏好，先给全局指令修改方案，等我批准后再改。
```

## 从用户偏好改进全局指令

skill 会从用户反复纠正的行为和明确的长期要求中提出建议，先对照当前全局指令，给出来源、目标位置、修改前后文案和影响。一次性的项目要求留在项目范围，已有规则覆盖的内容不重复添加。

你可以批准全部、只批准某几条、调整文案或拒绝。批准后只修改选中的条目；如果等待期间相关原文发生冲突，会先修订那一条方案。流程与[提案模板](project-salvage/assets/global-instruction-proposal.md)随 skill 提供，详见[全局偏好说明](project-salvage/references/global-preferences.md)。

## 安装与试用

核心是标准的 `SKILL.md` 与相对路径资源，同一份 skill 用于各应用。`agents/openai.yaml` 提供 Codex 的显示和调用设置，其他应用通过 `SKILL.md` 发现技能。

报告整理和经验更新由 agent 执行。随附的历史定位工具是可选的 Codex 本地历史入口，使用 Python 3.9+ 标准库；它从普通 JSONL 首行及本地 `threads` 索引查找记录，可定位压缩文件，不会恢复聊天或执行历史命令。其他应用使用自己可访问的项目文件、版本历史、对话工具或用户提供的材料。

```sh
python project-salvage/scripts/find_project_history.py /path/to/project
python project-salvage/scripts/find_project_history.py /path/to/project --codex-home /path/to/codex-data
```

目录迁移或 worktree 关系已经确认时，使用 `--related-root` 指定关联旧路径。具体读取方式见 [历史定位说明](project-salvage/references/local-history.md)。

## 文档交付后，怎么沉淀

文档给出具体建议：哪些方法适合放进已有知识库，哪些操作说明应合并到项目 README，哪些用户偏好值得形成全局指令提案。你可以自行采纳，也可以指定目标，让 agent 帮忙合并。

默认交付一份文档，不另建经验库、索引或条目体系。新证据更新相关既有文档，保留改变判断的原因；获准合并时沿用目标结构，已有内容不重复写。具体流程见[文档与沉淀说明](project-salvage/references/knowledge-handoff.md)。

知识库、项目文档、项目规则按各自授权处理；全局指令在具体方案获批后写入。报告、笔记和用户资料独立于 skill 安装目录保存。

## 运行检查

在仓库根目录运行：

```sh
python -B -X utf8 -m unittest discover -s validation -p "test_*.py"
```

自动检查使用临时合成数据，不读取真实用户历史。另有面向 agent 的实际试用场景，见 [验证说明](validation/README.md)和[本次验证结果](validation/TEST-RESULTS.md)。

## 仓库内容

- `project-salvage/`：可安装的 skill、说明、经验模板及只读定位工具。
- `docs/installation.md`：多应用安装、调用与更新指南。
- `validation/`：合成场景与自动检查。
- `ENGINEERING.md`：模块职责和工程约定。

本地生成的私人报告、知识资料和测试运行结果不进入公开发布包。发布时使用整理好的公开文件；不要上传自己的聊天数据库、客户文件或密钥。
