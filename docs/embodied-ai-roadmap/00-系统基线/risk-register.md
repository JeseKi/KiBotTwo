# 阶段 00：风险记录

## 风险总览

| 编号 | 风险 | 影响阶段 | 严重程度 | 当前判断 | 后续处理 |
| --- | --- | --- | --- | --- | --- |
| R-00-001 | 当前没有 `base_link`，机器人基座 frame 是 `chassis` | SLAM / Nav2 | 高 | 源码确认 | 阶段 01 设计 frame 适配 |
| R-00-002 | `chassis -> lidar_link` 的 ROS TF 可能不存在 | SLAM | 高 | SDF 有 fixed joint，但 ROS TF 待运行确认 | 阶段 01 优先确认并补齐 |
| R-00-003 | 当前没有 `map` frame | SLAM / Nav2 / 探索 | 高 | 源码确认 | 由 SLAM 引入 `map -> odom` |
| R-00-004 | 当前没有相机 | 视觉检测 | 高 | 源码确认 | 阶段 04 先增加 camera sensor 和 bridge |
| R-00-005 | 当前 `/flag_pose` 是 Gazebo 真值 | 任务目标 | 高 | 源码确认 | 后续 mission 不应消费该 topic 作为任务输入 |
| R-00-006 | 多控制源可能冲突 | Nav2 / 状态机 | 高 | 当前已有多个 `/cmd_vel_raw` 发布者 | 阶段 02 / 06 设计控制权互斥 |
| R-00-007 | 当前 FOLLOW 是局部控制，不是全局导航 | Nav2 / 探索 | 中 | 源码确认 | 不应直接扩展为探索导航 |
| R-00-008 | 当前世界不是封闭探索环境 | 探索 | 中 | world 主要是地面和障碍物 | 后续需要新建或调整探索 world |
| R-00-009 | 旗帜与环境都可能进入 lidar 地图 | SLAM / 任务语义 | 中 | 旗帜是 Gazebo 静态模型 | 后续需决定旗帜是否作为障碍物保留 |
| R-00-010 | 没有 depth camera，旗帜 3D 定位能力不足 | 旗帜位置估计 | 中 | 源码确认 | 阶段 05 决定单目、深度或发现即停止 |

## 关键风险说明

### R-00-001：缺少 `base_link`

当前 Gazebo DiffDrive 配置为：

```text
frame_id: odom
child_frame_id: chassis
```

Nav2 和常见 SLAM 配置通常围绕 `base_link` 或 `base_footprint`。如果不处理，后续参数配置会变得混乱。

处理方向：

- 接受 `chassis` 作为 base frame，并在所有配置中显式使用。
- 或引入 `base_link`，并建立 `base_link -> chassis` / `chassis -> base_link` 的清晰关系。

### R-00-002：激光雷达 TF 待确认

SDF 中有：

```text
chassis -> lidar_link
```

但当前 ROS bridge 主要桥接 `/tf`，来源是 DiffDrive 的 `/model/kibot_one_base/tf`。SDF fixed joint 是否会出现在 ROS TF tree，需要运行时确认。

如果不存在，`slam_toolbox` 将无法把 `/scan` 从 `lidar_link` 转换到机器人基座 frame。

### R-00-005：旗帜位姿是真值输入

当前 `/flag_pose` 是 Gazebo 模型位姿，不是传感器观测。

后续自主任务必须避免 mission 直接消费 `/flag_pose`。

建议把 `/flag_pose` 降级为 debug / 对照信息。

### R-00-006：控制源冲突

当前可能发布 `/cmd_vel_raw` 的节点包括：

- `mode_control`
- `follow_controller`
- `keyboard_teleop`
- `control_console`

Nav2 通常直接发布 `/cmd_vel`。如果直接接入 Nav2，同时保留现有控制节点，可能出现速度命令互相覆盖。

需要在阶段 02 或阶段 06 明确控制权：

```text
MANUAL / FOLLOW_LEGACY / NAV2 / STOP
```

同一时刻只能有一个控制源生效。

## 已排除风险

| 编号 | 风险 | 排除理由 |
| --- | --- | --- |
| R-00-X01 | 完全没有 SLAM 输入传感器 | 当前已有 `/scan` 和 `/odom` |
| R-00-X02 | 旗帜无法被视觉区分 | 当前旗帜模型有红色旗面，适合第一版颜色检测 |
| R-00-X03 | 没有速度控制入口 | 当前 `/cmd_vel` 已桥接到 Gazebo DiffDrive |

## 后续优先级

最高优先级：

- 解决 TF 基线问题。
- 确认是否采用 `chassis` 作为 base frame。
- 禁止后续 mission 直接依赖 `/flag_pose`。

第二优先级：

- 增加 camera。
- 建立 Nav2 控制权互斥。
- 设计封闭探索 world。
