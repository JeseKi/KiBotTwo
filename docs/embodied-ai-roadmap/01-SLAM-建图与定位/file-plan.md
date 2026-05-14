# 阶段 01：文件计划

## 文件计划定位

本文件只说明阶段 01 预计会涉及哪些文件，以及每类文件负责什么。

具体参数值、完整代码和调试细节不在这里展开，进入实现时再根据运行时确认结果补充。

## 文档文件

本阶段已有文档：

- `roadmap.md`：阶段路线和采用方案。
- `acceptance.md`：阶段完成标准。
- `file-plan.md`：文件组织和改动边界。
- `tf-plan.md`：TF 目标链路和决策记录。
- `runtime-checklist.md`：运行时确认记录。
- `notes.md`：阶段结论、调试记录和复盘。

## 推荐新增功能文件

第一版建议把 SLAM 相关文件先放在 `kibot_one_sim` 中。

原因：

- 当前仿真 bringup 已经集中在 `kibot_one_sim`。
- 阶段 01 的目标是跑通 SLAM 链路，不是重构 package 分层。
- 等阶段 02 接入 Nav2 时，再考虑是否拆出 `kibot_one_navigation`。

推荐新增：

| 文件 | 作用 |
| --- | --- |
| `src/kibot_one_sim/launch/slam.launch.py` | 启动 `slam_toolbox`，必要时同时启动静态 TF |
| `src/kibot_one_sim/config/slam_toolbox.yaml` | 保存 SLAM 参数，例如 frame 名、scan topic、建图模式 |
| `src/kibot_one_sim/rviz/slam.rviz` | 可选，保存 SLAM 验证用 RViz 配置 |

## 可能修改的文件

| 文件 | 修改原因 |
| --- | --- |
| `src/kibot_one_sim/CMakeLists.txt` | 安装新增的 `config`、`rviz` 或 launch 文件 |
| `src/kibot_one_sim/package.xml` | 如需要，声明 `slam_toolbox`、`tf2_ros` 等运行依赖 |
| `src/kibot_one_sim/launch/kibot_one.launch.py` | 可选：增加是否启动 SLAM 的 launch 参数 |

## 暂不建议修改的文件

| 文件 | 原因 |
| --- | --- |
| `src/kibot_one_control/kibot_one_control/follow_controller.py` | 阶段 01 不处理旗帜跟随逻辑 |
| `src/kibot_one_control/kibot_one_control/mode_control.py` | 阶段 01 不调整模式系统 |
| `src/kibot_one_control/kibot_one_control/cmd_vel_watchdog.py` | 阶段 01 不调整控制链路 |
| `src/kibot_one_sim/models/follow_flag/model.sdf` | 阶段 01 不处理旗帜模型 |
| `src/kibot_one_interface/*` | 阶段 01 不新增接口 |

## TF 相关实现提示

本阶段不要一开始就大改机器人模型。

优先顺序：

1. 先确认当前 TF 实际情况。
2. 如果缺少 `base_link -> lidar_link`，优先用 static transform 补齐。
3. 如果决定引入 `base_link`，优先在 launch 中补齐清晰的静态关系。
4. 只有当 launch 级 TF 方案无法满足后续 Nav2 时，再考虑改 SDF 或引入 URDF / Xacro。

## SLAM 配置提示

`slam_toolbox` 第一版配置只需要围绕这些核心项：

- `map_frame`
- `odom_frame`
- `base_frame`
- `scan_topic`
- 是否使用仿真时间 `use_sim_time`

不要在第一版过度调参。先让 `/map` 和 TF 链路稳定，再优化地图质量。

## 后续可能拆包

阶段 02 如果开始接入 Nav2，可以考虑新增：

```text
src/kibot_one_navigation
```

届时再迁移或集中管理：

- SLAM launch。
- Nav2 launch。
- Nav2 参数。
- RViz 配置。

阶段 01 不强制做这件事。
