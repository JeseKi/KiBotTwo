# 最终 runtime 副本

本目录保存阶段 04 探针实现中所有非 `docs/` runtime 文件的最终副本，文件名以 `.bak` 结尾，并保留项目相对路径。

这些文件用于文档复测后的审计：

- 复测者不应复制这些 `.bak` 文件。
- 复测者不应套用 `evidence/reference-runtime.patch`。
- 主 Agent 用这些副本逐文件核对复测产物是否与探针实现一致。

阶段 04 的 runtime 文件清单：

- `src/kibot_one_interface/msg/FlagDetection.msg`
- `src/kibot_one_interface/CMakeLists.txt`
- `src/kibot_one_interface/package.xml`
- `src/kibot_one_control/kibot_one_control/flag_detection_core.py`
- `src/kibot_one_control/kibot_one_control/flag_detector.py`
- `src/kibot_one_control/launch/flag_detection.launch.py`
- `src/kibot_one_control/test/test_flag_detection_core.py`
- `src/kibot_one_control/setup.py`
- `src/kibot_one_sim/config/ros_gz_bridge.yaml`
- `src/kibot_one_sim/models/kibot_one_base/model.sdf`
