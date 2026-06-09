# 使用与验证

## 环境准备

```bash
source .vscode/project-terminal-init.sh
```

如果你在临时 worktree 中复测，并且这个脚本因为缺少 `install/setup.sh` 或 `.venv/bin/activate` 失败，先执行：

```bash
source ~/.bashrc
source ~/.bash_profile.jazzy
colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim
source install/setup.sh
```

然后再继续下面的构建和验证命令。

## 构建

```bash
colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim
```

探针结果：

```text
Summary: 3 packages finished [5.55s]
```

## 核心算法测试

当前 `colcon test --packages-select kibot_one_control` 没有发现 pytest 测试，会返回 `NO TESTS RAN`。阶段 04 先用直接 pytest 命令验证核心算法：

```bash
python -m pytest -q src/kibot_one_control/test/test_frontier_core.py src/kibot_one_control/test/test_flag_detection_core.py
```

探针结果：

```text
6 passed in 0.01s
```

## 短时 launch 冒烟

启动：

```bash
ros2 launch kibot_one_control flag_detection.launch.py start_sim:=true run_on_start:=true
```

另一个终端检查 topic：

```bash
ros2 topic list
```

探针中观察到：

```text
/camera/image_raw
/flag_detection
/flag_pose
/odom
/scan
/tf
```

## 最小成功用例

启动后读取一条检测消息：

```bash
ros2 topic echo --once /flag_detection
```

探针中收到：

```text
header:
  stamp:
    sec: 6
    nanosec: 204000000
  frame_id: camera_link
detected: true
center_x: 44.15916061401367
center_y: 31.16216278076172
image_width: 320
image_height: 240
pixel_count: 333
confidence: 0.0043359375558793545
```

判定标准：

- 有 `/camera/image_raw`。
- 有 `/flag_detection`。
- `/flag_detection` 能收到消息。
- `detected=true` 时，中心点在图像范围内。
- 消息只包含图像观测，不包含 `/flag_pose` 或 Gazebo world 坐标。

## 第一视角查看

阶段 04 已接入前向相机，可以直接查看机器人第一视角图像。保持 launch 运行，在另一个终端执行：

```bash
rqt_image_view
```

在界面中选择 `/camera/image_raw`，应能看到来自 `camera_link` 的前向画面。然后再开一个终端读取检测事件：

```bash
ros2 topic echo /flag_detection
```

使用时可以把 `rqt_image_view` 里的画面和 `/flag_detection` 消息对照起来看：

- 旗帜进入画面后，`detected` 应该变为 `true`。
- `center_x`、`center_y` 表示检测到的红色区域中心点，坐标范围分别落在 `image_width` 和 `image_height` 内。
- `confidence` 是当前红色像素占图像面积的比例，不是 YOLO 分类置信度。

当前阶段不发布带检测框或中心点标记的 debug image。也就是说，`rqt_image_view` 只能看到原始第一视角画面；检测结果需要通过 `/flag_detection` topic 对照观察。带 bbox、类别、置信度文字或中心点 overlay 的可视化应放到 `04B-YOLO-旗帜检测升级` 中完成。

## 常见失败

- 看不到 `/camera/image_raw`：先检查 `ros_gz_bridge.yaml` 的 image bridge 和 SDF camera topic 是否一致。
- 看不到 `/flag_detection`：先检查 `flag_detector` console script 是否注册并随 launch 启动。
- 一直 `detected=false`：先确认旗帜是否在相机视野中，再检查红色阈值和 `min_pixel_count`。
- `rqt_image_view` 打不开或没有 `/camera/image_raw` 可选：先确认当前终端已经 source ROS2 环境，并且 launch 仍在运行。
- Gazebo 输出 `libEGL warning`：如果图像和检测消息仍能发布，记录为环境警告；如果没有图像，优先排查当前机器的 Gazebo 渲染能力。

## 收尾

验证完成后关闭 launch。若使用 `timeout` 运行 launch，确认没有残留：

```bash
pgrep -af "ros2 launch|gz sim|parameter_bridge|flag_detector"
```
