# 控制权归属

## 源码已确认

当前旧控制链路是：

```text
mode_control / follow_controller / keyboard_teleop
  -> /cmd_vel_raw
  -> cmd_vel_watchdog
  -> /cmd_vel
  -> ros_gz_bridge
  -> /model/kibot_one_base/cmd_vel
  -> Gazebo DiffDrive
```

阶段 02 新增的 Nav2 链路是：

```text
Nav2 controller / behavior
  -> cmd_vel_nav
  -> velocity_smoother
  -> cmd_vel_smoothed
  -> ros_gz_bridge
  -> /model/kibot_one_base/cmd_vel
  -> Gazebo DiffDrive
```

`nav2.launch.py` 不启动旧控制节点，因此阶段 02 运行时 Gazebo 运动来源应是 Nav2 的 `/cmd_vel_smoothed`。

## 已运行时确认

- `collision_monitor` 在当前配置下不会稳定把 `/cmd_vel_smoothed` 转发成 `/cmd_vel`。
- Gazebo bridge 已改为订阅 `/cmd_vel_smoothed`。
- 发送 0.5m `NavigateToPose` 目标后，Gazebo `/odom` 从接近 `0` 前进到约 `0.42m`。

## 后续约束

进入任务状态机阶段时，旧模式系统可以复用“控制权互斥”的思想，但不应让 FOLLOW 和 Nav2 同时控制 Gazebo `/model/kibot_one_base/cmd_vel`。如果要同时支持手动 `/cmd_vel` 和 Nav2，需要新增显式 mux，而不是让多个 bridge 抢同一个 Gazebo topic。
