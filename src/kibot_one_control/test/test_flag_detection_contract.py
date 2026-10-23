"""Fast interface guards that also run without a ROS installation."""

import argparse
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CONTROL = ROOT / "src/kibot_one_control"
TOPICS = {"image_topic": "/camera/image_raw", "detection_topic": "/flag_detection"}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def test_detector_defaults_match_public_topics() -> None:
    tree = _tree(CONTROL / "kibot_one_control/flag_detector.py")
    declaration = next(
        call
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "declare_parameters"
    )
    defaults = dict(
        ast.literal_eval(
            next(kw.value for kw in declaration.keywords if kw.arg == "parameters")
        )
    )
    for name, topic in TOPICS.items():
        assert defaults[name] == topic


def test_launch_exposes_and_forwards_topic_arguments() -> None:
    tree = _tree(CONTROL / "launch/flag_detection.launch.py")
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    arguments = {}
    for call in calls:
        if isinstance(call.func, ast.Name) and call.func.id == "DeclareLaunchArgument":
            keywords = {kw.arg: kw.value for kw in call.keywords}
            arguments[ast.literal_eval(keywords["name"])] = keywords["default_value"]
    detector = next(
        call
        for call in calls
        if isinstance(call.func, ast.Name) and call.func.id == "Node"
    )
    parameters = next(kw.value for kw in detector.keywords if kw.arg == "parameters")
    forwarded = {
        ast.literal_eval(key): value
        for mapping in parameters.elts
        for key, value in zip(mapping.keys, mapping.values)
    }
    for name, topic in TOPICS.items():
        assert ast.literal_eval(arguments[name]) == topic
        configuration = forwarded[name]
        assert isinstance(configuration, ast.Call)
        assert isinstance(configuration.func, ast.Name)
        assert configuration.func.id == "LaunchConfiguration"
        assert ast.literal_eval(configuration.keywords[0].value) == name


@pytest.mark.parametrize(
    "argv, expected",
    [
        ([], ("/camera/image_raw", "/flag_detection")),
        (
            ["--image-topic", "/test/image", "--detection-topic", "/test/detection"],
            ("/test/image", "/test/detection"),
        ),
    ],
)
def test_camera_viewer_cli_topics(argv, expected) -> None:
    # Execute the actual CLI parser without importing its ROS/OpenCV UI dependencies.
    tree = _tree(ROOT / "tools/camera_viewer.py")
    parser = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "parse_args"
    )
    namespace = {"argparse": argparse}
    exec(  # noqa: S102 - only the repository's parser function is executed
        compile(ast.Module(body=[parser], type_ignores=[]), "camera_viewer.py", "exec"),
        namespace,
    )
    args = namespace["parse_args"](argv)
    assert (args.image_topic, args.detection_topic) == expected


def test_flag_detection_wire_schema_is_stable() -> None:
    fields = [
        line.split("#", 1)[0].strip()
        for line in (ROOT / "src/kibot_one_interface/msg/FlagDetection.msg")
        .read_text()
        .splitlines()
    ]
    assert [field for field in fields if field] == [
        "std_msgs/Header header",
        "bool detected",
        "float32 center_x",
        "float32 center_y",
        "uint32 image_width",
        "uint32 image_height",
        "uint32 pixel_count",
        "float32 confidence",
    ]


def test_runtime_sources_do_not_reintroduce_legacy_topic() -> None:
    violations = []
    for directory in (ROOT / "src", ROOT / "tools"):
        for path in directory.rglob("*"):
            if (
                path.suffix in {".py", ".yaml", ".xml"}
                and "test" not in path.parts
                and "/flag_dectection" in path.read_text(encoding="utf-8")
            ):
                violations.append(str(path.relative_to(ROOT)))
    assert not violations, f"Legacy detection topic in runtime files: {violations}"
