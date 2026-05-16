# 04-验证 lifecycle 与目标入口

## 本节目标

确认 Nav2 已经启动到可接收目标的状态。

## 为什么现在做

阶段 03 只应依赖清晰的 Nav2 action 契约。如果 02 没有确认 lifecycle、action 和 costmap，frontier 探索会把问题混在一起，后续难以定位。

## 需要参考

- `../checklist/low.md`
- `../checklist/medium.md`
- `../evidence/validation-log.md`

## 具体做法

先检查运行依赖：

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

启动：

```bash
ros2 launch kibot_one_sim nav2.launch.py
```

检查 lifecycle：

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

检查 action：

```bash
ros2 action list | grep navigate_to_pose
ros2 action info /navigate_to_pose
```

检查 costmap：

```bash
ros2 topic list | grep costmap
ros2 topic echo /local_costmap/costmap --once
ros2 topic echo /global_costmap/costmap --once
```

发送一个短距离目标前，先在 RViz 中确认地图、激光和机器人姿态大体对齐。

发送目标后确认速度和里程计：

```bash
ros2 topic echo /cmd_vel_smoothed --once
ros2 topic echo /odom --once
```

## 做完应该看到什么

- `controller_server`、`planner_server`、`bt_navigator` 处于 active。
- `/navigate_to_pose` 存在。
- 发送目标后 Nav2 返回 `SUCCEEDED`，或给出明确失败原因。
- `/cmd_vel_smoothed` 有 Nav2 输出。
- `/odom` 能证明 Gazebo 中机器人实际移动。

## 下一节

进入 `05-交付阶段-03-契约.md`。
