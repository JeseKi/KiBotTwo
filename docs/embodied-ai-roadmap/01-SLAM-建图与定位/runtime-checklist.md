# 阶段 01：运行时确认清单

## 使用目的

本文件用于记录阶段 01 实现前和实现中的运行时事实。

阶段 00 主要基于源码静态分析；阶段 01 必须补充运行时确认，尤其是 TF 和 topic header。

## 环境准备

推荐先使用项目环境初始化脚本：

```bash
source .vscode/project-terminal-init.sh
source install/setup.bash
```

如尚未构建：

```bash
colcon build
source install/setup.bash
```

## 推荐启动方式

优先使用障碍物世界：

```bash
ros2 launch kibot_one_control follow_phase2.launch.py
```

或直接使用主入口：

```bash
ros2 launch kibot_one_sim kibot_one.launch.py \
  world:=<kibot_one_obstacles.world.sdf 的绝对路径> \
  mode:=2
```

## Topic 检查

| 检查项 | 命令 | 结果 |
| --- | --- | --- |
| `/scan` 是否存在 | `ros2 topic list | grep scan` | 待填写 |
| `/odom` 是否存在 | `ros2 topic list | grep odom` | 待填写 |
| `/tf` 是否存在 | `ros2 topic list | grep tf` | 待填写 |
| `/scan` 类型 | `ros2 topic info /scan` | 待填写 |
| `/odom` 类型 | `ros2 topic info /odom` | 待填写 |

## 消息 header 检查

| 检查项 | 预期 | 实际结果 |
| --- | --- | --- |
| `/scan.header.frame_id` | `lidar_link` | 待填写 |
| `/odom.header.frame_id` | `odom` | 待填写 |
| `/odom.child_frame_id` | `base_link` | 待填写 |

推荐命令：

```bash
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

## TF 检查

| 检查项 | 预期 | 实际结果 |
| --- | --- | --- |
| `odom -> base_link` | 存在 | 待填写 |
| `base_link -> lidar_link` | 待确认 | 待填写 |
| `map -> odom` | SLAM 启动前不存在，启动后存在 | 待填写 |
| `base_link` | 当前可能不存在 | 待填写 |

推荐命令：

```bash
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link lidar_link
```

## SLAM 启动后检查

| 检查项 | 预期 | 实际结果 |
| --- | --- | --- |
| `/map` 是否存在 | 存在 | 待填写 |
| `/map` 类型 | `nav_msgs/msg/OccupancyGrid` | 待填写 |
| `map -> odom` | 存在 | 待填写 |
| RViz fixed frame | `map` | 待填写 |
| 激光与地图是否对齐 | 大体对齐 | 待填写 |

## 异常记录

格式：

```text
现象：
命令：
输出摘要：
判断：
后续处理：
```
