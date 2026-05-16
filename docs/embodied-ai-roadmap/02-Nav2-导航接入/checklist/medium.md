# Medium 验收：功能完整

- `ros2 launch kibot_one_sim nav2.launch.py` 能启动 Gazebo、bridge、SLAM 和 Nav2。
- Nav2 lifecycle nodes 能进入 active。
- `/navigate_to_pose` action 存在。
- `/local_costmap/costmap` 和 `/global_costmap/costmap` 有数据。
- RViz 中能看到地图、激光、局部 costmap、全局 costmap 和机器人姿态。
- 发送一个短距离目标后，Nav2 能规划路径并向 `/cmd_vel_smoothed` 发布速度。
- `/cmd_vel_smoothed` 已桥接到 Gazebo `/model/kibot_one_base/cmd_vel`，目标执行后 `/odom` 应实际变化。
- 目标失败、取消或超时时，有清晰日志或 action result 可供阶段 03 使用。
