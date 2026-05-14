# 阶段 01：验收条件

## 验收目标

本阶段的验收重点不是“SLAM 参数调得完美”，而是建立一条能支撑后续 Nav2 和自主探索的建图定位基础链路。

## 必须通过的功能验收

| 验收项 | 要求 | 备注 |
| --- | --- | --- |
| `/scan` 可用 | 能稳定发布 `sensor_msgs/msg/LaserScan` | 频率和 frame_id 需要记录 |
| `/odom` 可用 | 能稳定发布 `nav_msgs/msg/Odometry` | header frame 和 child frame 需要记录 |
| base frame 明确 | 明确使用 `base_link` 或 `base_link` | 推荐最终使用 `base_link` |
| lidar TF 可用 | base frame 能转换到 `lidar_link` | 缺失则必须补齐 |
| SLAM 可启动 | `slam_toolbox` 或等价节点能正常启动 | 第一版推荐 `slam_toolbox` |
| `/map` 可用 | 能发布 `nav_msgs/msg/OccupancyGrid` | RViz 可见 |
| `map -> odom` 可用 | SLAM 能发布定位相关 TF | 后续 Nav2 依赖此项 |
| RViz 可验证 | 地图、激光、机器人 frame 对齐 | 不要求地图完美，但不能明显错位 |

## TF 验收

目标 TF 链路优先为：

```text
map -> odom -> base_link -> lidar_link
```

如果阶段内暂时采用 `base_link`，则必须满足：

```text
map -> odom -> base_link -> lidar_link
```

并记录：

- 为什么暂时不用 `base_link`。
- 这对 Nav2 配置有什么影响。
- 后续是否需要迁移到 `base_link`。

## 地图验收

地图验收标准：

- 机器人移动时 `/map` 会更新。
- 障碍物大致能在地图中出现。
- 激光点云和障碍物边界大体对齐。
- 地图不会持续旋转、漂移或跳变到无法使用。
- 地图坐标系和机器人坐标系关系可解释。

不要求：

- 地图完全无噪声。
- 地图边界非常平滑。
- SLAM 参数一次调到最优。

## 对阶段 02 的解锁条件

进入 `02-Nav2-导航接入` 前，必须明确：

- Nav2 的 `global_frame` 应该使用什么，预期是 `map`。
- Nav2 的 `odom_frame` 应该使用什么，预期是 `odom`。
- Nav2 的 `robot_base_frame` 应该使用什么，预期是 `base_link` 或暂定 `base_link`。
- Nav2 的 obstacle layer 可以使用哪个 topic，预期是 `/scan`。
- Nav2 的控制输出是否直接使用 `/cmd_vel`。
- 当前 `cmd_vel_watchdog` 是否会影响 Nav2 控制。

## 不通过条件

如果出现以下任一情况，本阶段不能结束：

- `/scan` 存在但无法转换到 base frame。
- SLAM 启动后没有 `/map`。
- TF tree 中没有 `map -> odom`。
- RViz 中激光和地图明显错位且原因不明。
- 不知道当前使用的是 `base_link` 还是 `base_link`。
- 不知道 Nav2 后续应该使用哪个 robot base frame。

## 允许遗留的问题

以下问题可以记录后留到后续阶段，不阻塞阶段 01 完成：

- 地图质量还有优化空间。
- 需要更好的封闭探索 world。
- 是否引入 `base_footprint`。
- 是否将 SDF 迁移或补充为 URDF / Xacro。
- 是否重构 package，把 navigation 独立成新包。
