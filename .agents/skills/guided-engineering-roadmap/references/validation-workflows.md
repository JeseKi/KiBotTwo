# 验证工作流

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

输出重点：

- roadmap 是面向用户的执行顺序，不是 diff 复述。
- checklist 来自实际验证目标，不是事后想象。
- reference 只保留后续实现需要查的事实。
- evidence 记录足够信息，让用户知道这条路线已经被试过。

如果探针被跳过，必须在 `evidence/` 或当前回复中明确说明原因，并把 roadmap 标记为“未经过探针验证”。

## 文档复测闭环

探针分支证明“这条实现路线能做出来”；文档复测闭环证明“读者只看 roadmap/evidence 能不能重新做出来”。两者职责不同。编写可运行系统、配置、launch、API、前端、仿真或任何可验证行为的具体 part 时，完成文档后必须执行复测闭环。

复测闭环的硬要求：

- 必须调用 sub agent。sub agent 是独立读者，不继承主 Agent 的探针实现上下文。
- sub agent 的实际任务只有一件事：按 `roadmap/` 步骤一步一步编写代码，运行文档承诺的验证命令，最后把非 `docs/` patch 与审计 oracle 做一致性比较并报告结果；主 Agent 只能复核，不能替代这一步。
- 如果当前工具、权限或策略无法启动 sub agent，复测不能判通过，只能记录为“复测阻塞”或“复测未通过”。
- 有成品分支、探针分支或参考实现分支时，复测分支的非 `docs/` patch 必须与同一 baseline 上的 `evidence/reference-runtime.patch` 或参考分支 patch 字节级一致；只允许忽略 CRLF/LF 换行符差异。
- `reference/final-runtime/*.bak` 和 `evidence/reference-runtime.patch` 是审计 oracle，不是实现来源。

复测闭环要验证：

- 验证 `roadmap/` 中的步骤是否足以让人手写代码。
- 验证 `evidence/usage.md` 的命令是否可复现。
- 发现文档遗漏、顺序错误、参数不完整、验收条件不清或清理步骤不足。
- 根据复测结果修正文档，而不是为了通过验证直接从功能分支同步代码。

如果当前 part 有成品分支、探针分支或参考实现分支，例如 `feat/<part>`，文档复测通过必须同时满足：

1. 运行时验收通过。
2. 文档包含 `reference/final-runtime/`，其中以 `.bak` 文件保存所有非 `docs/` diff 涉及文件的最终副本，目录结构保留项目相对路径。
3. 复测分支中除 `docs/` 外的完整 patch，与成品分支相对同一 baseline 的非 `docs/` patch 字节级一致；只允许忽略换行符格式差异。

不通过或阻塞判定：

- 不能启动 sub agent：阻塞或未通过。
- 运行时验收失败：未通过。
- 非 `docs/` patch 不一致：未通过，不能用“功能等价”“可解释差异”“文件名相同”或“测试都通过”替代。
- sub agent 复制 `.bak`、套用 reference patch、查看探针/成品分支源码来构造 runtime：未通过。
- sub agent 报告必须依赖 oracle 才能得到一致结果：未通过，说明 roadmap/reference 缺实现细节。
- 主 Agent 新增“完整最终代码清单”、把 `.bak` 转写成普通 reference、或把 reference patch 变成操作清单：未通过，必须撤回并改为补充增量步骤。
- 只有 `docs/` 下的差异可以不一致，因为复测后的文档可能已经被修正。

默认流程：

1. 在当前工作基础上创建临时复测分支或 worktree，例如 `test/<part>-roadmap-redo-check` 或 `tmp/<part>-roadmap-redo-check`。
2. 启动一个 sub agent 执行复测。不能启动 sub agent 时，停止复测通过判定，写入阻塞原因。
3. 给复测者的任务必须要求它只按 `roadmap/` 步骤一步一步编写代码，不读取目标功能分支的最终代码来补答案，不复制 `.bak`，不套用 reference patch。
4. 复测者可以在临时分支中实际编辑功能代码、配置和测试文件；这些代码只用于验证文档，不直接进入正式分支。
5. 复测者必须运行文档承诺的构建、测试、launch、CLI、手动验证或最小成功用例。
6. 复测者发现不一致时，记录复现命令、实际结果、文档缺口和可能解决方案。
7. 如果有成品分支或探针分支，主 Agent 必须先核对复测分支的非 `docs/` 文件与 `reference/final-runtime/` 下对应 `.bak` 文件完全一致。
8. 主 Agent 必须再对比“成品分支相对 baseline 的非 `docs/` patch”和“复测分支相对同一 baseline 的非 `docs/` patch”。两者必须字节级一致；只允许忽略换行符格式差异。
9. 未通过时，先修正文档，再从干净 baseline 重新复测；不要在复测分支里直接参考 oracle 后宣称通过。
10. 复测通过后，清理临时 launch、服务、仿真、dev server、后台进程、临时 worktree 和临时分支。
11. 正式分支只保留文档改动和用户明确要求保留的代码；复测分支中的功能代码不要混入正式交付，除非用户明确要求。

推荐的完全一致审计方式：

```bash
# 先逐文件核对最终 .bak 副本。runtime_paths 是本 part 的非 docs 文件清单。
for path in "${runtime_paths[@]}"; do
  diff -u \
    "docs/<目标>/<part>/reference/final-runtime/${path}.bak" \
    "${redo_worktree}/${path}"
done

# baseline 是成品分支和复测分支共同的起点。
# 生成 redo patch 前先对新增文件执行 git add -N，否则 untracked 文件不会出现在 git diff 中。
(cd "${redo_worktree}" && git add -N "${runtime_paths[@]}")
git diff --binary --no-ext-diff "${baseline}...${reference_branch}" -- . ':(exclude)docs/**' > /tmp/reference.diff
(cd "${redo_worktree}" && git diff --binary --no-ext-diff "${baseline}" -- . ':(exclude)docs/**') > /tmp/redo.diff
diff -u /tmp/reference.diff /tmp/redo.diff
```

`diff` 有任何输出都表示复测未通过。不要只比较文件名；必须比较完整 patch 内容。这里的“一致”是字节级 patch 一致，不是语义一致。唯一可忽略的是换行符格式差异；如果需要忽略 CRLF/LF，必须先用明确的换行规范化步骤生成审计副本，再比较规范化后的完整 patch。

给 sub agent 的复测 prompt 应该尽量像真实读者任务，而不是泄露答案。它应该包含：

```text
请只按 docs/<目标>/<part>/ 中的 roadmap 步骤一步一步编写代码。
不要从功能来源分支同步代码，不要复制 reference/final-runtime/*.bak，不要套用 reference-runtime.patch。
在新分支或临时 worktree 中实际编辑代码并运行验证。
如果文档步骤和实际结果不一致，记录不一致、复现命令和可能解决方案。
验证完成后，生成相对 baseline 的非 docs patch，并与 evidence/reference-runtime.patch 或参考分支 patch 做字节级一致比较；只允许忽略换行符格式差异。报告比较结果、命令和差异摘要；主 Agent 会复核你的审计。
验证后清理残留进程。
最终报告通过/不通过、关键命令结果、发现的问题和写入文件。
```

复测记录放置规则：

- 复测通过或失败的长期证据写入 `evidence/validation-log.md`。
- 可复现操作变化写入 `evidence/usage.md`。
- 如果需要保留临时问题清单，可写入 `evidence/redo-check.md` 或用户指定文件；不要把临时草稿默认放进主阅读路径。
- 提交时按用户要求控制范围；如果用户只要求提交 `roadmap/` 和 `evidence/`，不要把临时复测报告或问题草稿混入 commit。

复测失败的处理：

- 不要把失败包装成完成。
- 先判断失败来自文档遗漏、实现错误、环境依赖、测试不稳定还是清理残留。
- 如果是文档遗漏，修文档并重新验证受影响步骤。
- 如果是环境依赖，补 `reference/dependencies.md` 或 `evidence/usage.md` 的依赖检查和安装说明。
- 如果是目标行为边界，补 `roadmap/index.md` 的系统预期状态、完成边界和失败判读。
- 如果是 patch 审计失败，修正文档主线并从干净 baseline 重做；不能把差异记录为“可接受”后通过。
- 如果修复方式变成复制 oracle 或新增完整最终代码清单，必须撤回，改为补充对应 roadmap 章节的增量实现步骤。
- 如果复测无法安全完成，记录阻塞条件、已执行命令、最后可信状态和下一步解法。
