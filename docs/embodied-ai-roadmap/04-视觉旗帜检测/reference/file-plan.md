# 文件计划

## Runtime 文件

| 文件 | 职责 |
| --- | --- |
| `src/kibot_one_interface/msg/FlagDetection.msg` | 定义视觉检测事件，不携带 Gazebo world 位姿 |
| `src/kibot_one_interface/CMakeLists.txt` | 注册 `FlagDetection.msg` 并加入 `std_msgs` 依赖 |
| `src/kibot_one_interface/package.xml` | 声明接口包对 `std_msgs` 的依赖 |
| `src/kibot_one_sim/models/kibot_one_base/model.sdf` | 给机器人增加 `camera_link` 和前向 RGB camera |
| `src/kibot_one_sim/config/ros_gz_bridge.yaml` | 把 Gazebo 图像 topic 桥接为 ROS2 `/camera/image_raw` |
| `src/kibot_one_control/kibot_one_control/flag_detection_core.py` | 纯算法：从 RGB/BGR 图像 bytes 中提取红色旗面像素 |
| `src/kibot_one_control/kibot_one_control/flag_detector.py` | ROS2 节点：订阅图像，发布 `/flag_detection` |
| `src/kibot_one_control/launch/flag_detection.launch.py` | 组合 Gazebo、bridge 和 `flag_detector` |
| `src/kibot_one_control/test/test_flag_detection_core.py` | 颜色检测核心单测 |
| `src/kibot_one_control/setup.py` | 安装 launch 文件并注册 `flag_detector` console script |

## 文档文件

| 文件 | 职责 |
| --- | --- |
| `roadmap/` | 阶段 04 主线实施顺序 |
| `reference/vision-contract.md` | 检测消息、topic、坐标和状态契约 |
| `reference/dependencies.md` | ROS2 / Gazebo / Python 依赖与环境说明 |
| `reference/final-runtime/` | 探针成品 runtime `.bak` 副本 |
| `checklist/` | low / medium / high 分层验收 |
| `evidence/` | 探针分支、diff、验证命令和复测记录 |

## 不修改的文件

阶段 04 不修改：

- `src/kibot_one_control/kibot_one_control/follow_controller.py`
- `src/kibot_one_control/kibot_one_control/frontier_explorer.py`
- `src/kibot_one_sim/worlds/kibot_one.world.sdf`
- `src/kibot_one_sim/worlds/kibot_one_obstacles.world.sdf`
- `src/kibot_one_sim/config/nav2_params.yaml`

原因：

- 本阶段只建立“视觉发现事件”，不接管旧 FOLLOW 控制器。
- 旗帜仍由 world include 进仿真，检测节点只能看图像，不读取 `/flag_pose`。
- 探索与任务切换属于阶段 06。
