# 探针 diff 摘要

## 探针信息

- 探针分支：`roadmap-probe/04-vision-flag-detection`
- 探针提交：`0406c08`
- 提交说明：`probe: validate part 04 vision flag detection roadmap`

## Runtime 文件变化

新增：

- `src/kibot_one_interface/msg/FlagDetection.msg`
- `src/kibot_one_control/kibot_one_control/flag_detection_core.py`
- `src/kibot_one_control/kibot_one_control/flag_detector.py`
- `src/kibot_one_control/launch/flag_detection.launch.py`
- `src/kibot_one_control/test/test_flag_detection_core.py`

修改：

- `src/kibot_one_interface/CMakeLists.txt`
- `src/kibot_one_interface/package.xml`
- `src/kibot_one_control/setup.py`
- `src/kibot_one_sim/config/ros_gz_bridge.yaml`
- `src/kibot_one_sim/models/kibot_one_base/model.sdf`

## 行为摘要

- 在机器人模型中增加 `camera_link` 和前向 RGB camera。
- 通过 bridge 暴露 `/camera/image_raw`。
- 新增 `FlagDetection` 消息，输出图像内检测结果。
- 新增 `flag_detection_core.py`，用 RGB/BGR 像素阈值检测红色旗面。
- 新增 `flag_detector` 节点，订阅图像并发布 `/flag_detection`。
- 新增 `flag_detection.launch.py`，组合仿真、bridge 和检测节点。

## 不进入阶段 04 的内容

- 不修改 `follow_controller.py`。
- 不让任务状态机消费检测事件。
- 不估计 `map` / `world` 坐标中的旗帜位置。
- 不删除 `/flag_pose`，只把它降级为 debug 对照。
