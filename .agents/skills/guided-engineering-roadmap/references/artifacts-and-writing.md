# 产物与写作规则

## 写作感觉

`roadmap/` 应该参考 Eric Matthes 的工程教学节奏：小步推进、上下文清楚、例子贴近当前任务、每节都有可见结果和简短收束。借鉴的是这种组织感和读者体验，不是模仿具体措辞。

章节读起来应该像一本舒服的工程入门书：有顺序、有上下文、有小结，读者知道现在为什么做这一步、做完能看到什么、下一步去哪里。

避免：

- 大段通用概念教学。
- 与当前项目无关的学习建议。
- 未来阶段的完整实现细节。
- 把每个代码 diff 逐行翻译成任务。
- 创建大量用户不会读的模板文件。

## 推荐目录结构

除非用户指定其他位置，否则优先使用项目内文档目录。中文用户优先使用中文标题和中文正文；文件夹名可以保留稳定英文类别名，便于机器和人同时识别。

```text
docs/<目标>-tutorial/
  index.md
  00-系统基线/
    roadmap/
      index.md
      01-确认项目入口.md
      02-追踪核心链路.md
      03-本部分总结.md
    reference/
      system-inventory.md
      request-flow.md
      risk-register.md
    checklist/
      low.md
      medium.md
      high.md
    evidence/
      baseline-notes.md

  01-用户系统/
    roadmap/
      index.md
      01-建立用户模型.md
      02-实现用户创建.md
      03-实现登录入口.md
      04-本部分总结.md
    reference/
      api-contract.md
      database-schema.md
      file-plan.md
    checklist/
      low.md
      medium.md
      high.md
    evidence/
      probe-branch.md
      diff-summary.md
      validation-log.md
```

## 顶层 index.md

顶层 `index.md` 是整套 tutorial 的目录和总路线图，不是项目 README。

应该包含：

- 目标结果。
- 当前 part。
- 推荐阅读顺序。
- part 状态表。
- part 依赖图，优先用 Mermaid。
- 每个 part 的目的、依赖、产出、完成条件和解锁内容。
- 状态值和更新规则。

状态值建议：

```text
未开始
进行中
已完成
需要返工
阻塞
```

避免：

- 把顶层 `index.md` 写成项目介绍页。
- 在顶层提前展开所有 part 的具体实现。
- 把未来 part 写得像已经验证过。

## roadmap/ 规则

`roadmap/` 是主线章节。用户从 `roadmap/index.md` 开始，然后按编号阅读。

`roadmap/index.md` 应该包含：

- 当前 part 的目标。
- 本 part 的章节目录。
- 本 part 的 Mermaid 流程或依赖图。
- 本 part 需要先读的最少 reference。
- 本 part 完成后应该跑哪些 checklist。
- 系统预期状态：本 part 完成后系统应该处在什么可观察状态。
- 完成边界：本 part 已经承诺解决什么。
- 不承诺内容：本 part 明确不保证什么，哪些内容属于后续 part。
- 失败判读：常见失败结果应该如何解释，哪些失败不能被包装成完成。
- 下一阶段依赖契约：后续 part 可以依赖本 part 的哪些接口、行为或验证结论。

这些系统契约必须出现在当前 part 的 `roadmap/index.md` 主线入口中，不能只写在 `reference/`、`checklist/` 或 `evidence/`。

每个章节文件应该回答：

```text
这一节做什么？
为什么现在做？
需要参考什么？
具体怎么做？
做完应该看到什么？
这节完成后，下一节是什么？
```

如果章节涉及代码、配置、launch、API schema、命令行脚本或任何具体文件改动，必须采用增量式教学写法：

- 先给出最小可理解片段，再逐步加入下一段代码或配置。
- 每次新增片段后解释新增行承担的职责。
- 不要一开始贴完整文件，也不要只列“新增某文件、修改某参数”。
- 文件路径可以说明落点，但章节主线应围绕工程概念和行为闭环，而不是围绕 diff 顺序。
- 完整文件只能放在章节末尾作为汇总，或放入 `reference/` / `evidence/`，不能替代逐步讲解。
- 每个代码片段都应说明放到哪个文件、放在什么上下文附近，以及执行到这一步后可以观察到什么。

章节粒度规则：

- 一个章节只推进一个主要工程动作。
- 一个章节应该能在一次专注实现中完成。
- 如果步骤跨多个模块、多个行为边界或多个验收目标，拆成多个章节。
- 如果步骤只是一个小配置或一处小改动，不要强行扩写成长章节。

## reference/ 规则

`reference/` 是查阅材料，不是主线阅读材料。

适合放入：

- 当前系统事实。
- 文件计划。
- 接口契约。
- 数据流。
- schema 或配置说明。
- 运行边界。
- 风险登记。
- 领域专用链路，例如 `auth-flow.md`、`request-lifecycle.md`、`tf-flow.md`。

要求：

- 区分“源码已确认”和“需要运行时确认”。
- 优先记录项目事实，不写泛泛教程。
- roadmap 章节需要用到 reference 时，明确引用文件名。
- 不要把 implementation steps 主要写在 reference 里；它们应该留在 `roadmap/`。

## checklist/ 规则

`checklist/` 用来判断这个 part 是否完成。默认分三层：

- `low.md`：最低可用验收。证明核心能力存在。
- `medium.md`：功能完整验收。证明主要场景可用。
- `high.md`：产品级、集成级或边界条件验收。证明异常、安全性、一致性和可观测性达到预期。

每条验收条件应该尽量可观察、可测试、可复现。如果某个 part 很小，可以只创建 `low.md`，或在一个 checklist 文件中保留三层标题。不要为了形式制造空文件。

## evidence/ 规则

`evidence/` 用来解释 roadmap 为什么可信。

适合放入：

- 探针分支名。
- 探针 commit。
- 关键 diff 摘要。
- 实际修改文件。
- 实际验证命令和结果。
- `usage.md`：从启动到验证的可复现操作步骤，说明用户如何确认系统响应符合预期。
- 被证明必要的实现顺序。
- 探针中尝试过但不应进入正式 roadmap 的路径。
- 未验证事项和风险。

当当前 part 涉及可运行系统、命令行工具、服务、API、仿真、前端页面或任何需要用户手动确认的行为时，默认创建或更新 `evidence/usage.md`。这个文件应该包含：

- 环境准备和依赖检查。
- 启动命令。
- 基础健康检查。
- 最小成功用例。
- 结果判定标准。
- 常见失败结果和下一步排查入口。
- 收尾或清理步骤。

`usage.md` 写具体操作，不替代 `roadmap/index.md` 的系统预期状态、完成边界和失败判读；`roadmap/index.md` 负责定义契约，`usage.md` 负责让用户复现验证。
