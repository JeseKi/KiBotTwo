# 04 接入 flag_detector 节点与 launch

## 本节目标

新增 `flag_detector` ROS2 节点：订阅 `/camera/image_raw`，调用上一节的纯函数，发布 `/flag_detection`。

上一节已经把颜色判断固定成纯函数。这一节只做运行时接线：从 ROS2 图像消息取出数据，交给算法层，再把结果填进 `FlagDetection`。这样节点代码保持很薄，后续如果替换检测算法，也不会牵动 launch 和消息契约。

节点内的调用关系是：

```text
main()
  -> FlagDetector.__init__()
       -> 订阅 /camera/image_raw
       -> 发布 /flag_detection
       -> 注册 _image_callback
  -> _image_callback(msg)
       -> detect_red_flag_pixels(...)
       -> FlagDetection()
       -> publish(...)
```

先写 `__init__` 再写 `_image_callback`，是为了顺着 ROS2 节点生命周期阅读：节点启动时先声明参数和建立 topic，然后在每一帧图像到来时执行检测。

## 节点文件骨架

创建 `src/kibot_one_control/kibot_one_control/flag_detector.py`，先写 imports：

```python
from typing import cast

import rclpy
from kibot_one_interface.msg import FlagDetection  # type: ignore
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image  # type: ignore

from kibot_one_control.flag_detection_core import detect_red_flag_pixels
```

这里使用 `qos_profile_sensor_data` 订阅图像，符合 ROS2 传感器 topic 常见 QoS。

## 初始化参数和 topic

继续写 `FlagDetector` 类：

```python
class FlagDetector(Node):
    def __init__(self) -> None:
        super().__init__("flag_detector")
        self.declare_parameters(
            namespace="",
            parameters=[
                ("image_topic", "/camera/image_raw"),
                ("detection_topic", "/flag_detection"),
                ("min_red", 120),
                ("red_margin", 45),
                ("min_pixel_count", 80),
            ],
        )
        self.detection_pub = self.create_publisher(
            msg_type=FlagDetection,
            topic=cast(str, self.get_parameter("detection_topic").value),
            qos_profile=10,
        )
        self.image_sub = self.create_subscription(
            msg_type=Image,
            topic=cast(str, self.get_parameter("image_topic").value),
            callback=self._image_callback,
            qos_profile=qos_profile_sensor_data,
        )
```

这些参数让后续可以调阈值或换图像 topic。默认值对应本阶段新增的相机和检测 topic。

## 图像回调

在类中加入 `_image_callback`：

```python
    def _image_callback(self, msg: Image) -> None:
        detection = detect_red_flag_pixels(
            bytes(msg.data),
            msg.width,
            msg.height,
            msg.encoding,
            min_red=cast(int, self.get_parameter("min_red").value),
            red_margin=cast(int, self.get_parameter("red_margin").value),
            min_pixel_count=cast(int, self.get_parameter("min_pixel_count").value),
        )
        output = FlagDetection()
        output.header = msg.header
        output.detected = detection.detected
        output.center_x = detection.center_x
        output.center_y = detection.center_y
        output.image_width = msg.width
        output.image_height = msg.height
        output.pixel_count = detection.pixel_count
        output.confidence = detection.confidence
        self.detection_pub.publish(output)
```

注意 `output.header = msg.header`。检测事件的 frame 来自相机图像，不从 `/flag_pose` 或 Gazebo world pose 推导。

## 节点入口

在文件末尾加入：

```python
def main() -> None:
    rclpy.init()
    node = FlagDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## 注册 console script 和 launch

打开 `src/kibot_one_control/setup.py`。在 launch data files 中，把 `flag_detection.launch.py` 放在 `control_console.launch.py` 后面、`frontier_exploration.launch.py` 前面：

```python
            'launch/control_console.launch.py',
            'launch/flag_detection.launch.py',
            'launch/frontier_exploration.launch.py',
```

然后在 `console_scripts` 中，把 `flag_detector` 放在 `follow_controller` 后面、`frontier_explorer` 前面：

```python
            'follow_controller = kibot_one_control.follow_controller:main',
            'flag_detector = kibot_one_control.flag_detector:main',
            'frontier_explorer = kibot_one_control.frontier_explorer:main',
```

接着创建 `src/kibot_one_control/launch/flag_detection.launch.py`。先写 imports 和仿真 launch 路径：

```python
from pathlib import Path

from ament_index_python.packages import get_package_share_directory  # type: ignore
from launch import LaunchDescription  # type: ignore
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription  # type: ignore
from launch.conditions import IfCondition  # type: ignore
from launch.launch_description_sources import PythonLaunchDescriptionSource  # type: ignore
from launch.substitutions import LaunchConfiguration  # type: ignore
from launch_ros.actions import Node  # type: ignore
```

然后写 launch description：

```python
def generate_launch_description() -> LaunchDescription:
    sim_share = Path(get_package_share_directory(package_name="kibot_one_sim"))
    sim_launch = sim_share / "launch" / "sim_with_bridge.launch.py"

    world_arg = DeclareLaunchArgument(
        name="world",
        default_value=str(sim_share / "worlds" / "kibot_one.world.sdf"),
        description="Gazebo 世界的绝对路径。",
    )
    start_sim_arg = DeclareLaunchArgument(
        name="start_sim",
        default_value="true",
        description="是否启动 Gazebo 与 ros_gz_bridge。",
    )
    run_on_start_arg = DeclareLaunchArgument(
        name="run_on_start",
        default_value="true",
        description="是否让 Gazebo 启动后立即运行仿真。",
    )
```

接着组合仿真和检测节点：

```python
    start_sim = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(launch_file_path=str(sim_launch)),
        launch_arguments={
            "world": LaunchConfiguration(variable_name="world"),
            "run_on_start": LaunchConfiguration(variable_name="run_on_start"),
        }.items(),
        condition=IfCondition(predicate_expression=LaunchConfiguration(variable_name="start_sim")),
    )

    detector = Node(
        package="kibot_one_control",
        executable="flag_detector",
        name="flag_detector",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription([
        world_arg,
        start_sim_arg,
        run_on_start_arg,
        start_sim,
        detector,
    ])
```

`start_sim` 参数让你可以单独启动检测节点做消息注入测试；默认则直接启动仿真和 bridge。

到这里，阶段 04 的三个层次已经接上：仿真 launch 提供相机和 bridge，`flag_detector` 节点消费图像，算法核心给出逐帧检测结果。最后一节会从构建、算法测试和 topic 消息三个层面确认这条链路。

## 做完应该看到什么

运行：

```bash
source .vscode/project-terminal-init.sh
colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim
```

期望 `flag_detector` 可以作为 console script 安装，`flag_detection.launch.py` 可以被 `ros2 launch` 找到。

## 下一节

进入 `05-验证视觉闭环并交付契约.md`。现在 runtime 文件齐了，最后用构建、测试和 topic 消息证明链路成立。
