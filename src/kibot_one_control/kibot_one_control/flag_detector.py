from typing import List, cast

import rclpy
from kibot_one_interface.msg import FlagDetection  # type: ignore
from rclpy.node import Node, Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image  # type: ignore

from kibot_one_control.flag_detection_core import ColorDetection, detect_red_flag_pixels


class FlagDetector(Node):
    def __init__(
        self,
        node_name: str = "flag_detector",
        *,
        context: rclpy.Context | None = None,
        cli_args: List[str] | None = None,
        namespace: str | None = None,
        use_global_arguments: bool = True,
        enable_rosout: bool = True,
        start_parameter_services: bool = True,
        parameter_overrides: List[Parameter] | None = None,
        allow_undeclared_parameters: bool = False,
        automatically_declare_parameters_from_overrides: bool = False,
        enable_logger_service: bool = False,
    ) -> None:
        super().__init__(
            node_name=node_name,
            context=context,
            cli_args=cli_args,
            namespace=namespace,
            use_global_arguments=use_global_arguments,
            enable_rosout=enable_rosout,
            start_parameter_services=start_parameter_services,
            parameter_overrides=parameter_overrides,
            allow_undeclared_parameters=allow_undeclared_parameters,
            automatically_declare_parameters_from_overrides=automatically_declare_parameters_from_overrides,
            enable_logger_service=enable_logger_service,
        )

        self.declare_parameters(
            namespace="",
            parameters=[
                ("image_topic", "/camera/image_raw"),
                ("detection_topic", "/flag_dectection"),
                ("min_red", 120),
                ("red_margin", 45),
                ("min_pixel_count", 80),
            ] # type: ignore
        )
        self.image_sub = self.create_subscription(
            msg_type=Image,
            topic=cast(str, self.get_parameter(name="image_topic").value),
            callback=self._image_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.detection_pub = self.create_publisher(
            msg_type=FlagDetection,
            topic=cast(str, self.get_parameter(name="detection_topic").value),
            qos_profile=10
        )

    def _image_callback(self, msg: Image) -> None:
        detection: ColorDetection = detect_red_flag_pixels(
            image_data=bytes(msg.data),
            width=msg.width,
            height=msg.height,
            encoding=msg.encoding,
            min_red=cast(int, self.get_parameter(name="min_red").value),
            red_margin=cast(int, self.get_parameter(name="red_margin").value),
            min_pixel_count=cast(int, self.get_parameter(name="min_pixel_count").value)
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
        
        self.detection_pub.publish(msg=output)

def main() -> None:
    rclpy.init()
    node = FlagDetector()
    try:
        rclpy.spin(node=node)
    finally:
        node.destroy_node()
        rclpy.shutdown()