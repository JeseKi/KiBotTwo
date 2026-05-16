# Nav2 接口契约

## Frame

| 用途 | 值 |
| --- | --- |
| global frame | `map` |
| odom frame | `odom` |
| robot base frame | `base_link` |
| lidar frame | `lidar_link` |

## Topic

| Topic | 类型 | 作用 |
| --- | --- | --- |
| `/scan` | `sensor_msgs/msg/LaserScan` | local/global costmap 障碍物来源 |
| `/odom` | `nav_msgs/msg/Odometry` | controller 与 smoother 的里程计来源 |
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM 地图；探索模块可用于 frontier 选择 |
| `/cmd_vel_nav` | `geometry_msgs/msg/Twist` | Nav2 controller / behavior 原始速度输出 |
| `/cmd_vel_smoothed` | `geometry_msgs/msg/Twist` | velocity smoother 输出；当前 Gazebo bridge 的速度输入 |

## Action

阶段 03 应使用：

```text
/navigate_to_pose
```

目标 `PoseStamped.header.frame_id` 应使用：

```text
map
```

## 成功与失败解释

阶段 03 只需要处理这些结果类别：

- 成功：frontier 目标完成，可以继续选择下一个 frontier。
- 失败：目标不可达或规划失败，将该 frontier 临时降权或加入冷却列表。
- 取消：任务状态机或视觉检测打断探索。
- 超时：探索模块主动取消 goal，切换候选目标。

## 已运行时确认

- `NavigateToPose` 成功时 action status 为 `SUCCEEDED`，`error_code: 0`。
- 0.5m 短距离目标能让 `/odom` 实际前进。
- 当前阶段的 global costmap 不使用 `static_layer`，用 rolling obstacle/inflation 支撑探索目标执行。
