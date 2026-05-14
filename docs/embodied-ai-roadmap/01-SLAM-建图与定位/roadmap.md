# 阶段 01：SLAM 建图与定位路线图

## 阶段定位

本阶段承接 `00-系统基线`，目标是让当前 Gazebo 仿真小车具备基础 SLAM 建图与定位能力。

当前系统已经有 `/scan` 和 `/odom`，因此本阶段的主线不是重新设计机器人，而是基于现有激光雷达和里程计，接入 `slam_toolbox`，建立后续 Nav2 可依赖的地图与 TF 链路。

## 阶段目标

完成本阶段后，系统应具备：

- 能启动 Gazebo 仿真和 SLAM。
- 能发布 `/map`。
- 能形成可用的 `map -> odom -> base_link -> lidar_link` 或等价 TF 链路。
- 能在 RViz 中看到地图、激光和机器人位置关系。
- 能为 `02-Nav2-导航接入` 提供明确输入条件。

## 采用方案

本阶段采用：

- SLAM 工具：`slam_toolbox`。
- SLAM 输入：`/scan`。
- 里程计输入：当前 Gazebo bridge 提供的 `/odom`。
- 第一版验证环境：优先使用 `kibot_one_obstacles.world.sdf`。
- 可视化工具：RViz。

## TF 策略

目标 TF 链路优先采用：

```text
map -> odom -> base_link -> lidar_link
```

但当前 Gazebo 模型的机器人基座 link 是 `base_link`。因此本阶段采用一个务实策略：

- 第一优先：引入 `base_link`，让后续 SLAM / Nav2 配置贴近 ROS 常见约定。
- 如果引入 `base_link` 会导致 TF 冲突，则第一版允许先使用 `base_link` 作为 SLAM 的 `base_frame`。
- 不管采用哪种方式，都必须保证 `/scan` 能从 `lidar_link` 转换到机器人基座 frame。

也就是说，本阶段可以先跑通，但不能让 TF 关系保持含糊。

## 实施路线

### 01.1 运行时确认当前 TF 与传感器

确认 `/scan`、`/odom`、`/tf` 的实际运行情况，尤其是：

- `/scan.header.frame_id`
- `/odom.header.frame_id`
- `/odom.child_frame_id`
- TF tree 中是否存在 `base_link -> lidar_link`

产出记录到：

- `runtime-checklist.md`
- `tf-plan.md`

### 01.2 确定并补齐 TF 链路

根据运行时结果确定使用 `base_link` 还是 `base_link`。

推荐方向：

- 如果可以干净地补齐 `base_link`，则使用 `base_link`。
- 如果当前 Gazebo DiffDrive 已稳定发布 `odom -> base_link`，且短期不想改动模型，则先让 `slam_toolbox` 使用 `base_link`。

补齐方式优先使用 launch 中的 static transform，不急于重构 SDF 或引入完整 URDF。

### 01.3 增加 SLAM 启动与配置

新增最小 SLAM bringup：

- 一个 SLAM launch 文件。
- 一个 `slam_toolbox` 参数文件。

第一版只追求链路跑通，不追求参数最优。

### 01.4 RViz 验证

用 RViz 验证：

- `/map` 是否显示。
- `/scan` 是否和机器人位置对齐。
- 机器人移动时地图是否更新。
- TF 是否连续、无明显冲突。

### 01.5 输出 Nav2 前置条件

本阶段结束时，要明确给阶段 02 提供：

- `global_frame` 使用什么。
- `odom_frame` 使用什么。
- `robot_base_frame` 使用什么。
- obstacle layer 使用哪个 scan topic。
- Nav2 控制输出是否直接使用 `/cmd_vel`。

## 本阶段不做

本阶段不处理：

- Nav2。
- 自主探索。
- 相机或视觉检测。
- 旗帜位置估计。
- mission state machine。
- 旧 FOLLOW 控制器重构。

`/flag_pose` 可以继续存在，但不参与本阶段设计。

## 阶段完成条件

本阶段完成时应满足：

- `slam_toolbox` 能随仿真启动。
- `/map` 正常发布。
- `map -> odom` 正常发布。
- 机器人基座 frame 与 `lidar_link` 之间 TF 可用。
- RViz 中地图、激光和机器人位置关系基本正确。
- 已记录阶段 02 接入 Nav2 所需 frame 和 topic。

## 后续阶段

完成本阶段后进入：

```text
02-Nav2-导航接入
```

如果当前 world 不适合持续建图，再补一个小阶段处理封闭探索环境，不把环境设计混入本阶段。
