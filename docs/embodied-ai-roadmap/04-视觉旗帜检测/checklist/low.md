# Low 验收

最低可用验收用于证明“视觉发现事件已经存在”。

- `colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim` 成功。
- `python -m pytest -q src/kibot_one_control/test/test_flag_detection_core.py` 成功。
- `ros2 launch kibot_one_control flag_detection.launch.py start_sim:=true run_on_start:=true` 启动后，`ros2 topic list` 能看到 `/camera/image_raw` 和 `/flag_detection`。
- `ros2 topic echo --once /flag_detection` 能收到 `kibot_one_interface/msg/FlagDetection`。
- 收到的检测消息不包含 Gazebo world 坐标字段。
