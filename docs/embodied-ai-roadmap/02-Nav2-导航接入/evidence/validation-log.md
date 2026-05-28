# 验证记录

## 当前结论

阶段 02 的成品分支已通过运行时验收：

- Nav2 / FastCDR 运行依赖检查通过。
- Gazebo、ros_gz_bridge、slam_toolbox 和 Nav2 可由 `nav2.launch.py` 一起启动。
- `/clock` 只有一个 publisher，未再出现 TF 时间回跳。
- Nav2 lifecycle nodes 自动进入 `active`。
- `/navigate_to_pose` action 可用。
- global costmap 使用 rolling obstacle/inflation 配置，不再被 SLAM 初始小地图边界阻塞。
- Nav2 速度经 `/cmd_vel_smoothed` 桥接到 Gazebo，`/odom` 实际前进。

文档复测结论已收紧：

- 旧记录证明过成品分支 runtime 可用，但不足以证明“只按文档手写就能生成完全一致的 runtime diff”。
- 从 2026-05-28 起，阶段 02 文档复测必须先通过 `evidence/reference-runtime.patch` 的完全一致审计，再进入 runtime 验收。
- runtime 文件相对 baseline 的 patch 只要与 `reference-runtime.patch` 有任何差异，即使短目标运行成功，也不能宣称文档复测通过。

## 已执行

## 2026-05-28 文档复测规则修复

本轮复核发现，之前的文档复测在失败后参考了 `feat/02-Nav2-导航接入` 修复 runtime 问题，但没有再从干净 baseline 出发，只按修正后的文档重新生成 runtime 文件并与成品分支做完全一致审计。

因此补充：

- 新增 `evidence/reference-runtime.patch`，记录共同 baseline `e9b6fa40f7b269d098611b64f983d914f916b84e` 到 `feat/02-Nav2-导航接入` 的阶段 02 runtime 完整 patch。
- 新增 `reference/final-runtime/`，保存成品分支 runtime 文件的 `.bak` 完整副本，用于逐文件核对最终合并结果。
- `evidence/usage.md` 增加 runtime patch 完全一致审计步骤。
- `roadmap/index.md`、`roadmap/02-增加-Nav2-参数.md` 和 `roadmap/03-增加-Nav2-启动入口.md` 明确：runtime 文件必须与成品分支完全一致，只有 `docs/` 下的差异可以不同。
- `reference/file-plan.md` 记录成品一致性边界和需要完全一致的 runtime 文件清单。

这次修复没有重新宣称文档复测已经通过；它修正的是复测通过标准。后续复测必须从 baseline 重做，并让生成的 runtime patch 与 `reference-runtime.patch` 无差异。

## 2026-05-25 文档实操复核与修复

按 roadmap 手写代码后，首次完整启动卡在：

```text
[collision_monitor]: Error while getting parameters: parameter 'observation_sources' is not initialized
[lifecycle_manager_navigation]: Failed to bring up all requested nodes. Aborting bringup.
```

同时发现 `run_on_start` 只在 `nav2.launch.py` 声明，未在 `sim_with_bridge.launch.py` / `gazebo.launch.py` 中透传到 `gz sim -r`。

参考 `feat/02-Nav2-导航接入` 后修复：

- `collision_monitor` 增加 `observation_sources: ["scan"]` 和 `scan` source。
- `nav2_params.yaml` 补齐 Jazzy bringup 管理的辅助 lifecycle nodes 参数。
- `gazebo.launch.py` 增加 `run_on_start` 参数，按条件启动 `gz sim` 或 `gz sim -r`。
- `sim_with_bridge.launch.py` 透传 `run_on_start`。
- `CMakeLists.txt` 安装 `scripts/`。
- roadmap 和 usage 文档补齐上述步骤。

验证命令：

```bash
source .vscode/project-terminal-init.sh
python3 -m py_compile \
  src/kibot_one_sim/launch/nav2.launch.py \
  src/kibot_one_sim/launch/gazebo.launch.py \
  src/kibot_one_sim/launch/sim_with_bridge.launch.py
python3 - <<'PY'
import yaml
from pathlib import Path
yaml.safe_load(Path('src/kibot_one_sim/config/nav2_params.yaml').read_text())
print('yaml ok')
PY
colcon build --packages-select kibot_one_sim
source install/setup.bash
ros2 launch kibot_one_sim nav2.launch.py --show-args
ros2 launch kibot_one_sim nav2.launch.py use_rviz:=false
```

运行时检查：

- `gz sim` 进程包含 `-r`。
- `/clock` publisher count 为 `1`。
- `controller_server`、`planner_server`、`bt_navigator`、`velocity_smoother`、`collision_monitor` 均为 `active [3]`。
- `/navigate_to_pose` 和 `/navigate_through_poses` action 可见。
- `/cmd_vel_smoothed` 有 `velocity_smoother` publisher 和 `kibot_one_bridge` subscriber。

短距离目标：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

结果：

```text
Goal finished with status: SUCCEEDED
error_code: 0
```

目标完成后：

- `/odom.pose.pose.position.x`: `0.4221665850315707`
- `map -> base_link Translation`: `[0.412, 0.019, 0.000]`

本轮验证中并行执行多个 ROS2 CLI 时曾出现 daemon/发现缓存短暂不一致。重启 daemon 后串行检查恢复稳定：

```bash
ros2 daemon stop
ros2 daemon start
```

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
colcon build --packages-select kibot_one_sim
```

结果：通过。`colcon` 仍提示当前 workspace 已经在 underlay 中构建过 `kibot_one_sim`，未阻塞构建。

```bash
source .vscode/project-terminal-init.sh
source install/setup.bash
ros2 launch kibot_one_sim nav2.launch.py --show-args
```

结果：通过。已确认 `world`、`params_file`、`use_sim_time`、`use_composition`、`start_sim`、`run_on_start`、`start_slam`、`start_nav2`、`use_rviz`、`check_runtime_deps` 等参数可见。

```bash
source .vscode/project-terminal-init.sh
source install/setup.bash
ros2 launch kibot_one_sim nav2.launch.py use_rviz:=false
```

运行时检查结果：

- `/clock` publisher count: `1`
- `controller_server`: `active [3]`
- `planner_server`: `active [3]`
- `bt_navigator`: `active [3]`
- `waypoint_follower`: `active [3]`
- `/cmd_vel_smoothed` 有 `kibot_one_bridge` subscriber
- 启动日志未出现 `Detected jump back in time`、`TF_OLD_DATA`、`Robot is out of bounds`、`Error advertising topic`

实际目标执行：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

结果：

```text
Goal finished with status: SUCCEEDED
error_code: 0
```

里程计验证：

- 初始 `odom.pose.pose.position.x`: `5.468872581415822e-17`
- 目标执行后 `odom.pose.pose.position.x`: `0.4219161459857354`

`/odom` 只证明机器人实际移动。`NavigateToPose` 使用 `frame_id: map` 时，目标误差应通过 `ros2 run tf2_ros tf2_echo map base_link` 判读，不能直接把 `/odom` 的 `x/y` 与 `map` 目标坐标相减。

Nav2 日志关键行：

```text
controller_server: Received a goal, begin computing control effort.
controller_server: Reached the goal!
bt_navigator: Goal succeeded
```

## 2026-05-16 边界复核：`map` 坐标 `(5.0, 0.0)`

用户报告：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

结果为：

```text
Goal finished with status: ABORTED
error_code: 105
```

复核结论：

- `105` 对应 `nav2_msgs/action/FollowPath` 的 `FAILED_TO_MAKE_PROGRESS`。
- 这说明目标已经进入路径跟随阶段；不是 action server 不存在，也不是 Nav2 lifecycle 未激活。
- `frame_id: map` 下的 `(5.0, 0.0)` 是绝对地图坐标，不是相对机器人当前位置向前 5m。
- 默认 `kibot_one_obstacles.world.sdf` 中，`x≈1.10,y≈0.10` 和 `x≈2.45,y≈0.10` 附近有箱体障碍，`(5.0, 0.0)` 位于障碍物带后方，属于压力/边界目标。

实际复核记录：

- 干净启动后，`(0.5, 0.0)` 返回 `SUCCEEDED`，证明阶段 02 的低层接入仍然可用。
- 干净启动后直接发送 `(5.0, 0.0)`，曾观察到最终 `SUCCEEDED`，耗时约 175 秒；日志中多次出现 `Failed to make progress`、`[follow_path] [ActionServer] Aborting handle`、`Running spin`，最终 `bt_navigator: Goal succeeded`。
- 再次验证时，调宽 progress checker 只能推迟第一次 `Failed to make progress`，没有证明该远端目标稳定；该调参已回退，避免把未验证改动留在系统中。

主线文档中的系统预期状态和完成边界见 `../roadmap/index.md`。本节只保留这次复核的证据。

## 已修复的问题

依赖问题：

- 旧 `ros-jazzy-fastcdr 2.2.5` 缺少 `eprosima::fastcdr::Cdr::serialize(unsigned int)`，会导致 Nav2 FastRTPS 类型支持运行时崩溃。
- 用户重新安装依赖后，`ros-jazzy-fastcdr 2.2.7` 导出该符号。
- `check_nav2_runtime_deps.sh` 已修复 `pipefail + grep -q` 导致的误报。

时间问题：

- 旧验证残留了多个 `gz sim` / `bridge_node` 进程，造成 `/clock` 多 publisher 和 TF 时间回跳。
- 干净启动后 `/clock` publisher count 为 `1`。

规划问题：

- SLAM 初始 `/map` 过小，静态 global costmap 会把机器人判定为地图外或让目标落在 unknown 区域。
- global costmap 改为 `rolling_window: true`、`width: 20`、`height: 20`。
- global costmap 移除 `static_layer`，保留 `obstacle_layer` 和 `inflation_layer`，用于探索目标执行。
- planner tolerance 从 `0.5` 收紧到 `0.10`，goal checker `xy_goal_tolerance` 从 `0.25` 收紧到 `0.10`，避免近距离目标被容差假阳性吞掉。

控制链路问题：

- Nav2 实际非零速度出现在 `/cmd_vel_smoothed`。
- Gazebo bridge 原先只接 `/cmd_vel`，导致 Nav2 有速度但机器人不动。
- 当前 bridge 改为 `/cmd_vel_smoothed -> /model/kibot_one_base/cmd_vel`。

## 历史阻塞

最初完整启动时曾出现：

```text
symbol lookup error:
/opt/ros/jazzy/lib/libnav2_msgs__rosidl_typesupport_fastrtps_cpp.so:
undefined symbol: eprosima::fastcdr::Cdr::serialize(unsigned int)
```

这不是 YAML 参数问题，而是本机 Jazzy deb 包版本组合不一致。教程中的 `reference/dependencies.md` 已加入依赖安装和检查说明。
