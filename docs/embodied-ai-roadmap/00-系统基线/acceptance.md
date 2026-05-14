# 阶段 00：验收结果

## 验收结论

阶段 00 的源码静态基线调查已完成。

本阶段已经回答：

- 当前有哪些 package。
- 当前主要 launch 入口是什么。
- 当前有哪些传感器。
- 当前有哪些关键 topic / service。
- 当前旗帜位姿如何产生和被消费。
- 当前小车如何被控制。
- 后续 SLAM、Nav2、视觉检测和任务状态机的主要接入风险是什么。

## 已满足项

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| 已记录主要 package 和职责 | 通过 | `system-inventory.md` |
| 已记录主要启动入口 | 通过 | `system-inventory.md` |
| 已记录仿真、bridge、控制节点关系 | 通过 | `system-inventory.md` |
| 已记录当前传感器 | 通过 | `system-inventory.md` |
| 已记录关键 topic | 通过 | `system-inventory.md` |
| 已记录关键 service | 通过 | `system-inventory.md` |
| 已记录当前 TF 判断 | 部分通过 | 需要运行时确认具体 TF tree |
| 已找到旗帜位姿发布者 | 通过 | `flag-pose-flow.md` |
| 已找到旗帜位姿消费者 | 通过 | `flag-pose-flow.md` |
| 已说明旗帜位姿如何影响小车行为 | 通过 | `flag-pose-flow.md` |
| 已说明当前小车控制链路 | 通过 | `system-inventory.md` |

## 需要运行时确认的遗留项

这些不阻塞阶段 00 的静态结论，但会影响阶段 01 的具体实现：

- `/tf` 中是否只有 `odom -> chassis`。
- ROS 侧是否存在 `chassis -> lidar_link` 静态或动态 TF。
- `/scan` 的 header frame 是否稳定为 `lidar_link`。
- `/odom` 的 child frame 是否稳定为 `chassis`。
- Gazebo bridge 实际运行时是否完全按配置发布 `/flag_pose` 和 `/robot_pose`。

## 阶段 01 解锁判断

`01-SLAM-建图与定位` 可以进入详细 roadmap 编写。

理由：

- 已有 `/scan`，类型为 `sensor_msgs/msg/LaserScan`。
- 已有 `/odom`，类型为 `nav_msgs/msg/Odometry`。
- 机器人模型中已有 2D 激光雷达。

进入阶段 01 前必须优先处理：

- `chassis` 与 `base_link` 的关系。
- `lidar_link` 与机器人基座 frame 的 TF。
- 是否需要增加 `robot_state_publisher` 或静态 TF 发布。
- `map -> odom -> base_link` 目标链路设计。

## 阶段 04 解锁判断

`04-视觉旗帜检测` 可以进入详细 roadmap 编写，但不能直接实现检测节点。

理由：

- 当前机器人没有相机。
- 当前没有 image topic。
- 旗帜模型有红色旗面，适合后续简单视觉方案。

进入阶段 04 前必须优先处理：

- 给 SDF 机器人模型增加 RGB camera。
- 通过 `ros_gz_bridge` 暴露 `sensor_msgs/msg/Image`。
- 确认 camera frame。
- 决定第一版是“发现即停止”还是“发现后靠近”。

## 不建议立即进入的阶段

不建议直接进入：

- `02-Nav2-导航接入`，因为还没有 SLAM 和清晰 TF。
- `03-边界探索`，因为还没有地图和 Nav2。
- `05-旗帜位置估计`，因为还没有相机或深度来源。
- `06-任务状态机`，因为探索和视觉输入都尚未建立。
