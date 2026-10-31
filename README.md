# Project Alchemy · 项目炼金

**项目知识资产沉淀 skill。** 把开发过程中的经验、判断和现成模块，沉淀成下次可查、可用、可继续更新的知识资产。

给出项目路径后，读取相关文件和仍可访问的开发历史，整理关键节点、有效做法、失败原因及可复用模块。重要经验可以保存为独立 Markdown 条目，下个项目继续查阅和更新。

## 如何调用

**手动调用：** 输入 `$project-salvage`，再说明项目路径或要整理的经验。显示名称为“项目知识资产沉淀”，安装目录和调用标识保留 `project-salvage`。

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

将 `project-salvage/` 整个文件夹放入所用 agent 的技能目录。技能入口是 `project-salvage/SKILL.md`；也可以直接让 agent 读取这个文件并按它执行。

报告整理和经验更新由 agent 执行；随附的历史定位工具使用 Python 3.9+ 和标准库，无第三方依赖。它从普通 JSONL 首行及本地 `threads` 索引查找相关记录，可定位索引中的压缩文件，不会恢复聊天或执行历史命令。

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
- `validation/`：合成场景与自动检查。
- `ENGINEERING.md`：模块职责和工程约定。

本地生成的报告、经验库和测试运行结果默认被 Git 忽略。发布时使用整理好的公开文件；不要上传自己的聊天数据库、客户文件或密钥。
