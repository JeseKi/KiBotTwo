# 阶段 01：记录与复盘

## 当前阶段结论

待填写。

## 已确认事实

- 当前项目已有 `/scan`。
- 当前项目已有 `/odom`。
- 当前 Gazebo 模型中机器人基座 link 是 `base_link`。
- 当前 Gazebo 模型中激光雷达 link 是 `lidar_link`。
- 当前还没有 `map` frame。
- 当前还没有相机。

## 尚未确认的问题

- `/scan.header.frame_id` 运行时是否为 `lidar_link`。
- `/odom.child_frame_id` 运行时是否为 `base_link`。
- ROS TF tree 中是否存在 `base_link -> lidar_link`。
- 阶段 01 是否直接引入 `base_link`。
- SLAM 第一版是否放在 `kibot_one_sim`，还是新建 `kibot_one_navigation`。
- 当前障碍物世界是否足够验证 SLAM。

## 决策记录

### D-01-001：base frame 选择

状态：待决策。

候选：

- 使用 `base_link`。
- 引入 `base_link`。

判断依据：

- 是否会破坏现有 Gazebo TF。
- 是否能让 SLAM 稳定运行。
- 是否利于后续 Nav2。

### D-01-002：SLAM 文件归属

状态：待决策。

候选：

- 放入 `kibot_one_sim`。
- 新建 `kibot_one_navigation`。

当前倾向：先放入 `kibot_one_sim`，阶段 02 再考虑拆分。

## 调试记录

待填写。

格式：

```text
现象：
排查：
结论：
后续：
```

## 阶段复盘

本阶段结束时填写：

- SLAM 是否跑通？
- 最终采用了哪个 base frame？
- 是否补齐了 lidar TF？
- 地图质量是否足够支撑 Nav2？
- 阶段 02 接入 Nav2 的最大风险是什么？
