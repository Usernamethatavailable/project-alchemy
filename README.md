# Project Alchemy · 项目资产抢救企划

从项目文件和开发历史中，找回可复用的经验、模块与知识资产。

给出项目路径后，这个 skill 会读取相关文件和仍可访问的开发历史，整理关键节点、有效做法、失败原因及可复用模块，生成完整复盘。重要经验保存为独立 Markdown 条目，下个项目继续查阅和更新；项目成功、失败或搁置，都能按实际材料整理。

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

**自动选用：** skill 安装并被 agent 发现后，用户表达“复盘项目”“沉淀经验”“留存知识资产”“找可复用模块”“别再踩这个坑”“以前怎么解决”等意图时，agent 可以自行选用，无需记住技能名称。按实际意图判断，普通开发、保存文件或开发“复盘功能”不触发。

这里的自动是对当前请求选用 skill，不是后台定时运行；只要求分析时不会自动写入经验库。

## 两种用法

**完整复盘**：输出开发历史、经验总结、现成能力、规则建议和留存安排。正文使用通俗语言，代码位置与依赖放附录。

**轻量经验更新**：解决一个难题或推翻一个旧判断后，查找已有条目并更新，只处理这次经验，不重新写长报告。

可以这样说：

```text
复盘这个项目：/path/to/project。先只读分析，给我一份完整报告。

把这次排查沉淀到 /path/to/knowledge，先找已有经验，避免重复创建。

这个新案例推翻了旧做法。更新原经验，保留改变判断的原因。

从经验库里找找，以前遇到“文件能打开但导出错位”时怎么处理。
```

## 安装与试用

核心是标准的 `SKILL.md` 与相对路径资源，同一份 skill 用于各应用。`agents/openai.yaml` 提供 Codex 的显示和调用设置，其他应用通过 `SKILL.md` 发现技能。

报告整理和经验更新由 agent 执行。随附的历史定位工具是可选的 Codex 本地历史入口，使用 Python 3.9+ 标准库；它从普通 JSONL 首行及本地 `threads` 索引查找记录，可定位压缩文件，不会恢复聊天或执行历史命令。其他应用使用自己可访问的项目文件、版本历史、对话工具或用户提供的材料。

```sh
python project-salvage/scripts/find_project_history.py /path/to/project
python project-salvage/scripts/find_project_history.py /path/to/project --codex-home /path/to/codex-data
```

目录迁移或 worktree 关系已经确认时，使用 `--related-root` 指定关联旧路径。具体读取方式见 [历史定位说明](project-salvage/references/local-history.md)。

## 经验保存方式

```text
knowledge/
  INDEX.md
  experiences/
    exp-visual-output-check.md
  evidence/
    exp-visual-output-check/
      case-a.md
```

经验库与安装的 skill 分开保存。每条经验有稳定编号，索引说明什么时候查；相同问题更新原条目，新证据修正当前做法，判断变化和真实使用结果留在同一条目中。必要事实保存在条目或证据摘录里，库内链接采用相对路径，便于搬到别的目录或用 Obsidian 打开。

用户只要求分析时交付建议；授权保存经验后直接维护指定经验库。报告不会自动修改全局指令、安装新 skill 或抽取源项目代码。

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

本地生成的报告、经验库和测试运行结果默认被 Git 忽略。发布时使用整理好的公开文件；不要上传自己的聊天数据库、客户文件或密钥。
