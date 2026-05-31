# Medium 验收

功能完整验收证明探索节点能接入阶段 02 的 Nav2 runtime。

- `frontier_exploration.launch.py --show-args` 能展示本阶段参数和阶段 02 Nav2 参数。
- 不启动 Gazebo/Nav2 时，`frontier_explorer` 能启动并等待 `/map`，无 Python traceback。
- 完整 launch 中 Nav2 lifecycle 能进入 active。
- explorer 至少发送一个 frontier goal 到 `/navigate_to_pose`。
- 至少一个 frontier goal 返回 `succeeded`。
- 被拒绝的 goal 不会导致节点退出。
