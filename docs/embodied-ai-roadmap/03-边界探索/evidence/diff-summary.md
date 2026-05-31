# 探针 diff 摘要

## 探针信息

分支：

```text
roadmap-probe/03-frontier-exploration
```

commit：

```text
bd5837fc9c2d90fdbc271bd6e9542110734c41cc
```

共同 baseline：

```text
6f0ef3bb59e898d3f11ecabb04518b37321be9b5
```

## Runtime diff

```text
src/kibot_one_control/kibot_one_control/frontier_core.py             | 194 +++++++++++++++++++
src/kibot_one_control/kibot_one_control/frontier_explorer.py         | 214 +++++++++++++++++++++
src/kibot_one_control/launch/frontier_exploration.launch.py          |  55 ++++++
src/kibot_one_control/package.xml                                    |   3 +
src/kibot_one_control/setup.py                                       |   2 +
src/kibot_one_control/test/test_frontier_core.py                     |  66 +++++++
6 files changed, 534 insertions(+)
```

完整 patch：

```text
evidence/reference-runtime.patch
```

## 关键设计结论

- frontier goal 必须落在边界的已知空闲侧，不能直接落在 unknown cell 质心。
- action server 存在不等价于 Nav2 lifecycle active；启动早期 rejected goal 要进入 cooldown，而不是让节点退出。
- 阶段 03 不需要修改阶段 02 的 Nav2 参数，复用 `/navigate_to_pose` action 契约即可。
- 核心地图算法应保持纯 Python，便于不启动仿真的单测验证。
