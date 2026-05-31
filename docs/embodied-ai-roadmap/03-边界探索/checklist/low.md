# Low 验收

最低可用验收证明阶段 03 的代码入口存在，并且核心算法可验证。

- `frontier_core.py` 存在，包含 `GridInfo`、`FrontierCandidate`、`find_frontier_candidates()` 和 `filter_cooldown_candidates()`。
- 单测能证明 unknown/free 边界会生成 frontier candidate。
- 单测能证明 goal 坐标落在 free-side centroid，而不是 unknown cell centroid。
- `frontier_explorer` console script 已注册。
- `colcon build --packages-select kibot_one_control` 通过。
