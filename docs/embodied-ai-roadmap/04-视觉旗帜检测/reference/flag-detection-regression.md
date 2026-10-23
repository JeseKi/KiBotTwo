# FlagDetection 接口回归验证

## 问题影响

修复前，唯一的检测发布端 `flag_detector` 默认发布 `/flag_dectection`，唯一的检测订阅端 `tools/camera_viewer.py` 也使用这个拼写，预览工具因此可能掩盖接口错误。`flag_detection.launch.py` 只传入 `use_sim_time`，会沿用错误默认值。按文档订阅 `/flag_detection` 的节点和 `ros2 topic echo` 收不到检测结果。

`flag_pose_publisher` 和 `follow_controller` 使用 `PoseStamped` 类型的 `/flag_pose`，不消费 `FlagDetection`；边界探索也没有检测订阅。位置估计和任务状态机尚未实现。本次修复影响检测接口及预览工具，现有跟随链路并非通过该接口工作。

原有 `test_flag_detection_core.py` 只测试像素算法，无法发现话题接线错误。新增静态测试约束节点、launch、预览工具默认值和消息字段；ROS 测试通过真实 DDS 发布合成图像，覆盖默认接线、参数覆盖、remap、安装后的无仿真 launch 以及预览工具订阅。ROS 测试还验证 reliable/volatile/keep-last-10 输出、header 和尺寸透传、命中后无目标及小噪声、未支持的 encoding。

## 构建与自动化测试

在项目根目录、已安装 ROS 2 Jazzy 的终端执行。测试使用独立 domain，先关闭同一 domain 内的其他检测器：

```bash
source /opt/ros/jazzy/setup.bash
sudo apt-get install python3-pytest python3-opencv python3-colcon-common-extensions
export ROS_DOMAIN_ID=73
export ROS_LOCALHOST_ONLY=1
colcon build --packages-select kibot_one_interface kibot_one_sim kibot_one_control
source install/setup.bash
KIBOT_REQUIRE_ROS_TESTS=1 colcon test --packages-select kibot_one_control \
  --event-handlers console_direct+ --return-code-on-test-failure --pytest-args " -q"
colcon test-result --verbose
```

`setup.py` 的 `tests_require=['pytest']` 和 `package.xml` 的测试依赖保证 colcon 可以发现测试。`KIBOT_REQUIRE_ROS_TESTS=1` 会让缺失 ROS 或生成消息的环境直接失败，防止 CI 将跳过 ROS 测试视为成功。工作流 `.github/workflows/flag-detection-contract.yml` 在 ROS Jazzy 容器中执行构建和上述回归，不需要 Gazebo 渲染或 YOLO 权重。

也可以直接运行全部测试：

```bash
KIBOT_REQUIRE_ROS_TESTS=1 python3 -m pytest -q src/kibot_one_control/test
```

没有 ROS 时仍可检查算法、默认值、launch 参数和消息定义：

```bash
python3 -m pytest -q src/kibot_one_control/test
```

此时 ROS 测试模块会明确显示 skipped；这不能替代真实通信测试。

## 无 Gazebo 的手动通信验证

每个终端都加载 ROS 和 `install/setup.bash`，设置同一 `ROS_DOMAIN_ID=73`。终端 A 启动节点：

```bash
ros2 launch kibot_one_control flag_detection.launch.py start_sim:=false
```

终端 B 检查发布类型、QoS 并等待一条检测消息：

```bash
ros2 topic info /flag_detection --verbose
ros2 interface show kibot_one_interface/msg/FlagDetection
ros2 topic echo /flag_detection kibot_one_interface/msg/FlagDetection --once
```

终端 C 持续发布一像素红色图像：

```bash
ros2 topic pub --rate 5 --qos-reliability best_effort \
  /camera/image_raw sensor_msgs/msg/Image \
  '{header: {stamp: {sec: 123, nanosec: 456}, frame_id: camera_link}, height: 1, width: 1, encoding: rgb8, is_bigendian: 0, step: 3, data: [220, 20, 20]}'
```

预期收到 `header.stamp={123,456}`、`frame_id=camera_link`、图像尺寸 `1×1`、`pixel_count=1`、`confidence=1.0`、`detected=false`、中心为零。默认 `min_pixel_count=80`，一像素图像用于验证链路；自动化测试另用 80 个红色像素覆盖 `detected=true`。检测发布端应位于 `/flag_detection`，旧拼写不应出现发布端。

自定义接线示例：

```bash
ros2 launch kibot_one_control flag_detection.launch.py start_sim:=false \
  image_topic:=/test/image detection_topic:=/test/detection
python3 tools/camera_viewer.py --image-topic /test/image --detection-topic /test/detection
```

## Gazebo 相机验证

关闭合成图像发布器和无仿真 launch，再执行：

```bash
ros2 launch kibot_one_control flag_detection.launch.py start_sim:=true run_on_start:=true
```

另一个终端执行 `ros2 topic hz /camera/image_raw` 和 `ros2 topic echo /flag_detection --once`，核对实际相机帧的 header、尺寸和检测结果。合成图像回归覆盖通信契约，Gazebo 验证另外检查渲染及 bridge。
