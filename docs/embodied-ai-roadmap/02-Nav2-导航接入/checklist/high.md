# High 验收：集成级

- 从干净 baseline 只按本文档重做一遍，runtime patch 仍与 `evidence/reference-runtime.patch` 完全一致。
- 在 `kibot_one_obstacles.world.sdf` 中，机器人能到达至少三个不同方向的 RViz 目标点。
- costmap 膨胀半径和机器人半径不会让可通行区域被错误完全堵死。
- 机器人不会因为速度或加速度参数过大而明显震荡。
- 当目标在障碍物后方或不可达区域时，Nav2 能返回失败，而不是无限卡住。
- 在导航过程中停止 launch 后，Gazebo 中机器人不会继续保留非零速度。
- 阶段 03 的 action client 可以只依赖 `/navigate_to_pose`，不需要读取 Nav2 内部节点状态。
