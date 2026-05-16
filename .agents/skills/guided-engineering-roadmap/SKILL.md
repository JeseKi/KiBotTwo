---
name: guided-engineering-roadmap
description: Use when the user wants a guided engineering tutorial or roadmap instead of immediate unstructured code generation. Trigger for staged roadmap chapters, baseline investigation, implementation walkthroughs, references, layered checklists, and evidence-backed part planning where concrete parts normally use proof/probe branches so the user can understand and progress part by part.
---

# Guided Engineering Roadmap

## 用途

当用户想推进一个复杂工程目标，但不希望 Agent 过早直接实现代码时，使用这个 skill。

这个 skill 的目标不是生成一份普通计划，而是生成一套可以顺着读、顺着做、能验收、能追溯可靠性的工程引导材料。

它是一套协作协议，不是某个技术栈的教程。

## 核心模型

把产物分成四类。每类只承担一种职责：

- `roadmap/`：主阅读路径。用户应该按顺序阅读并执行这里的章节。
- `reference/`：实现时查阅的项目事实、接口、数据流、文件计划和领域说明。
- `checklist/`：完成某个 part 后的验收条件，按 `low`、`medium`、`high` 分层。
- `evidence/`：证明 roadmap 不是拍脑袋写的证据，例如探针分支、diff 摘要、验证命令和决策记录。

`roadmap/` 可以包含具体实施步骤。不要再把“路线图”和“实现步骤”拆成两个互相竞争的入口。

## 写作感觉

`roadmap/` 应该参考 Eric Matthes 的工程教学节奏：小步推进、上下文清楚、例子贴近当前任务、每节都有可见结果和简短收束。借鉴的是这种组织感和读者体验，不是模仿具体措辞。

章节读起来应该像一本舒服的工程入门书：有顺序、有上下文、有小结，读者知道现在为什么做这一步、做完能看到什么、下一步去哪里。

但它不应该写成完整教材、百科、API 手册或长篇背景课。

每个 roadmap 章节围绕一个明确工程动作：

```text
确认现有入口
建立数据模型
接入迁移
暴露创建接口
补齐失败路径
整理本部分总结
```

好的章节应该包含：

- 本节目标。
- 为什么现在做。
- 需要参考哪些 `reference/` 文件。
- 具体实施步骤。
- 完成后应该观察到什么。
- 本节小结。
- 下一节入口。

避免：

- 大段通用概念教学。
- 与当前项目无关的学习建议。
- 未来阶段的完整实现细节。
- 把每个代码 diff 逐行翻译成任务。
- 创建大量用户不会读的模板文件。

## 默认工作流

1. 如果最终目标不清楚，先简短澄清。
2. 判断用户要的是顶层 tutorial、某个 part 的 roadmap、reference、checklist、evidence，还是基线调查。
3. 优先创建或更新顶层 `index.md`，说明 part 顺序、依赖和当前推进位置。
4. 只展开当前 part；除非用户明确要求，不要一次性补齐所有未来 part 的细节。
5. 当前 part 默认使用四类目录：`roadmap/`、`reference/`、`checklist/`、`evidence/`。如果某类暂时没有价值，可以不创建。
6. 如果当前 part 是基线调查，Agent 应该读取项目并写出事实材料，而不是把调查工作丢给用户。
7. 如果当前 part 是实现引导，Agent 应该把实施步骤写进 `roadmap/`，把查阅性材料放进 `reference/`，把完成标准放进 `checklist/`。
8. 如果是在写顶层全局规划，只做路线分解，不默认创建探针分支。
9. 如果是在编写某个具体 part，默认启用探针分支模式并产出 `evidence/`；除非用户显式要求“不做探针”“只写静态规划”或当前环境无法安全创建分支。
10. 每个 part 结束时，记录它解锁了哪些后续 part。

## 推荐目录结构

除非用户指定其他位置，否则优先使用项目内文档目录。中文用户优先使用中文标题和中文正文；文件夹名可以保留稳定英文类别名，便于机器和人同时识别。

示例：

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

如果项目或用户明显偏好英文，可以改用英文 part 名和文件名。

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

这些系统契约必须出现在当前 part 的 `roadmap/index.md` 主线入口中，不能只写在 `reference/`、`checklist/` 或 `evidence/`。其他目录可以展开细节或记录证据，但不能替代 `roadmap/index.md` 对用户说明“系统完成后是什么状态、边界在哪里”。

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

示例风格：

````markdown
我们先写最小配置，让节点知道自己的更新频率：

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0
```

这里先不配置 planner 或 costmap，只确认 controller server 有自己的参数入口。

接下来加入 progress checker：

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0
    progress_checker_plugins: ["progress_checker"]
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
```

新增的 `progress_checker_plugins` 告诉 Nav2 加载哪个进展检查器；`required_movement_radius` 和 `movement_time_allowance` 定义“多久没有移动多少距离就算失败”。
````

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

每条验收条件应该尽量可观察、可测试、可复现。

示例：

```text
low:
- 可以创建用户。
- 可以使用密码登录。

medium:
- 支持用户创建、查询、修改、删除。
- 支持密码登录和验证码登录。
- 主要失败路径返回稳定错误结构。

high:
- 创建用户时必须校验用户名、密码和邮箱。
- 验证码登录不泄露邮箱是否存在。
- 验证码发送有频率限制。
- 关键路径有测试或可复现的手动验证步骤。
```

如果某个 part 很小，可以只创建 `low.md`，或在一个 checklist 文件中保留三层标题。不要为了形式制造空文件。

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

`evidence/` 不应该成为主阅读路径。用户可以不读 evidence，也能按 roadmap 推进；但当用户怀疑可靠性时，evidence 应该能说明依据。

当当前 part 涉及可运行系统、命令行工具、服务、API、仿真、前端页面或任何需要用户手动确认的行为时，默认创建或更新 `evidence/usage.md`。这个文件应该包含：

- 环境准备和依赖检查。
- 启动命令。
- 基础健康检查。
- 最小成功用例。
- 结果判定标准。
- 常见失败结果和下一步排查入口。
- 收尾或清理步骤。

`usage.md` 写具体操作，不替代 `roadmap/index.md` 的系统预期状态、完成边界和失败判读；`roadmap/index.md` 负责定义契约，`usage.md` 负责让用户复现验证。

## 探针分支模式

编写具体 part 时，默认使用探针分支模式。工程式学习应该让 roadmap 来自一次真实尝试，而不是只来自静态推测。

只有这些情况可以跳过探针：

- 用户显式要求不做探针或只写静态规划。
- 当前任务只是顶层全局规划，还没有进入具体 part。
- 当前环境不是 git 仓库，或工作区状态无法安全创建分支。
- 目标 part 完全不涉及代码、配置、运行行为或可验证系统响应。

目的：先在临时分支把当前 part 做到行为符合预期，再从真实 diff 和验证结果中提炼 roadmap。

推荐流程：

1. 记录当前分支和工作区状态。
2. 创建探针分支，例如 `roadmap-probe/01-user-system`。
3. 在探针分支实现当前 part 的最小可验证版本。
4. 运行必要测试、构建或手动验证。
5. 提交探针 commit，例如 `probe: validate part 01 user system roadmap`。
6. 用 `git diff`、提交记录和验证结果写入 `evidence/`。
7. 从真实编辑顺序中提炼 `roadmap/` 章节。
8. 切回原分支，保留文档改动；不要把探针功能代码混入原分支，除非用户明确要求。

探针分支模式的输出重点：

- roadmap 是面向用户的执行顺序，不是 diff 复述。
- checklist 来自实际验证目标，不是事后想象。
- reference 只保留后续实现需要查的事实。
- evidence 记录足够信息，让用户知道这条路线已经被试过。

如果探针被跳过，必须在 `evidence/` 或当前回复中明确说明原因，并把 roadmap 标记为“未经过探针验证”。

## 阶段类型规则

### 基线调查

当 part 目标是理解当前系统时，Agent 应该检查项目并输出调查结论。

应该做：

- 只读取理解当前结构和数据流所需的文件。
- 识别 package、模块、启动入口、服务、topic、API、schema 或运行边界。
- 追踪当前系统中将被替换、扩展或复用的行为链路。
- 区分源码已确认的事实和需要运行时确认的事项。
- 把调查结果主要写入 `reference/`。
- 在 `roadmap/` 中写出用户应该如何理解这些事实，以及它们如何解锁下一 part。

不应该做：

- 不要把基线调查写成用户作业。
- 不要修改功能代码。
- 不要把未知运行时行为写成已经确认。

基线调查应该回答：

```text
当前系统已经有什么？
当前系统如何工作？
当前能力边界在哪里？
哪些内容应该复用、替换或隔离？
下一 part 需要从这里得到什么？
```

### 架构设计

当 part 目标是设计目标结构时，Agent 应该提供：

- 模块或节点边界。
- 接口契约。
- 数据流。
- 状态归属。
- 失败模式。
- 迁移策略。
- 分层验收条件。

架构决策放入 `reference/`，推进顺序和落地步骤放入 `roadmap/`。

### 实现引导

当用户准备自己实现某个边界清晰的功能时，Agent 应该提供：

- `roadmap/` 中的顺序实施章节。
- `reference/` 中的文件计划、接口契约和必要项目事实。
- `checklist/` 中的 low / medium / high 验收条件。
- 必要调试检查点。

除非用户明确说“帮我实现”或类似表达，否则不要在正式交付分支写完整功能代码。探针分支中的最小实现用于验证 roadmap，完成后应提炼为文档和 evidence，而不是默认作为正式代码交付。

实现引导应该避免过度设计。如果目标可以通过一个配置文件、一个 launch、一个迁移或一个小改动完成，就不要先创建完整架构文档或长篇 checklist。

### 代码审阅

当用户已经写了代码，希望获得反馈时，Agent 应该像工程师一样 review：

- 先列发现的问题，按严重程度排序。
- 尽量包含文件和行号引用。
- 重点关注 bug、行为回归、集成风险、缺失测试和接口不清晰。
- 给出具体修改建议，但不要默认重写整套方案。
- 必要时更新对应 checklist 或 evidence，说明当前实现还差什么。

### 集成推进

当多个 part 需要串成端到端流程时，Agent 应该提供：

- 启动或运行顺序。
- 集成假设。
- 调试检查点。
- 可观测性点位。
- 已知失败模式。
- 演示验收条件。

集成材料可以写入 `roadmap/` 的集成章节，也可以按需写入 `reference/` 和 `checklist/`。

## 语言规则

匹配用户的主要语言。

如果用户主要用中文交流，则标题和说明都应该用中文。

技术标识符保持原样，例如：

```text
ROS2, Nav2, TF, topic, action, service, API, package, launch, base_link, cmd_vel
```

优先使用：

```text
阶段 00：系统基线
本节目标
完成条件
依赖 part
后续 part
```

而不是：

```text
Stage 00: System Baseline
Expected Outputs
Exit Criteria
Depends On
Next Stage
```

## 行为约束

- 不要过度展开未来 part。
- 不要制造虚假的确定性。
- 把未知事项标记为“需要运行时确认”。
- 不要把 roadmap 写成只包含标题的空路线。
- 不要把 reference 写成主线教程。
- 不要把 checklist 写成泛泛愿望；尽量写成可观察结果。
- 不要因为某类目录暂时为空，就强行创建文件。
- 不要因为文档模板没有全部填满，就否定已经通过核心验收的 part。
- 编写具体 part 时，探针分支可以修改功能代码来验证路线；正式分支只保留文档和用户明确要求保留的代码改动。
