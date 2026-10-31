# 工程基线

本项目交付 `project-salvage` skill。`SKILL.md` 负责完整复盘、轻量经验更新和查用；经验库协议定义独立条目、稳定编号、索引、证据与合并规则。资料使用普通 Markdown，由 agent 做语义判断，不增加知识管理服务。

`scripts/find_project_history.py` 只负责从 JSONL 首行与本地 SQLite `threads` 元数据定位记录，Python 标准库，无外部依赖；支持实际索引指向的压缩记录及 Windows 扩展路径，不读取聊天正文。`validation/prepare_scenario.py` 只复制合成场景到新目录并绑定测试路径，不覆盖已有目录。

输入为存在的项目目录与可选历史存储目录、已核实的关联绝对路径；关联路径可以是迁移后已不存在的旧目录。输出为 stdout JSON 清单，不写文件，不恢复聊天，不读取消息正文，不负责判断项目经验。工作树归属由调用者核实后传入，不靠同名或前缀猜测。

未知格式、读取失败、扫描预算与结果截断需要显式报告。零匹配只代表已检查范围内未匹配，不代表历史不存在。SQLite 使用只读连接与查询限制，不改变数据库或 WAL；正文由 agent 按实际可用的只读来源定向读取。

经验库与安装目录分开；同一来源无新增信息时不改文件与更新时间，新证据更新原条目并保存改变原因。库内链接相对化，必要事实随库保存。全局规则、源代码和真实聊天的写入需要各自任务授权，不由经验保存隐含扩大。

同一份标准 skill 用于多个宿主，Codex UI 元数据与本地历史定位器是可选扩展。安装复用 skills CLI，手动复制与 Claude ZIP 上传见 `docs/installation.md`；测试只安装到隔离项目，不改变用户实际技能目录。独立 ZIP 只含 skill 目录，个人知识库和报告不进入安装包。

自动检查：`python -B -X utf8 -m unittest discover -s validation -p test_*.py`。隔离测试数据在临时目录生成；`validation/fixtures` 是独立情境试用的虚构材料。真实历史只在验证本项目读取入口时查元数据，不混入发布产物。

发布文件采用明确清单：README、工程基线、skill 和公开验证资料。`reports/`、`knowledge/`、`validation/runs/`、`validation/results.md` 与内部计划被忽略；发布目录还要单独检查，不只依赖忽略规则。
