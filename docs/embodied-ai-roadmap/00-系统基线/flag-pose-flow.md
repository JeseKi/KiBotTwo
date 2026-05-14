# 当前旗帜位姿链路

## 结论

当前 `/flag_pose` 不是视觉检测结果，而是 Gazebo 中 `follow_flag` 模型的位姿，经 `ros_gz_bridge` 转成 ROS2 `PoseStamped` 后提供给 `follow_controller`。

这正是后续路线图要替换的关键链路。

## 当前链路图

```text
src/kibot_one_sim/worlds/*.world.sdf
  -> include model://follow_flag
  -> src/kibot_one_sim/models/follow_flag/model.sdf
  -> gz-sim-pose-publisher-system
  -> Gazebo topic: /model/follow_flag/pose
  -> ros_gz_bridge
  -> ROS topic: /flag_pose
  -> follow_controller
  -> /cmd_vel_raw
  -> cmd_vel_watchdog
  -> /cmd_vel
  -> Gazebo DiffDrive
```

## 位姿发布者

| 项目 | 内容 |
| --- | --- |
| 真实来源 | Gazebo 中的 `follow_flag` 模型 |
| 模型文件 | `src/kibot_one_sim/models/follow_flag/model.sdf` |
| 发布插件 | `gz-sim-pose-publisher-system` |
| Gazebo topic | `/model/follow_flag/pose` |
| Bridge 配置 | `src/kibot_one_sim/config/ros_gz_bridge.yaml` |
| ROS topic | `/flag_pose` |
| ROS 消息类型 | `geometry_msgs/msg/PoseStamped` |
| frame_id | `world` |
| 默认世界旗帜位置 | `(2.5, 1.0, 0)` |
| 障碍物世界旗帜位置 | `(2.8, 1.1, 0)` |

## 位姿消费者

| 项目 | 内容 |
| --- | --- |
| 节点名 | `follow_controller` |
| 文件路径 | `src/kibot_one_control/kibot_one_control/follow_controller.py` |
| 订阅 topic | `/flag_pose`，参数名 `flag_pose_topic` |
| 消息类型 | `geometry_msgs/msg/PoseStamped` |
| 使用字段 | `pose.position.x`、`pose.position.y` |
| 行为影响 | 作为 FOLLOW 模式目标点 |

## 行为计算方式

`follow_controller` 同时读取：

- `/mode`：确认当前是否为 FOLLOW 模式。
- `/robot_pose`：优先使用机器人在 Gazebo world 中的位姿。
- `/odom`：当没有 `/robot_pose` 时作为备用机器人位姿。
- `/flag_pose`：旗帜在 world 中的位置。
- `/scan`：用于局部避障。

核心行为是：

```text
flag_x - robot_x -> dx
flag_y - robot_y -> dy
atan2(dy, dx) -> 目标方向
hypot(dx, dy) -> 到旗帜距离

如果距离 <= stop_distance：
  发布零速度
否则：
  根据目标方向和 scan 选择局部安全航向
  发布 /cmd_vel_raw
```

默认停止距离：`0.60 m`。

## 为什么这条链路需要替换

这条链路直接把仿真内部真实位姿交给控制器，相当于系统已经“知道旗帜在哪里”。

它不符合后续目标：

```text
旗帜位置变化后，小车应通过探索和视觉感知找到旗帜。
```

当前链路绕过了：

- 图像获取。
- 视觉检测。
- 目标确认。
- 目标相对位置估计。
- 地图中的目标定位。

## 旧的 `flag_pose_publisher`

项目中还存在一个 Python 节点：

- 文件：`src/kibot_one_control/kibot_one_control/flag_pose_publisher.py`
- 节点：`flag_pose_publisher`
- 功能：按参数发布固定 `/flag_pose`
- 默认 frame：`odom`
- 默认位置：`(2.5, 1.0, 0)`

该节点当前没有出现在主 bringup launch 中。它可以作为早期测试工具，但不应作为后续自主任务的真实输入。

## 后续替换策略

推荐替换方向：

```text
第一步：保留 /flag_pose 作为 debug 对照，不再作为 mission 输入
第二步：新增 camera 和 image topic
第三步：新增 flag_detector，发布 /flag_detection
第四步：mission_manager 消费 /flag_detection
第五步：如需要靠近，再引入 /flag_estimated_pose
```

不建议直接让视觉节点伪装成 `/flag_pose`，因为这样会继续让任务逻辑误以为旗帜位姿是可靠全局真值。

## 后续接口建议

第一版检测接口可以表达“是否看见旗帜”，不必马上表达全局位置。

候选 topic：

```text
/flag_detection
```

候选信息：

```text
detected
confidence
bbox center
bbox size
source frame
stamp
```

靠近旗帜阶段再考虑：

```text
/flag_estimated_pose
```
