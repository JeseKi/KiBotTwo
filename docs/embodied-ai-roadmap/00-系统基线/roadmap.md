# 阶段 00：系统基线调查报告

## 本阶段定位

本阶段由 Agent 负责完成项目梳理，用于承接当前系统，并为后续 SLAM、Nav2、自主探索和视觉旗帜检测提供工程入口。

本阶段不是学习任务清单，也不是功能实现阶段。它的产物应该回答：

```text
当前系统是什么样？
当前能力边界在哪里？
后续阶段应该从哪里接入？
哪些现有逻辑需要保留、替换或隔离？
```

## 调查方式

本次基线基于源码静态分析完成，未启动 Gazebo 或 ROS2 graph 做运行时采样。

已阅读范围：

- `README.md`
- `src/kibot_one_control` 的 package、launch 和 Python 节点
- `src/kibot_one_interface` 的 msg / srv 接口
- `src/kibot_one_sim` 的 launch、bridge 配置、world 和 SDF 模型

## 核心结论

当前系统是一个基于 Gazebo Sim 的移动机器人仿真项目，主要能力是：

- 启动 Gazebo 世界。
- 通过 `ros_gz_bridge` 桥接 Gazebo 和 ROS2。
- 使用 `/cmd_vel` 控制 Gazebo 中的差速机器人模型。
- 使用 `/odom`、`/robot_pose`、`/flag_pose` 和 `/scan` 做目标跟随。
- 通过模式系统在 STOP、CRUISE、MANUAL、FOLLOW 之间切换。
- FOLLOW 模式下，`follow_controller` 直接读取机器人全局位姿和旗帜全局位姿，结合激光雷达做局部避障跟随。

当前系统还不具备：

- 相机传感器。
- 深度相机。
- IMU。
- SLAM。
- Nav2。
- `map` frame。
- 标准 `base_link` frame。
- 基于视觉的旗帜检测。
- 自主探索。

## 当前主线数据流

```text
Gazebo world
  -> kibot_one_base model
  -> DiffDrive plugin
  -> /model/kibot_one_base/odometry
  -> ros_gz_bridge
  -> /odom

Gazebo world
  -> follow_flag model
  -> PosePublisher plugin
  -> /model/follow_flag/pose
  -> ros_gz_bridge
  -> /flag_pose

Gazebo lidar
  -> /scan
  -> ros_gz_bridge
  -> /scan

/mode
/odom or /robot_pose
/flag_pose
/scan
  -> follow_controller
  -> /cmd_vel_raw
  -> cmd_vel_watchdog
  -> /cmd_vel
  -> ros_gz_bridge
  -> /model/kibot_one_base/cmd_vel
  -> Gazebo DiffDrive
```

## 当前任务逻辑判断

当前“找旗帜”的任务并不是感知任务，而是位姿跟随任务。

`follow_controller` 直接订阅 `/flag_pose`，从消息中读取 `x/y` 作为目标点；同时订阅 `/robot_pose` 或 `/odom` 获取机器人自身位置，再计算到旗帜的方向和距离。当距离小于 `stop_distance` 时发布零速度停止。

这条链路绕过了：

- 视觉发现。
- 目标识别。
- 从图像估计目标位置。
- 地图构建。
- 全局路径规划。

因此后续目标不是简单替换某个参数，而是要逐步把“已知旗帜位姿输入”改造成“运行时视觉感知输入”。

## 对后续阶段的直接影响

### 对阶段 01：SLAM 建图与定位

当前已有 `/scan` 和 `/odom`，这是接入 2D SLAM 的基础。

但存在关键风险：

- 当前机器人坐标 frame 是 `chassis`，不是 Nav2 / SLAM 常见的 `base_link`。
- 激光 frame 是 `lidar_link`，但 ROS 侧是否存在 `chassis -> lidar_link` 的 TF 需要运行时确认。
- 当前没有 `map` frame。
- 当前没有 `robot_state_publisher`，模型是 Gazebo SDF，不是 URDF / Xacro。

阶段 01 的首要任务应该不是直接调 `slam_toolbox` 参数，而是先补齐或确认 TF 结构。

### 对阶段 02：Nav2 导航接入

当前控制入口是 `/cmd_vel`，理论上 Nav2 controller 可以输出到 `/cmd_vel`。

但当前已有 `cmd_vel_watchdog` 和多个控制节点会通过 `/cmd_vel_raw -> /cmd_vel` 链路控制机器人。后续接入 Nav2 时必须避免多个控制源同时发布速度。

阶段 02 需要明确：

- Nav2 是否直接发布 `/cmd_vel`。
- 是否保留 `cmd_vel_watchdog`。
- FOLLOW / MANUAL / CRUISE 模式与 Nav2 控制权如何互斥。

### 对阶段 03：边界探索

当前没有地图，也没有 Nav2，因此不能直接做 frontier exploration。

边界探索必须依赖：

- `map`。
- 机器人在 `map` 中的定位。
- 可用的 Nav2 goal 接口。

### 对阶段 04：视觉旗帜检测

当前没有相机，因此视觉检测阶段必须先给机器人模型增加 RGB camera，并通过 bridge 暴露 ROS2 图像 topic。

当前旗帜模型具备红色旗面，尺寸约为 `0.30 x 0.02 x 0.20`，适合第一版用颜色阈值做检测。

### 对阶段 05：旗帜位置估计

当前没有深度相机。若只增加 RGB camera，第一版可以先做“发现即停止”；若要“发现后靠近”，需要至少满足一个条件：

- 增加 depth camera。
- 利用已知旗帜尺寸做单目测距。
- 结合机器人运动和多帧观测做估计。

### 对阶段 06：任务状态机

当前模式系统已经有 STOP、CRUISE、MANUAL、FOLLOW，但 FOLLOW 逻辑是“直接跟随旗帜位姿”。

后续可以复用模式管理思想，但不建议继续把探索、视觉、导航和停止逻辑塞进现有 `follow_controller`。

更合理的方向是新增 mission manager，让它管理：

```text
探索中
  -> 发现旗帜
  -> 取消探索目标
  -> 靠近或停止
  -> 任务结束
```

## 本阶段结论

阶段 00 已经足够解锁两个并行方向：

- `01-SLAM-建图与定位`：基于 `/scan` 和 `/odom`，先解决 TF 命名和激光 frame 问题。
- `04-视觉旗帜检测`：先给 SDF 机器人模型增加 RGB camera，再桥接图像 topic，最后检测红色旗面。

推荐先推进 `01-SLAM-建图与定位`，因为自主探索和后续靠近旗帜都依赖地图、定位和导航能力。
