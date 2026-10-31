# 七份公开复盘案例及本 skill 的取舍

查阅日期：2026-10-31。以下均已打开正文；前五份是产品或技术项目回顾，后两份是事故复盘。只借鉴组织方式，不用其他公司的结论证明用户项目中的事实。

| 案例 | 类型 | 可借鉴的写法 | 本 skill 的采用方式 |
| --- | --- | --- | --- |
| [Mozilla Persona AAR](https://wiki.mozilla.org/Identity/Persona_AAR) | 产品采用受阻后的复盘 | 分开讨论做对了什么、为何采用不足、学到了什么；功能有效与产品采用可以有不同结论 | 同时保留成功做法和失败经验，区分真实痛点、实现效果及继续投入的价值 |
| [Dropbox 重写同步引擎](https://dropbox.tech/infrastructure/rewriting-the-heart-of-our-sync-engine) | 长期技术重写回顾 | 解释原系统约束、已尝试的渐进改进，以及重写的条件和代价 | 时间线记录当时依据；经验包含适用条件，避免把一次成功写成普遍应当重写 |
| [Discord 从 Go 迁移到 Rust](https://discord.com/blog/why-discord-is-switching-from-go-to-rust) | 单个服务迁移回顾 | 从用户体验要求出发，追踪问题、调参尝试、取舍和结果 | 不跳过无效尝试；把问题、措施和结果连起来，引用实测范围，不照搬技术选型 |
| [Discord 消息存储迁移](https://discord.com/blog/how-discord-stores-trillions-of-messages) | 大规模数据迁移回顾 | 交代历史方案、运维负担、迁移过程、数据校验和后续观察 | 保留关键转折与前后结果，区分完成迁移和长期运行验证 |
| [GitHub 工程团队迁移 Codespaces](https://github.blog/engineering/infrastructure/githubs-engineering-team-moved-codespaces/) | 开发工作流改造回顾 | 把旧痛点、分阶段改进、等待时间变化和开发者反馈放在同一条叙事里 | 报告兼顾工程效果和开发者实际操作成本；没有实测数字时不编造收益 |
| [GitLab 2017 年数据库事故复盘](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/) | 数据库事故 | 先还原时间线，再追查多个问题的原因及恢复措施，提出防止复发的工作 | 时间线与分析分开；经验有具体行动，避免只写“要更小心” |
| [Cloudflare 2019 年 7 月故障复盘](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/) | 规则发布事故 | 追查测试、保护机制、发布、回滚等多个促成条件，并区分措施的完成状态 | 不把问题只归咎于某个人或单个模型；建议明确已执行、待执行及验证状态 |

## 综合后的报告结构

采用“关键开发历史 → 经验总结 → 可复用模块与其他资产 → AGENTS.md 规则建议 → 留存动作与证据范围”。这是按本项目目标作出的设计，不是任何一份案例的原始模板。

一般复盘重在改善下一次工作；本 skill 额外要求资产能定位、依赖能辨认、经验能变为 agent 的行动规则。公开案例没有替我们证明模块可复用，这部分仍须检查用户项目的实现、调用和验证记录。

## 不照搬的部分

- 不把全部项目复盘写成事故报告；成功和主动停止同样可以产生有用经验。
- 不默认填写大型团队的责任人、会议流程、SLA 和生产事故字段，只有项目实际需要时才出现。
- 不将推广文章中的收益、规模或技术偏好代入用户项目，也不为报告漂亮补造工时、成本或成功率。
- 不把“回收资产”变成重新立项；维护和迁移成本高于预期复用价值的内容可以舍弃。
