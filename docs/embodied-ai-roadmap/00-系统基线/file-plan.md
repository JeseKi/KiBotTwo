# 阶段 00：文件计划与实际产物

## 本阶段性质

本阶段是基线调查阶段，不修改功能代码。

## 实际新增或更新的文档

- `docs/embodied-ai-roadmap/00-系统基线/roadmap.md`
- `docs/embodied-ai-roadmap/00-系统基线/acceptance.md`
- `docs/embodied-ai-roadmap/00-系统基线/file-plan.md`
- `docs/embodied-ai-roadmap/00-系统基线/system-inventory.md`
- `docs/embodied-ai-roadmap/00-系统基线/flag-pose-flow.md`
- `docs/embodied-ai-roadmap/00-系统基线/risk-register.md`
- `docs/embodied-ai-roadmap/00-系统基线/notes.md`

## 本阶段阅读过的关键文件

| 文件 | 用途 |
| --- | --- |
| `README.md` | 总体项目说明、运行入口、topic 与服务说明 |
| `src/kibot_one_control/package.xml` | 控制包依赖 |
| `src/kibot_one_control/setup.py` | 控制节点入口 |
| `src/kibot_one_control/launch/*.launch.py` | 控制与跟随启动入口 |
| `src/kibot_one_control/kibot_one_control/*.py` | 控制、模式、跟随、遥控逻辑 |
| `src/kibot_one_interface/msg/*.msg` | 模式消息定义 |
| `src/kibot_one_interface/srv/*.srv` | 模式服务定义 |
| `src/kibot_one_sim/launch/*.launch.py` | Gazebo 和 bridge bringup |
| `src/kibot_one_sim/config/ros_gz_bridge.yaml` | ROS-Gazebo topic 桥接 |
| `src/kibot_one_sim/models/kibot_one_base/model.sdf` | 机器人模型、激光雷达、差速驱动 |
| `src/kibot_one_sim/models/follow_flag/model.sdf` | 旗帜模型与位姿发布插件 |
| `src/kibot_one_sim/worlds/*.world.sdf` | 默认世界和障碍物世界 |

## 本阶段未修改的功能文件

本阶段没有修改：

- package 源码。
- launch 文件。
- SDF 模型。
- world 文件。
- msg / srv 接口。
- bridge 配置。

## 后续阶段预计会涉及的文件

### 阶段 01：SLAM 建图与定位

可能新增或修改：

- SLAM launch 文件。
- SLAM 参数文件。
- TF 相关 launch 或静态 TF 配置。
- RViz 配置。
- 如需要，机器人 frame 命名或 frame 适配配置。

### 阶段 02：Nav2 导航接入

可能新增或修改：

- Nav2 bringup launch。
- Nav2 参数 YAML。
- 机器人 footprint / radius 配置。
- 控制源互斥策略。

### 阶段 04：视觉旗帜检测

可能新增或修改：

- `kibot_one_base/model.sdf`，增加 camera sensor。
- `ros_gz_bridge.yaml`，增加 image / camera_info 桥接。
- 新的视觉检测 package 或节点。
- 新的检测结果 msg。

## 文件组织建议

后续每个阶段都应先创建阶段目录，再补充：

- `roadmap.md`
- `acceptance.md`
- `file-plan.md`
- `notes.md`

但从阶段 01 开始，文档应服务于实现，不应再写成泛泛学习清单。
