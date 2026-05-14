# 当前系统盘点

## 项目概览

当前 workspace 是 ROS2 + Gazebo Sim 项目，源码集中在 `src` 下。

| Package | 类型 | 主要职责 | 备注 |
| --- | --- | --- | --- |
| `kibot_one_control` | `ament_python` | 模式控制、速度看门狗、键盘遥控、控制台、旗帜跟随控制 | 当前任务逻辑主要在这里 |
| `kibot_one_interface` | `ament_cmake` 接口包 | 定义模式相关 msg / srv | 当前只有 Mode / ModeState / Mode 服务 |
| `kibot_one_sim` | `ament_cmake` 资源包 | Gazebo 模型、世界、launch、ROS-Gazebo bridge 配置 | 当前机器人和旗帜都是 SDF 模型 |

## 启动入口

| 启动命令 | Launch 文件 | 作用 | 备注 |
| --- | --- | --- | --- |
| `ros2 launch kibot_one_sim kibot_one.launch.py` | `src/kibot_one_sim/launch/kibot_one.launch.py` | 主 bringup：Gazebo、bridge、mode_control、cmd_vel_watchdog、follow_controller | 默认模式是 MANUAL，默认启动 follow_controller |
| `ros2 launch kibot_one_control follow_phase1.launch.py` | `src/kibot_one_control/launch/follow_phase1.launch.py` | 无障碍世界 FOLLOW 演示 | 使用 `kibot_one.world.sdf`，mode 默认 3 |
| `ros2 launch kibot_one_control follow_phase2.launch.py` | `src/kibot_one_control/launch/follow_phase2.launch.py` | 障碍物世界 FOLLOW 演示 | 使用 `kibot_one_obstacles.world.sdf`，mode 默认 3 |
| `ros2 launch kibot_one_control control_console.launch.py` | `src/kibot_one_control/launch/control_console.launch.py` | 启动交互式控制台 | 需要终端 stdin |
| `ros2 launch kibot_one_sim sim_with_bridge.launch.py` | `src/kibot_one_sim/launch/sim_with_bridge.launch.py` | 启动 Gazebo 和 ros_gz_bridge | 被主 bringup 引用 |
| `ros2 launch kibot_one_sim gazebo.launch.py` | `src/kibot_one_sim/launch/gazebo.launch.py` | 仅启动 Gazebo | 被 sim_with_bridge 引用 |

## 主要节点

| 节点名 | 所属 package | 作用 | 输入 | 输出 |
| --- | --- | --- | --- | --- |
| `mode_control` | `kibot_one_control` | 管理 STOP / CRUISE / MANUAL / FOLLOW 模式 | `/mode_control` 服务请求 | `/mode`，STOP/CRUISE 下发布 `/cmd_vel_raw` |
| `cmd_vel_watchdog` | `kibot_one_control` | 将 `/cmd_vel_raw` 转发到 `/cmd_vel`，超时自动停车 | `/cmd_vel_raw` | `/cmd_vel` |
| `follow_controller` | `kibot_one_control` | FOLLOW 模式下根据旗帜位姿、机器人位姿和激光雷达输出速度 | `/mode`、`/odom`、`/robot_pose`、`/flag_pose`、`/scan` | `/cmd_vel_raw` |
| `keyboard_teleop` | `kibot_one_control` | MANUAL 模式键盘遥控 | `/mode`、键盘输入 | `/cmd_vel_raw` |
| `control_console` | `kibot_one_control` | 交互式模式切换和手操控制台 | `/mode`、`/mode_control`、键盘输入 | `/cmd_vel_raw`、服务请求 |
| `kibot_one_bridge` | `ros_gz_bridge` | 桥接 Gazebo 和 ROS2 topic | Gazebo / ROS topic | ROS / Gazebo topic |
| `flag_pose_publisher` | `kibot_one_control` | 发布固定旗帜位姿 | 参数 | `/flag_pose` |

备注：`flag_pose_publisher` 在 `setup.py` 中注册，但未在当前主 launch 中启动。当前主链路的 `/flag_pose` 来自 Gazebo bridge。

## 传感器列表

| 传感器 | 是否存在 | ROS Topic | Frame | 用途 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 2D lidar | 存在 | `/scan` | `lidar_link` | SLAM / 局部避障 | 可作为阶段 01 输入 |
| RGB camera | 不存在 | 无 | 无 | 旗帜检测 | 阶段 04 需要新增 |
| depth camera | 不存在 | 无 | 无 | 旗帜 3D 位置估计 | 阶段 05 如要靠近需考虑 |
| imu | 不存在 | 无 | 无 | 定位辅助 | 第一版可不依赖 |
| odom | 存在 | `/odom` | `odom -> chassis` | 定位 / 控制 | 可作为阶段 01 输入，但 frame 命名需处理 |

## 关键 Topic

| Topic | 消息类型 | 发布者 | 订阅者 | 作用 |
| --- | --- | --- | --- | --- |
| `/cmd_vel_raw` | `geometry_msgs/msg/Twist` | `mode_control`、`follow_controller`、`keyboard_teleop`、`control_console` | `cmd_vel_watchdog` | 项目内部原始速度命令 |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `cmd_vel_watchdog` | `ros_gz_bridge` -> Gazebo DiffDrive | 最终机器人速度命令 |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo DiffDrive -> `ros_gz_bridge` | `follow_controller` | 机器人里程计 |
| `/tf` | `tf2_msgs/msg/TFMessage` | Gazebo DiffDrive -> `ros_gz_bridge` | ROS TF consumers | 当前主要是里程计 TF |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo lidar -> `ros_gz_bridge` | `follow_controller` | 激光雷达扫描 |
| `/robot_pose` | `geometry_msgs/msg/PoseStamped` | Gazebo PosePublisher -> `ros_gz_bridge` | `follow_controller` | 机器人在 Gazebo world 中的位姿 |
| `/flag_pose` | `geometry_msgs/msg/PoseStamped` | Gazebo PosePublisher -> `ros_gz_bridge` | `follow_controller` | 旗帜在 Gazebo world 中的位姿 |
| `/mode` | `kibot_one_interface/msg/ModeState` | `mode_control` | `follow_controller`、`keyboard_teleop`、`control_console` | 当前运行模式 |

## 关键 Service

| Service | 类型 | 提供者 | 调用者 | 作用 |
| --- | --- | --- | --- | --- |
| `/mode_control` | `kibot_one_interface/srv/Mode` | `mode_control` | `control_console`、命令行 | 切换 STOP / CRUISE / MANUAL / FOLLOW |

## 关键 Action

当前项目未发现自定义 action，也未接入 Nav2 action。

后续 Nav2 接入时，预计会引入：

- `NavigateToPose`
- 可能的 `FollowPath`

## 关键 TF Frame

| 父 Frame | 子 Frame | 发布者 | 当前判断 | 备注 |
| --- | --- | --- | --- | --- |
| `odom` | `chassis` | Gazebo DiffDrive -> `/tf` | 源码中明确配置 | `child_frame_id` 是 `chassis`，不是 `base_link` |
| `chassis` | `lidar_link` | SDF fixed joint | ROS 侧待运行确认 | SDF 中存在 fixed joint，但 bridge 是否提供该 TF 需要确认 |
| `map` | `odom` | 无 | 当前不存在 | SLAM 阶段需要引入 |
| `base_link` | 未定义 | 无 | 当前不存在 | Nav2 / SLAM 可能需要适配 |
| `world` | `flag_pose` | bridge frame_id | 以 PoseStamped header 表达 | 不是 TF tree 中的目标 frame |
| `world` | `robot_pose` | bridge frame_id | 以 PoseStamped header 表达 | 不是 TF tree 中的目标 frame |

## 小车控制链路

当前控制链路如下：

```text
mode_control / follow_controller / keyboard_teleop / control_console
  -> /cmd_vel_raw
  -> cmd_vel_watchdog
  -> /cmd_vel
  -> ros_gz_bridge
  -> /model/kibot_one_base/cmd_vel
  -> Gazebo DiffDrive
  -> robot motion
```

关键判断：

- 最终速度命令 topic 是 `/cmd_vel`。
- 当前没有全局路径规划。
- 当前没有导航目标 action。
- FOLLOW 模式是基于目标点方向的局部控制，不是 Nav2 导航。
- 停车逻辑存在于 `follow_controller` 的 `stop_distance` 判断，以及 `cmd_vel_watchdog` 的超时停车。

## 仿真世界

| World | 文件 | 内容 |
| --- | --- | --- |
| 默认世界 | `src/kibot_one_sim/worlds/kibot_one.world.sdf` | 地面、机器人、旗帜，旗帜位置约 `(2.5, 1.0, 0)` |
| 障碍物世界 | `src/kibot_one_sim/worlds/kibot_one_obstacles.world.sdf` | 地面、机器人、旗帜、多个箱体和圆柱障碍物，旗帜位置约 `(2.8, 1.1, 0)` |

## 与后续阶段相关的结论

### 对 SLAM 的影响

有 `/scan` 和 `/odom`，具备接入 2D SLAM 的基础。

需要优先处理：

- `base_link` 缺失。
- `chassis -> lidar_link` ROS TF 待确认。
- `map` frame 缺失。

### 对 Nav2 的影响

Nav2 可使用 `/cmd_vel` 作为控制出口，但必须处理控制权冲突。

当前多个节点可能发布 `/cmd_vel_raw`，而 Nav2 通常直接发布 `/cmd_vel`。如果不隔离，会出现控制源冲突。

### 对视觉旗帜检测的影响

当前没有相机，不能直接做视觉检测节点。

旗帜视觉模型是红色矩形旗面，适合第一版做 HSV / 颜色阈值检测。

### 对任务状态机的影响

当前模式系统可以作为参考，但当前 FOLLOW 逻辑与 `/flag_pose` 强耦合。

后续任务状态机应消费“探索状态”和“视觉检测状态”，不应继续直接依赖 Gazebo 旗帜位姿。
