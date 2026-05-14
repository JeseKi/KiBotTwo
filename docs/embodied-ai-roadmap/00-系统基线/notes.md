# 阶段 00：记录与复盘

## 当前结论

当前项目是一个完成度较高的 Gazebo 目标跟随仿真，但还不是自主探索系统。

它已经具备：

- Gazebo 机器人模型。
- 差速驱动。
- 2D 激光雷达。
- 里程计。
- ROS-Gazebo bridge。
- 基础模式控制。
- 速度命令看门狗。
- 基于真值旗帜位姿的 FOLLOW 控制。

它暂时不具备：

- 相机。
- SLAM。
- Nav2。
- 地图。
- 自主探索。
- 视觉旗帜检测。
- 旗帜位置估计。

## 已确认事实

- 主启动入口是 `ros2 launch kibot_one_sim kibot_one.launch.py`。
- 当前桥接配置在 `src/kibot_one_sim/config/ros_gz_bridge.yaml`。
- `/cmd_vel` 桥接到 Gazebo `/model/kibot_one_base/cmd_vel`。
- `/odom` 来自 Gazebo `/model/kibot_one_base/odometry`。
- `/scan` 来自 Gazebo lidar。
- `/flag_pose` 来自 Gazebo `/model/follow_flag/pose`。
- `/robot_pose` 来自 Gazebo `/model/kibot_one_base/pose`。
- 当前机器人模型文件是 `src/kibot_one_sim/models/kibot_one_base/model.sdf`。
- 当前旗帜模型文件是 `src/kibot_one_sim/models/follow_flag/model.sdf`。
- 当前旗帜红色旗面尺寸约为 `0.30 x 0.02 x 0.20`。
- 当前机器人基座 link 名是 `chassis`。
- 当前激光雷达 link 名是 `lidar_link`。
- 当前没有 camera sensor。

## 尚需运行时确认的问题

- `/tf` 实际是否只包含 `odom -> chassis`。
- `/scan` 的 frame_id 是否稳定为 `lidar_link`。
- ROS 侧是否存在 `chassis -> lidar_link`。
- `/robot_pose` 和 `/flag_pose` 的 header stamp / frame 是否符合 bridge 配置。
- 当前 FOLLOW 模式在障碍物世界中的稳定性。

## 设计取舍建议

### 关于 SLAM 优先级

建议先做 SLAM，再做视觉。

原因：

- 自主探索依赖地图和定位。
- Nav2 依赖稳定 TF。
- 视觉发现旗帜之后，如果没有导航和地图，最多只能做到“发现即停止”。

### 关于 `base_link`

建议阶段 01 明确 frame 策略，不要边调 SLAM 边猜。

可选方向：

- 方案 A：继续使用 `chassis` 作为机器人 base frame，所有 SLAM / Nav2 参数显式配置为 `chassis`。
- 方案 B：引入标准 `base_link`，让 `base_link` 成为后续算法配置的中心 frame。

更推荐方案 B，因为它更接近 ROS 生态默认约定。

### 关于旧 FOLLOW 逻辑

建议保留旧 `follow_controller` 作为对照实验，不要立即删除。

但后续自主任务不应继续扩展这个节点。原因是它已经把目标真值、局部避障和速度控制耦合在一起，不适合作为探索 + 视觉 + 导航任务的中心。

### 关于 `/flag_pose`

建议后续保留 `/flag_pose` 作为 debug 真值，不作为 mission 输入。

新任务输入应该来自：

```text
/flag_detection
/flag_estimated_pose
```

## 下一阶段建议

推荐进入：

```text
01-SLAM-建图与定位
```

阶段 01 的第一步不应该是直接写 launch，而应该先设计目标 TF：

```text
map -> odom -> base_link -> lidar_link
```

然后决定当前的 `chassis` 如何映射到 `base_link`。
