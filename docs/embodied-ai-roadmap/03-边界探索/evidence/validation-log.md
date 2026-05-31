# 验证日志

## 探针验证

执行者：当前 Agent。

分支：`roadmap-probe/03-frontier-exploration`

commit：`bd5837fc9c2d90fdbc271bd6e9542110734c41cc`

命令和结果：

| 命令 | 结果 |
| --- | --- |
| `python3 -m py_compile ...` | 通过，退出码 0 |
| `PYTHONPATH=src/kibot_one_control python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py` | 通过，`3 passed in 0.01s` |
| `colcon build --packages-select kibot_one_control` | 通过，`Summary: 1 package finished` |
| `ros2 launch kibot_one_control frontier_exploration.launch.py --show-args` | 通过，参数正常展示 |
| `timeout 8s ros2 launch ... start_sim:=false start_slam:=false start_nav2:=false check_runtime_deps:=false` | 通过，explorer process started；退出码 124 为 timeout 截断 |
| `timeout 35s ros2 launch kibot_one_control frontier_exploration.launch.py use_rviz:=false` | 通过，至少一个 frontier goal succeeded，并继续发送第二个 frontier |

## 已观察到的运行时现象

- Nav2 lifecycle active 前，`/navigate_to_pose` action server 可能存在但拒绝 goal。
- explorer 对 rejected goal 进入 cooldown 后，后续能重新发送 frontier。
- 第一个完整 frontier goal `7:11` 成功到达。
- 成功后 explorer 继续发送 `8:18`。

## 文档复测方式

本环境的 sub-agent 工具策略只允许用户显式要求时才派生子 Agent；本次用户没有要求并行子 Agent，因此文档复测由当前 Agent 在临时分支执行。

复测必须满足：

- 从共同 baseline 重新得到 runtime 文件。
- 非 `docs/` diff 与 `evidence/reference-runtime.patch` 完全一致。
- 至少重新运行静态编译、单测和 `kibot_one_control` 构建。

复测结果追加在本文件末尾。

## 文档复测结果

本节是主 Agent 执行的复测，随后又执行了一次独立 sub agent 复测，见下一节。

复测分支：

```text
tmp/03-roadmap-redo-check
```

复测 worktree：

```text
/tmp/kibot-redo-03
```

复测说明：

- 从共同 baseline `6f0ef3bb59e898d3f11ecabb04518b37321be9b5` 创建临时 worktree。
- 按 `roadmap/` 和 `reference/final-runtime/` 重建 runtime 文件。
- 临时 worktree 没有自己的 `.venv/` 和初始 `install/`，因此先在主 workspace 执行 `source .vscode/project-terminal-init.sh`，再进入临时 worktree 运行验证。

复测命令和结果：

| 命令 | 结果 |
| --- | --- |
| `python3 -m py_compile ...` | 通过，退出码 0 |
| `PYTHONPATH=src/kibot_one_control python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py` | 通过，`3 passed in 0.02s` |
| `colcon build --packages-select kibot_one_control` | 通过，`Summary: 1 package finished`；提示 `kibot_one_interface` 和 `kibot_one_sim` 来自主 workspace install |
| `ros2 launch kibot_one_control frontier_exploration.launch.py --show-args` | 通过，参数正常展示 |
| `diff -u evidence/reference-runtime.patch /tmp/redo-03.diff` | 通过，无输出 |

复测结论：

- 复测 runtime patch 与探针 runtime patch 完全一致。
- 复测未重新跑 35 秒完整仿真，原因是探针阶段已经完成完整短时仿真；复测重点用于证明文档和 final-runtime oracle 能重建完全一致的代码并通过构建、单测和 launch 参数验证。

清理：

- 复测期间未启动 Gazebo。
- 已执行 `git worktree remove --force /tmp/kibot-redo-03`。
- 已删除临时分支 `tmp/03-roadmap-redo-check`。

## 独立 sub agent 文档复测结果

复测者：独立 sub agent `019e7c74-f5fb-74a1-a81d-e6f529bac8e6`。

复测目的：

- 验证复测者在没有探针实现上下文的情况下，只看当前文档状态，是否能从共同 baseline 重建阶段 03 runtime。
- 验证重建后的非 `docs/` diff 是否与 `evidence/reference-runtime.patch` 完全一致。

复测限制：

- 只允许阅读 `docs/embodied-ai-roadmap/index.md`、`docs/embodied-ai-roadmap/03-边界探索/**`、`mkdocs.yml` 和环境说明。
- 不允许读取 `roadmap-probe/03-frontier-exploration` 分支源码。
- 不允许从功能分支同步代码。
- runtime 文件只写入临时 worktree。

实际阅读文档：

- `AGENTS.md`
- `mkdocs.yml`
- `docs/embodied-ai-roadmap/index.md`
- `docs/embodied-ai-roadmap/03-边界探索/roadmap/*.md`
- `docs/embodied-ai-roadmap/03-边界探索/reference/*.md`
- `docs/embodied-ai-roadmap/03-边界探索/reference/final-runtime/README.md`
- `docs/embodied-ai-roadmap/03-边界探索/reference/final-runtime/**/*.bak`
- `docs/embodied-ai-roadmap/03-边界探索/evidence/*.md`
- `docs/embodied-ai-roadmap/03-边界探索/checklist/*.md`

临时 worktree：

```text
/tmp/kibot-subagent-redo-03-30423
```

临时写入 runtime 文件：

- `src/kibot_one_control/kibot_one_control/frontier_core.py`
- `src/kibot_one_control/kibot_one_control/frontier_explorer.py`
- `src/kibot_one_control/launch/frontier_exploration.launch.py`
- `src/kibot_one_control/test/test_frontier_core.py`
- `src/kibot_one_control/package.xml`
- `src/kibot_one_control/setup.py`

复测命令和结果：

| 命令 | 结果 |
| --- | --- |
| `python3 -m py_compile ...` | 通过，退出码 0 |
| `PYTHONPATH=src/kibot_one_control python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py` | 通过，`3 passed in 0.01s` |
| `colcon build --packages-select kibot_one_control` | 通过，`Summary: 1 package finished` |
| `ros2 launch kibot_one_control frontier_exploration.launch.py --show-args` | 通过，展示 `world`、`use_rviz`、`start_explorer` 和阶段 02 Nav2 透传参数 |
| `timeout 8s ros2 launch ... start_sim:=false start_slam:=false start_nav2:=false check_runtime_deps:=false` | 通过，`frontier_explorer` process started；退出码 124；无 traceback |
| `diff -u docs/embodied-ai-roadmap/03-边界探索/evidence/reference-runtime.patch /tmp/redo-03-runtime.diff` | 通过，无输出 |

复测结论：

- 按复测当时的旧口径：通过。sub agent 使用当前文档状态中的 `final-runtime/*.bak` 和 `reference-runtime.patch` 作为 oracle，从共同 baseline 重建了阶段 03 runtime，且非 `docs/` diff 与 patch 完全一致。
- 按更新后的 skill 规则：不通过。原因是 sub agent 明确指出 byte-for-byte 复现依赖 `reference/final-runtime/*.bak` 和 `evidence/reference-runtime.patch`，而不是只依赖 `roadmap/` / `reference/` 中的实施说明完成手写复现。
- sub agent 未跑 35 秒完整 Gazebo 仿真；探针阶段已经跑过完整短时仿真，独立复测覆盖静态、单测、构建、launch 参数和无仿真节点冒烟。

发现的风险边界：

- 严格 byte-for-byte 复现依赖 `reference/final-runtime/*.bak` 和 `evidence/reference-runtime.patch` 作为文档 oracle。
- 如果只阅读 `roadmap/` 正文而不使用 `.bak`，部分实现细节不足以保证手写结果与探针 runtime 完全一致。
- 按更新后的 skill 规则，这不是可接受风险，而是文档复测失败条件。下一步必须把完整实现细节从 `.bak` 反哺进 `roadmap/` 或 `reference/`，然后重新启动 sub agent 复测。

清理状态：

- sub agent 已删除临时 worktree `/tmp/kibot-subagent-redo-03-30423`。
- sub agent 已删除临时分支 `tmp/subagent-redo-03-30423`。
- sub agent 已删除临时 diff/path 文件。
- sub agent 已检查无 `gz sim server`、`frontier_explorer`、`controller_server`、`bt_navigator`、`async_slam_toolbox_node`、`bridge_node` 残留进程。

## 严格 roadmap-only sub agent 复测结果

复测者：独立 sub agent `019e7c7f-9334-7ee3-88fc-a007a9a8d6b0`。

复测口径：

- 只按 `roadmap/` 步骤一步一步手写 runtime 代码。
- `reference/final-runtime/*.bak` 和 `evidence/reference-runtime.patch` 不能作为代码来源。
- `evidence/reference-runtime.patch` 只在手写实现和验证完成后作为最终审计对象。
- 复测非 `docs/` patch 必须与 reference patch 字节级一致，只允许忽略换行符格式差异。

实际阅读文档：

- `roadmap/index.md`
- `roadmap/01-拆出-frontier-核心算法.md`
- `roadmap/02-接入-ROS2-探索节点.md`
- `roadmap/03-增加探索-launch-入口.md`
- `roadmap/04-验证探索闭环.md`
- `roadmap/05-交付阶段-06-契约.md`
- `reference/frontier-contract.md`
- `reference/file-plan.md`
- `evidence/usage.md`
- `evidence/diff-summary.md`
- 本地 `guided-engineering-roadmap` skill 验证说明
- `evidence/reference-runtime.patch`，仅用于最终审计

手写/修改 runtime 文件：

- `src/kibot_one_control/kibot_one_control/frontier_core.py`
- `src/kibot_one_control/kibot_one_control/frontier_explorer.py`
- `src/kibot_one_control/launch/frontier_exploration.launch.py`
- `src/kibot_one_control/test/test_frontier_core.py`
- `src/kibot_one_control/package.xml`
- `src/kibot_one_control/setup.py`

验证命令和结果：

| 命令 | 结果 |
| --- | --- |
| `python3 -m py_compile ...` | 通过 |
| `pytest -q src/kibot_one_control/test/test_frontier_core.py` | 通过，`3 passed in 0.01s` |
| `colcon build --packages-select kibot_one_control` | 通过，`Summary: 1 package finished` |
| `ros2 launch kibot_one_control frontier_exploration.launch.py --show-args` | 通过，能看到 `world/use_rviz/start_explorer` 和阶段 02 Nav2 参数 |
| 无仿真冒烟 | 通过，`frontier_explorer` process started，`timeout` 退出码 `124`，无 traceback |
| 35s 完整仿真 | 达到关键观测：先因 Nav2 inactive 被拒绝一次，随后 Nav2 active，explorer 发送 frontier，controller 到达目标，`Goal succeeded`，explorer 继续发送第二个 frontier |

patch 一致性：

- 不通过。
- 换行规范化后仍不一致。
- reference patch：`20980` bytes。
- redo patch：`21352` bytes。
- reference diff 统计：`534 insertions`。
- redo diff 统计：`569 insertions`。

差异摘要：

- `frontier_core.py`：reference 为 194 行，redo 为 208 行。roadmap 不足以确定精确 helper 结构、是否使用 `Sequence/Iterable`、是否做 `_validate_grid`、free-side centroid 用 4 邻域还是 8 邻域，以及 key/centroid 的精确实现形式。
- `frontier_explorer.py`：reference 为 214 行，redo 为 224 行。roadmap 不足以确定精确参数声明风格、类型 cast/import、`PoseStamped` 使用、`ExternalShutdownException` 处理、action result/status 辅助函数和日志实现细节。
- `frontier_exploration.launch.py`：reference 为 55 行，redo 为 58 行，主要是结构/格式与返回 `LaunchDescription` 细节不一致。
- `test_frontier_core.py`：reference 为 66 行，redo 为 74 行。roadmap 只说明覆盖点，不足以复现 exact test names、fixture 数据和断言值。
- `package.xml` / `setup.py` 插入数量一致，但整体 patch 仍因其他文件差异失败。
- 审计流程缺口：按文档原命令 `git diff --binary --no-ext-diff -- . ':(exclude)docs/**'`，新增文件若未 staging 或未 `git add -N`，不会进入 patch。复测中必须先执行 `git add -N` 才能生成完整 redo patch；这一步需要写入 `evidence/usage.md` 或 validation workflow。

严格复测结论：

- 阶段 03 当前文档复测不通过。
- runtime 行为可以通过验证，但 roadmap 不足以让独立读者生成与 reference patch 字节级一致的 runtime patch。
- 下一步需要把上述缺失实现细节补入 `roadmap/` 或 `reference/`，并重新启动 sub agent 复测。

清理状态：

- sub agent 已删除临时 worktree `/tmp/kibot-strict-redo-03-37973`。
- sub agent 已删除临时分支 `tmp/strict-redo-03-37973`。
- sub agent 已删除临时 diff 文件。
- Gazebo / ROS2 残留进程已清理。
- 主 workspace 未写入 runtime 文件。

## roadmap 细节补强后的复测阻塞记录

修正内容：

- `roadmap/01-拆出-frontier-核心算法.md` 已改为按空文件逐步追加片段，覆盖 `frontier_core.py` 和 `test_frontier_core.py` 的关键实现顺序、helper 结构、测试数据和断言。
- `roadmap/02-接入-ROS2-探索节点.md` 已改为按空文件逐步追加片段，覆盖 `frontier_explorer.py` 的 imports、状态字段、QoS、TF、action callback、超时、冷却和 main 入口。
- `roadmap/03-增加探索-launch-入口.md` 已改为按空文件逐步追加片段，覆盖 launch imports、参数、Nav2 include、explorer node 和 `LaunchDescription` 返回结构。
- `evidence/usage.md` 已补充 `git add -N`，避免新增 runtime 文件未进入 redo patch。

严格 sub agent 复测尝试：

| 时间顺序 | sub agent | 结果 |
| --- | --- | --- |
| 第一次 | `019e7c8d-3b7e-7bc3-a032-53eb0f59f415` | 工具认证失败：`Your access token could not be refreshed because your refresh token was already used. Please log out and sign in again.` |
| 第二次 | `019e7c8d-abba-7481-bafc-c680d22dc084` | 同样工具认证失败 |

阻塞结论：

- 当前无法完成更新后文档的 sub agent 复测，阻塞原因是 sub agent 工具认证失败。
- 按更新后的 skill 规则，主 Agent 自己复测不能替代 sub agent 复测，因此阶段 03 仍不能判通过。
- 恢复 sub agent 工具认证后，应重新执行严格 roadmap-only 复测：只按 `roadmap/` 步骤手写 runtime，最后比较非 `docs/` patch 与 `evidence/reference-runtime.patch`，除换行符格式差异外必须字节级一致。

## roadmap 细节补强后的严格复测通过记录

复测者：独立 sub agent `019e7c90-dc63-7470-a41d-00bde2487952`。

复测口径：

- 只按 `roadmap/` 步骤一步一步手写 runtime 代码。
- 不阅读或复制 `reference/final-runtime/**/*.bak`。
- 不套用 `evidence/reference-runtime.patch`，不读取探针分支或功能分支源码。
- `evidence/reference-runtime.patch` 仅在手写实现和验证完成后用于最终审计。
- 复测非 `docs/` patch 必须与 reference patch 字节级一致，只允许忽略换行符格式差异。

实际阅读文档：

- `roadmap/index.md`
- `roadmap/01-拆出-frontier-核心算法.md`
- `roadmap/02-接入-ROS2-探索节点.md`
- `roadmap/03-增加探索-launch-入口.md`
- `roadmap/04-验证探索闭环.md`
- `roadmap/05-交付阶段-06-契约.md`
- `reference/frontier-contract.md`
- `reference/file-plan.md`
- `checklist/low.md`
- `checklist/medium.md`
- `checklist/high.md`
- `evidence/usage.md`
- `evidence/diff-summary.md`
- `evidence/reference-runtime.patch`，仅用于最终审计

手写/修改 runtime 文件：

- `src/kibot_one_control/kibot_one_control/frontier_core.py`
- `src/kibot_one_control/kibot_one_control/frontier_explorer.py`
- `src/kibot_one_control/launch/frontier_exploration.launch.py`
- `src/kibot_one_control/test/test_frontier_core.py`
- `src/kibot_one_control/setup.py`
- `src/kibot_one_control/package.xml`

验证命令和结果：

| 命令 | 结果 |
| --- | --- |
| `python3 -m py_compile ...` | 通过，退出码 0 |
| `PYTHONPATH=src/kibot_one_control python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py` | 通过，`3 passed in 0.01s` |
| `colcon build --packages-select kibot_one_control` | 通过，`Summary: 1 package finished` |
| `ros2 launch kibot_one_control frontier_exploration.launch.py --show-args` | 通过，显示 `world/use_rviz/start_explorer` 和阶段 02 Nav2 透传参数 |
| 无仿真冒烟 | 通过，`frontier_explorer` 启动，`timeout` 退出码 124，无 traceback |
| 35s 完整仿真 | 通过，Nav2 active 后发送 frontier，出现 `Goal succeeded` 和 `frontier goal 7:11 succeeded`，随后继续发送第二个 frontier |

patch 审计：

- 已先对新增 runtime 文件执行 `git add -N`。
- 生成的非 `docs` patch 与 `docs/embodied-ai-roadmap/03-边界探索/evidence/reference-runtime.patch` 字节级一致。
- `cmp` 退出码：0。
- 无差异摘要；无需补缺失 roadmap 步骤。

严格复测结论：

- 通过。阶段 03 文档现在满足严格 roadmap-only 复测要求。
- 独立复测者不依赖 `.bak` 或 reference patch 作为代码来源，也能按 roadmap 步骤写出与 reference patch 字节级一致的 runtime patch。

清理状态：

- sub agent 已删除临时 worktree `/tmp/kibot-strict-redo-03-68207`。
- sub agent 已删除临时分支 `strict-redo-03-68207`。
- sub agent 已删除临时 diff 文件。
- 仿真残留 `gz sim server` 已终止。
- 最终检查未见目标 ROS/Gazebo 残留进程，仅匹配到检查命令自身。
