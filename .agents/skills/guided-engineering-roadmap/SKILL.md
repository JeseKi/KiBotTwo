---
name: guided-engineering-roadmap
description: Use when the user wants a guided engineering tutorial or roadmap instead of immediate unstructured code generation. Trigger for staged roadmap chapters, baseline investigation, implementation walkthroughs, references, layered checklists, evidence-backed part planning, probe branches, and post-documentation redo validation where an independent pass checks whether the roadmap can be followed to reach the expected result.
---

# Guided Engineering Roadmap

## 用途

当用户想推进一个复杂工程目标，但不希望 Agent 过早直接实现代码时，使用这个 skill。

目标不是生成普通计划，而是生成一套可以顺着读、顺着做、能验收、能追溯可靠性的工程引导材料。

## 核心产物

默认把教程产物分成四类：

- `roadmap/`：主阅读路径，用户应该按顺序阅读并执行这里的章节。
- `reference/`：实现时查阅的项目事实、接口、数据流、文件计划和领域说明。
- `checklist/`：完成某个 part 后的验收条件，按 `low`、`medium`、`high` 分层。
- `evidence/`：证明 roadmap 不是拍脑袋写的证据，例如探针分支、diff 摘要、验证命令和决策记录。

详细目录、写作和文件职责见：`references/artifacts-and-writing.md`。

## 默认工作流

1. 如果最终目标不清楚，先简短澄清。
2. 判断用户要的是顶层 tutorial、某个 part 的 roadmap、reference、checklist、evidence，还是基线调查。
3. 优先创建或更新顶层 `index.md`，说明 part 顺序、依赖和当前推进位置。
4. 只展开当前 part；除非用户明确要求，不要一次性补齐所有未来 part 的细节。
5. 当前 part 默认使用 `roadmap/`、`reference/`、`checklist/`、`evidence/`；如果某类暂时没有价值，可以不创建。
6. 如果当前 part 是基线调查，Agent 应该读取项目并写出事实材料，而不是把调查工作丢给用户。
7. 如果当前 part 是实现引导，Agent 应该把实施步骤写进 `roadmap/`，把查阅性材料放进 `reference/`，把完成标准放进 `checklist/`。
8. 如果是在写顶层全局规划，只做路线分解，不默认创建探针分支。
9. 编写具体 part 时默认启用探针分支模式并产出 `evidence/`；跳过条件见 `references/validation-workflows.md`。
10. 当前 part 的文档完成后，按 `references/validation-workflows.md` 执行文档复测闭环：必须由 sub agent 独立复测，且有参考实现时必须通过非 `docs/` patch 字节级一致审计。
11. 根据复测反馈修正文档和 evidence；失败、阻塞和修正结果不能只留在聊天里。
12. 每个 part 结束时，记录它解锁了哪些后续 part。

探针分支和文档复测闭环的详细规则见：`references/validation-workflows.md`。

## 何时读取 Reference

- 写目录结构、顶层 `index.md`、roadmap 章节、reference/checklist/evidence 文件时，读取 `references/artifacts-and-writing.md`。
- 需要做探针分支、真实验证、sub agent 复测、临时分支/worktree 清理时，读取 `references/validation-workflows.md`。
- 需要判断当前 part 属于基线调查、架构设计、实现引导、代码审阅或集成推进时，读取 `references/phase-types-and-constraints.md`。

只读取当前任务需要的 reference，不要一次性把所有 reference 都加载进上下文。

## 行为底线

- 不要过度展开未来 part。
- 不要制造虚假的确定性。
- 把未知事项标记为“需要运行时确认”。
- 不要把 roadmap 写成只包含标题的空路线。
- 不要把 reference 写成主线教程。
- 不要用“完整最终代码清单”、复制 `.bak`、套用 reference patch 或功能等价说明绕过 roadmap 复测。
- 不要把 checklist 写成泛泛愿望；尽量写成可观察结果。
- 不要因为某类目录暂时为空，就强行创建文件。
- 不要因为文档模板没有全部填满，就否定已经通过核心验收的 part。
- 编写具体 part 时，探针分支可以修改功能代码来验证路线；正式分支只保留文档和用户明确要求保留的代码改动。

更多阶段类型和行为约束见：`references/phase-types-and-constraints.md`。
