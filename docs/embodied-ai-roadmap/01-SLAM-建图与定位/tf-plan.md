# 阶段 01：TF 方案

## 目标

为 SLAM、Nav2 和后续自主探索建立清晰、稳定、可解释的 TF 链路。

最终推荐目标：

```text
map -> odom -> base_link -> lidar_link
```

## 当前已知情况

来自阶段 00 的源码调查：

- Gazebo DiffDrive 配置：`frame_id = odom`。
- Gazebo DiffDrive 配置：`child_frame_id = base_link`。
- 机器人 SDF 中存在 `base_link` link。
- 机器人 SDF 中存在 `lidar_link` link。
- 机器人 SDF 中存在 `base_link -> lidar_link` fixed joint。
- 当前没有 `base_link`。
- 当前没有 `map`。

## 待运行时确认

| 项目 | 预期 | 实际结果 |
| --- | --- | --- |
| `/odom.header.frame_id` | `odom` | 待确认 |
| `/odom.child_frame_id` | `base_link` | 待确认 |
| `/scan.header.frame_id` | `lidar_link` | 待确认 |
| `/tf` 是否有 `odom -> base_link` | 是 | 待确认 |
| `/tf` 是否有 `base_link -> lidar_link` | 不确定 | 待确认 |
| 是否存在 `base_link` | 否 | 待确认 |
| 是否存在 `map` | 否 | 待确认 |

## 推荐方案

### 方案 B：引入 `base_link`

推荐目标链路：

```text
map
  -> odom
    -> base_link
      -> lidar_link
```

由于当前 Gazebo 发布的是 `odom -> base_link`，可以考虑：

```text
odom -> base_link
base_link -> base_link
base_link -> lidar_link
```

或：

```text
odom -> base_link
base_link -> base_link
base_link -> lidar_link
```

但必须避免重复发布等价 TF，尤其不能同时存在两个互相冲突的机器人基座路径。

## 最小可行方案

为了尽快跑通 SLAM，可以先采用：

```text
map -> odom -> base_link -> lidar_link
```

此时 `slam_toolbox` 配置中：

```text
base_frame: base_link
odom_frame: odom
map_frame: map
scan_topic: /scan
```

这个方案实现简单，但会让后续 Nav2 配置继续使用 `base_link`。如果后续学习和扩展需要贴近主流 ROS 约定，仍建议迁移到 `base_link`。

## 决策记录

当前决策：待确认。

候选决策：

- `D-01-001`：阶段 01 先使用 `base_link` 跑通 SLAM。
- `D-01-002`：阶段 01 直接引入 `base_link`，避免后续 Nav2 再迁移。

## 决策标准

优先级从高到低：

- 不破坏 Gazebo DiffDrive 的现有控制链路。
- SLAM 能正确转换 `/scan`。
- 后续 Nav2 配置清晰。
- 不引入重复或冲突 TF。
- 尽量减少阶段 01 的功能代码修改。

## 推荐检查命令

进入阶段实现或运行时确认时，可使用：

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo base_link lidar_link
ros2 run tf2_ros tf2_echo odom base_link
```

如果引入 `base_link`，还应检查：

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link lidar_link
```
