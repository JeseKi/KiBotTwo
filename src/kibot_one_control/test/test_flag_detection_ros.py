"""Real DDS regression tests; run after colcon build and sourcing install/setup.bash."""

import importlib.util
import os
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

# Make an ordinary Python-only test run useful while making ROS CI fail on missing dependencies.
if os.environ.get("KIBOT_REQUIRE_ROS_TESTS") == "1":
    import rclpy

else:
    rclpy = pytest.importorskip(
        "rclpy", reason="source a ROS 2 environment for DDS tests"
    )
    pytest.importorskip(
        "kibot_one_interface.msg", reason="build and source the interface package"
    )

from kibot_one_control.flag_detector import FlagDetector
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from sensor_msgs.msg import Image

from kibot_one_interface.msg import FlagDetection


@pytest.fixture
def graph():
    rclpy.init(args=[])
    executor = SingleThreadedExecutor()
    probe = Node("flag_contract_probe")
    executor.add_node(probe)
    try:
        yield executor, probe
    finally:
        nodes = executor.get_nodes()
        executor.shutdown(timeout_sec=2.0)
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()


def _wait(executor, predicate, description, timeout=10.0):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        executor.spin_once(timeout_sec=0.05)
    assert predicate(), f"Timed out waiting for {description}"


def _image(red_pixels, stamp, encoding="rgb8"):
    image = Image()
    image.header.frame_id = "camera_link"
    image.header.stamp.sec = stamp
    image.header.stamp.nanosec = 123456789
    image.width, image.height = 20, 10
    image.encoding = encoding
    image.step = image.width * (1 if encoding == "mono8" else 3)
    data = bytearray(image.step * image.height)
    positions = [(x, y) for y in range(1, 9) for x in range(6, 16)]
    for x, y in positions[:red_pixels]:
        offset = (y * image.width + x) * 3
        data[offset : offset + 3] = bytes((220, 20, 20))
    image.data = bytes(data)
    return image


def _check_pipeline(graph, image_topic, detection_topic):
    executor, probe = graph
    received = []
    subscription = probe.create_subscription(
        FlagDetection, detection_topic, received.append, 10
    )
    publisher = probe.create_publisher(Image, image_topic, qos_profile_sensor_data)
    _wait(
        executor,
        lambda: (
            publisher.get_subscription_count() > 0
            and subscription.get_publisher_count() > 0
        ),
        "matching image and detection endpoints",
    )
    types = dict(probe.get_topic_names_and_types())
    assert types[image_topic] == ["sensor_msgs/msg/Image"]
    assert types[detection_topic] == ["kibot_one_interface/msg/FlagDetection"]
    for endpoint in probe.get_publishers_info_by_topic(detection_topic):
        assert endpoint.qos_profile.reliability == ReliabilityPolicy.RELIABLE
        assert endpoint.qos_profile.durability == DurabilityPolicy.VOLATILE
        assert endpoint.qos_profile.history == HistoryPolicy.KEEP_LAST
        assert endpoint.qos_profile.depth == 10
    assert probe.count_publishers("/flag_dectection") == 0

    # A hit followed by misses must clear stale centers; each result keeps its input header.
    for stamp, (red_pixels, encoding) in enumerate(
        [(80, "rgb8"), (0, "rgb8"), (1, "rgb8"), (0, "mono8")], start=100
    ):
        image = _image(red_pixels, stamp, encoding)

        def publish_until_received(image=image):
            publisher.publish(image)
            return any(msg.header.stamp == image.header.stamp for msg in received)

        _wait(executor, publish_until_received, f"FlagDetection for frame {stamp}")
        result = next(msg for msg in received if msg.header.stamp == image.header.stamp)
        assert result.header == image.header
        assert (result.image_width, result.image_height) == (20, 10)
        assert result.detected == (red_pixels == 80)
        assert result.pixel_count == red_pixels
        assert result.confidence == pytest.approx(red_pixels / 200)
        assert (result.center_x, result.center_y) == (
            (10.5, 4.5) if result.detected else (0.0, 0.0)
        )


def test_default_detector_publishes_public_contract(graph):
    detector = FlagDetector()
    graph[0].add_node(detector)
    assert detector.get_parameter("image_topic").value == "/camera/image_raw"
    assert detector.get_parameter("detection_topic").value == "/flag_detection"
    _check_pipeline(graph, "/camera/image_raw", "/flag_detection")


@pytest.mark.parametrize("configuration", ["parameters", "remap"])
def test_detector_supports_explicit_topic_configuration(graph, configuration):
    image_topic, detection_topic = "/flag_contract/image", "/flag_contract/detection"
    if configuration == "parameters":
        detector = FlagDetector(
            parameter_overrides=[
                Parameter("image_topic", value=image_topic),
                Parameter("detection_topic", value=detection_topic),
            ]
        )
    else:
        detector = FlagDetector(
            cli_args=[
                "--ros-args",
                "-r",
                f"/camera/image_raw:={image_topic}",
                "-r",
                f"/flag_detection:={detection_topic}",
            ]
        )
    graph[0].add_node(detector)
    assert detector.image_sub.topic_name == image_topic
    assert detector.detection_pub.topic_name == detection_topic
    assert graph[1].count_publishers("/flag_detection") == 0
    _check_pipeline(graph, image_topic, detection_topic)


@contextmanager
def _launch_detector(tmp_path, arguments):
    log_path = tmp_path / "flag_detection_launch.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                "ros2",
                "launch",
                "kibot_one_control",
                "flag_detection.launch.py",
                "start_sim:=false",
                *arguments,
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            yield
            assert process.poll() is None, log_path.read_text()
        except BaseException:
            print(log_path.read_text())
            raise
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)


@pytest.mark.parametrize("custom_topics", [False, True])
def test_installed_launch_routes_images_without_gazebo(graph, tmp_path, custom_topics):
    image_topic, detection_topic = (
        ("/launch_contract/image", "/launch_contract/detection")
        if custom_topics
        else ("/camera/image_raw", "/flag_detection")
    )
    arguments = (
        [f"image_topic:={image_topic}", f"detection_topic:={detection_topic}"]
        if custom_topics
        else []
    )
    with _launch_detector(tmp_path, arguments):
        _check_pipeline(graph, image_topic, detection_topic)


def test_camera_viewer_default_subscriber_receives_detector_messages(graph):
    # Import the real tool, then exercise its real ROS subscription without an HTTP server.
    path = Path(__file__).resolve().parents[3] / "tools/camera_viewer.py"
    spec = importlib.util.spec_from_file_location("flag_contract_camera_viewer", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    args = module.parse_args([])
    state = module.ViewerState(jpeg_quality=85, min_red=120, red_margin=45)
    viewer = module.CameraViewerNode(
        state=state,
        image_topic=args.image_topic,
        detection_topic=args.detection_topic,
    )
    detector = FlagDetector()
    graph[0].add_node(viewer)
    graph[0].add_node(detector)
    assert viewer._detection_sub.topic_name == "/flag_detection"
    _check_pipeline(graph, args.image_topic, args.detection_topic)
    _wait(
        graph[0], lambda: state.latest_detection is not None, "viewer detection update"
    )
