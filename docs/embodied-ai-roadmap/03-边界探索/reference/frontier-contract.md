# Frontier 探索契约

## 源码已确认

阶段 03 探针分支新增 `frontier_explorer`，运行时依赖：

- `/map`：`nav_msgs/msg/OccupancyGrid`
- `map -> base_link`：TF 查询机器人在地图中的位置
- `/navigate_to_pose`：`nav2_msgs/action/NavigateToPose`

frontier 定义：

```text
unknown cell 且 4 邻域中至少有一个 free cell
```

候选分组：

- 8 邻域连接 frontier cells。
- `min_frontier_size` 过滤小组件。
- `min_goal_distance` 和 `max_goal_distance` 控制目标距离。

goal 位置：

- frontier 的 key 来自未知边界质心。
- Nav2 goal 使用相邻 free cells 的质心。
- goal frame 固定为 `map`。

结果处理：

- rejected / failed / timeout：当前 frontier key 进入 cooldown。
- succeeded：清空当前 goal，下一轮继续选候选。
- timeout：由 explorer 主动 cancel。

## 需要运行时确认

- 不同 world 下 `min_frontier_size`、`max_goal_distance` 和 `frontier_cooldown` 的最佳值。
- 大地图中 frontier 数量增加后的 CPU 开销。
- 狭窄区域中 free-side centroid 是否需要再做 footprint 安全性检查。
- 是否需要给任务状态机新增显式 `/exploration/status`。
