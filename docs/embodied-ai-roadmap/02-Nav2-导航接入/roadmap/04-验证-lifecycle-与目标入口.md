# 04-验证点到点导航闭环

## 本节目标

本节验证的不是“launch 进程还活着”，而是完整闭环：

```text
Nav2 lifecycle active
  -> /navigate_to_pose 接收目标
  -> controller 输出 /cmd_vel_smoothed
  -> bridge 驱动 Gazebo
  -> /odom 证明机器人移动
  -> map -> base_link 证明接近 map 目标
```

本节的详细操作手册在：

```text
../evidence/usage.md
```

这里解释每一步为什么要做，以及每个检查点失败时代表什么。

## 为什么现在做

阶段 03 的 frontier 探索只应该处理“选哪个目标”。如果阶段 02 没有先证明点到点导航闭环成立，阶段 03 的失败就会混在 SLAM、Nav2、bridge、TF 和目标选择之间。

本节需要参考：

- `../evidence/usage.md`
- `../checklist/low.md`
- `../checklist/medium.md`

## 第一步：先证明依赖可用

启动前先运行：

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

这个脚本不是形式检查。它会先确认 ROS 发行版：

```bash
if [[ "${ROS_DISTRO:-}" != "jazzy" ]]; then
  echo "[error] 请先 source ROS2 Jazzy 环境，例如：source .vscode/project-terminal-init.sh"
  missing=1
fi
```

这里的 `${ROS_DISTRO:-}` 是 shell 参数展开。如果 `ROS_DISTRO` 不存在，就用空值，避免脚本因为 `set -u` 直接退出。

接下来脚本检查关键 ROS package：

```bash
required_packages=(
  nav2_bringup
  nav2_controller
  nav2_planner
  nav2_bt_navigator
  nav2_msgs
  slam_toolbox
  ros_gz_bridge
)
```

这些包分别对应本阶段的启动入口、controller、planner、行为树 action、消息类型、SLAM 和 Gazebo bridge。

最后检查 FastCDR 符号：

```bash
fastcdr_lib="/opt/ros/jazzy/lib/libfastcdr.so.2"
fastcdr_symbols="$(nm -D "${fastcdr_lib}" 2>/dev/null | c++filt)"
if [[ "${fastcdr_symbols}" == *"eprosima::fastcdr::Cdr::serialize(unsigned int)"* ]]; then
  echo "[ok] ${fastcdr_lib} exports Cdr::serialize(unsigned int)"
else
  echo "[error] ${fastcdr_lib} 缺少 Cdr::serialize(unsigned int)，Nav2 controller_server 会在运行时崩溃。"
fi
```

这一步是为了提前发现运行库不一致。它失败时，不要继续看 YAML。

## 第二步：启动前清理旧进程

先检查是否有旧仿真：

```bash
pgrep -af 'ros2 launch kibot_one_sim nav2.launch.py|gz sim|ros_gz_bridge|bridge_node|controller_server|planner_server|bt_navigator|slam_toolbox'
```

预期没有输出。

如果这里还有旧 `gz sim` 或 `bridge_node`，后面 `/clock` 可能出现多个 publisher。多个 `/clock` 会导致 TF 时间回跳，表现为 Nav2 偶发失败。

## 第三步：启动完整环境

启动：

```bash
ros2 launch kibot_one_sim nav2.launch.py use_rviz:=false
```

先不用 RViz，是为了减少验证变量。这个终端保持运行。

在另一个终端加载环境：

```bash
source .vscode/project-terminal-init.sh
source install/setup.bash
```

如果 launch 直接报 FastCDR 依赖错误，回到第一步修依赖。

## 第四步：检查仿真时间只有一个来源

运行：

```bash
ros2 topic info /clock
```

预期：

```text
Publisher count: 1
```

这一步看起来很小，但很关键。Nav2、SLAM 和 TF 都依赖时间一致性。如果 `/clock` 有多个 publisher，后续所有行为都不可信。

## 第五步：检查 Nav2 lifecycle

先检查 controller：

```bash
ros2 lifecycle get /controller_server
```

再检查 planner：

```bash
ros2 lifecycle get /planner_server
```

最后检查行为树 navigator：

```bash
ros2 lifecycle get /bt_navigator
```

预期都返回：

```text
active [3]
```

`active [3]` 表示 lifecycle manager 已经把节点激活。节点存在但不是 active 时，action 可能存在，但不能稳定执行目标。

## 第六步：检查 action 入口

先确认 action 名称：

```bash
ros2 action list | grep navigate_to_pose
```

应该看到：

```text
/navigate_to_pose
```

再看 action 信息：

```bash
ros2 action info /navigate_to_pose
```

这一步确认的是阶段 03 将来要依赖的入口，而不是 Nav2 内部实现。

## 第七步：检查速度链路

阶段 02 的 Gazebo 速度入口是 `/cmd_vel_smoothed`。检查 bridge 是否订阅它：

```bash
ros2 topic info /cmd_vel_smoothed -v
```

你应该能看到类似：

```text
Node name: kibot_one_bridge
Endpoint type: SUBSCRIPTION
```

如果 bridge 没有订阅 `/cmd_vel_smoothed`，机器人可能不会动，即使 Nav2 controller 正在输出速度。

不要用 `/cmd_vel` 判断本阶段是否正常。旧系统使用 `/cmd_vel`，阶段 02 的 Nav2 验收使用 `/cmd_vel_smoothed`。

## 第八步：发送最小目标

先发一个近距离目标：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

这里的 `frame_id: map` 很重要。它表示 `(0.5, 0.0)` 是地图坐标，不是相对机器人当前位置的“向前 0.5m”。

预期结果：

```text
Goal accepted
Goal finished with status: SUCCEEDED
error_code: 0
```

如果是 `ABORTED`，不要把本阶段记为通过。先看日志里是 planner 失败、controller 失败，还是 TF/clock 问题。

## 第九步：用 odom 证明机器人真的动了

目标完成后读取：

```bash
ros2 topic echo /odom --once
```

`/odom` 用来证明 Gazebo 里的机器人实际移动。历史上出现过“action 看起来成功，但机器人没动”的假象，所以这一步必须保留。

但 `/odom` 不是 `map` 坐标。不要把 `/odom.pose.pose.position.x` 直接和目标 `map.x` 相减。

## 第十步：用 TF 证明接近 map 目标

目标误差要看：

```bash
ros2 run tf2_ros tf2_echo map base_link
```

对于 `(0.5, 0.0)`，`Translation` 应接近：

```text
x: 0.5
y: 0.0
```

允许误差来自 `nav2_params.yaml` 里的 goal checker：

```yaml
general_goal_checker:
  xy_goal_tolerance: 0.10
  yaw_goal_tolerance: 0.25
```

也就是说，平面距离误差约 `0.10m` 内是合理的。

## 第十一步：理解 105 不是启动失败

如果你发送远端目标，比如：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 5.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

可能看到：

```text
Goal finished with status: ABORTED
error_code: 105
```

`105` 对应 `FollowPath` 的 `FAILED_TO_MAKE_PROGRESS`。这表示目标进入了路径跟随阶段，但机器人没有稳定取得进展。

这不是：

- action server 没启动。
- lifecycle 没 active。
- Nav2 依赖缺失。

它是目标执行边界问题。阶段 02 不把穿过障碍物带的远端绝对坐标作为通过标准。

## 做完应该看到什么

本节通过时，你应该能同时证明：

- `/clock` publisher count 是 `1`。
- Nav2 lifecycle nodes 是 `active [3]`。
- `/navigate_to_pose` 存在。
- `/cmd_vel_smoothed` 有 `kibot_one_bridge` subscriber。
- 近距离 `map` 目标返回 `SUCCEEDED`。
- `/odom` 显示机器人实际移动。
- `map -> base_link` 接近目标坐标。

## 本节小结

本节把“Nav2 已接入”拆成了可观察事实。阶段 03 不需要重新证明这些底层链路，只需要依赖 `/navigate_to_pose` 的成功、失败、取消和超时语义。
