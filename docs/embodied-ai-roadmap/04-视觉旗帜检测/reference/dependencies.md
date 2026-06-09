# 依赖与环境

## 已确认依赖

源码和探针验证确认阶段 04 依赖：

- ROS2 Jazzy 环境。
- `ros_gz_bridge`，用于 Gazebo Image 到 ROS2 Image 的桥接。
- `sensor_msgs`，用于 `/camera/image_raw`。
- `std_msgs`，用于 `FlagDetection.msg` 的 `Header`。
- `kibot_one_interface`，用于新增 `FlagDetection` 消息。
- `pytest`，用于直接运行纯算法测试。

## 环境激活

在本项目中优先使用：

```bash
source .vscode/project-terminal-init.sh
```

该脚本会加载 ROS2、当前工作区 install overlay 和 Python venv。

## 临时 worktree 首次构建

如果在新建的临时 worktree 中复测文档，`.vscode/project-terminal-init.sh` 可能因为缺少 `install/setup.sh` 或 `.venv/bin/activate` 直接返回失败。此时先用 ROS 基础环境完成一次 bootstrap：

```bash
source ~/.bashrc
source ~/.bash_profile.jazzy
colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim
source install/setup.sh
```

如果该 worktree 没有 `.venv`，可以复用主工作区的 venv，或在已经有 `pytest` 的 ROS/Python 环境中直接运行阶段 04 的测试命令。普通项目工作区已经有 `install/` 和 `.venv/` 时，仍优先使用 `.vscode/project-terminal-init.sh`。

## 已知测试配置缺口

探针运行中发现：

```bash
colcon test --packages-select kibot_one_control --event-handlers console_direct+
```

当前会返回 `NO TESTS RAN`，说明 `kibot_one_control` 的 pytest 测试没有被 `colcon test` 自动发现。这不是阶段 04 新增检测算法失败，而是现有包测试集成方式需要后续整理。

阶段 04 的核心算法验收使用：

```bash
python -m pytest -q src/kibot_one_control/test/test_frontier_core.py src/kibot_one_control/test/test_flag_detection_core.py
```

## 需要运行时确认

- 图形环境或 headless 渲染环境不同，可能影响 Gazebo camera 是否能正常产出图像。
- `camera_link` 的 TF 是否被 Gazebo `/tf` 桥接出来需要在完整 TF tree 中确认。阶段 04 的检测事件不依赖 TF；阶段 05 如果做空间估计需要重新确认。
