# 使用与验证步骤

这份文档用于确认阶段 02 的 Nav2 接入是否真的可用。验收重点不是“进程能启动”，而是：

- Nav2 lifecycle active。
- `/clock` 没有多 publisher。
- `/navigate_to_pose` 可以接收目标。
- Gazebo 中机器人通过 `/odom` 证明实际移动。

## 1. 准备环境

在项目根目录执行：

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
colcon build --packages-select kibot_one_sim
source install/setup.bash
```

预期结果：

- 依赖检查输出 `Nav2 runtime dependencies look usable.`
- 构建成功，允许出现 `colcon` 的 override warning，但不能有 build failure。

如果依赖检查失败，先按 `../reference/dependencies.md` 安装或升级依赖，不要继续验证导航行为。

## 2. 确认没有残留仿真进程

```bash
pgrep -af 'ros2 launch kibot_one_sim nav2.launch.py|gz sim|ros_gz_bridge|bridge_node|controller_server|planner_server|bt_navigator|slam_toolbox'
```

预期结果：

- 没有输出。

如果有旧进程，先停止旧 launch 或清理残留进程。残留的 `gz sim` 或 `bridge_node` 会造成 `/clock` 多 publisher，导致 TF 时间回跳。

## 3. 启动 Nav2 验证环境

建议先不启动 RViz，减少变量：

```bash
ros2 launch kibot_one_sim nav2.launch.py use_rviz:=false
```

这个终端保持运行。后续命令在另一个终端执行，并同样先加载环境：

```bash
source .vscode/project-terminal-init.sh
source install/setup.bash
```

## 4. 检查基础状态

检查 `/clock`：

```bash
ros2 topic info /clock
```

预期结果：

```text
Publisher count: 1
```

检查 lifecycle：

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /waypoint_follower
```

预期结果：

```text
active [3]
```

检查 action：

```bash
ros2 action list | grep navigate_to_pose
```

预期结果：

```text
/navigate_to_pose
```

检查 Gazebo bridge 是否订阅 Nav2 速度：

```bash
ros2 topic info /cmd_vel_smoothed -v | grep -A2 'Node name: kibot_one_bridge'
```

预期结果：

- 能看到 `kibot_one_bridge`。
- Endpoint type 应为 `SUBSCRIPTION`。

## 5. 记录初始里程计

```bash
ros2 topic echo /odom --once
```

记录：

```text
pose.pose.position.x
```

刚启动时通常接近 `0`。

## 6. 发送短距离目标

发送一个 0.5m 的 `NavigateToPose` 目标：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

预期结果：

```text
Goal accepted
Result:
    error_code: 0
error_msg: ''

Goal finished with status: SUCCEEDED
```

如果 status 是 `ABORTED`，不要算通过。查看启动终端日志或 `~/.ros/log`，重点搜索：

```bash
grep -E 'GridBased plugin failed|Failed to make progress|Robot is out of bounds|Detected jump back in time|TF_OLD_DATA|Error advertising' ~/.ros/log/latest/*/*.log
```

## 7. 确认机器人实际移动

目标完成后再次读取 `/odom`：

```bash
ros2 topic echo /odom --once
```

对比前后的：

```text
pose.pose.position.x
```

预期结果：

- `x` 应明显大于初始值。
- 已验证样例中，`x` 从接近 `0` 前进到约 `0.42`。

只看到 action `SUCCEEDED` 还不够，必须同时看到 `/odom` 变化。之前出现过因 tolerance 过大导致的“假成功”，所以这里必须做里程计确认。

## 8. 可选：观察速度链路

目标执行过程中可以观察 Nav2 输出：

```bash
ros2 topic echo /cmd_vel_smoothed --once
```

预期结果：

- 执行中能看到非零 `linear.x` 或 `angular.z`。
- 当前 Gazebo bridge 使用 `/cmd_vel_smoothed -> /model/kibot_one_base/cmd_vel`。

不要用 `/cmd_vel` 判断阶段 02 是否正常。阶段 02 的 Gazebo 控制入口是 `/cmd_vel_smoothed`。

## 9. 通过标准

本探针响应符合预期，需要同时满足：

- 依赖检查通过。
- `/clock` publisher count 为 `1`。
- Nav2 lifecycle nodes 为 `active [3]`。
- `/navigate_to_pose` 存在。
- `/cmd_vel_smoothed` 有 `kibot_one_bridge` subscriber。
- 0.5m 目标返回 `SUCCEEDED`。
- `/odom.pose.pose.position.x` 明显前进。

任意一项失败，都不能宣称阶段 02 可用。优先根据失败点回查 `../evidence/validation-log.md` 中记录过的历史问题。

系统预期状态、完成边界和 `(5.0, 0.0)` 这类压力目标的判读，统一以 `../roadmap/index.md` 为准；本文件只保留具体操作步骤。

## 10. 收尾

验证完成后，在启动 launch 的终端按 `Ctrl+C`。

确认没有残留：

```bash
pgrep -af 'ros2 launch kibot_one_sim nav2.launch.py|gz sim|ros_gz_bridge|bridge_node|controller_server|planner_server|bt_navigator|slam_toolbox'
```

预期结果：

- 没有输出。
