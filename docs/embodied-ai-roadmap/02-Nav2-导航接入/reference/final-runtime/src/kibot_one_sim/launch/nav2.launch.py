# mypy: disable-error-code="import-untyped"

from pathlib import Path
import subprocess

from ament_index_python.packages import get_package_share_directory  # type: ignore
from launch import LaunchDescription  # type: ignore
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction  # type: ignore
from launch.conditions import IfCondition  # type: ignore
from launch.launch_description_sources import PythonLaunchDescriptionSource  # type: ignore
from launch.substitutions import LaunchConfiguration  # type: ignore
from launch_ros.actions import Node  # type: ignore


def _check_nav2_runtime_deps(context, *args, **kwargs):
    if LaunchConfiguration("check_runtime_deps").perform(context).lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return []

    fastcdr_lib = Path("/opt/ros/jazzy/lib/libfastcdr.so.2")
    if not fastcdr_lib.exists():
        raise RuntimeError(_dependency_error(f"未找到 {fastcdr_lib}"))

    result = subprocess.run(
        ["bash", "-lc", f"nm -D {fastcdr_lib} 2>/dev/null | c++filt"],
        check=False,
        capture_output=True,
        text=True,
    )
    if "eprosima::fastcdr::Cdr::serialize(unsigned int)" not in result.stdout:
        raise RuntimeError(_dependency_error(f"{fastcdr_lib} 缺少 Cdr::serialize(unsigned int)"))

    return []


def _dependency_error(reason: str) -> str:
    return f"""
Nav2 运行依赖检查失败：{reason}

请先升级 Jazzy FastCDR / FastRTPS 相关包：

sudo apt-get update
sudo apt-get install -y \\
  ros-jazzy-fastcdr \\
  ros-jazzy-fastrtps \\
  ros-jazzy-rmw-fastrtps-cpp \\
  ros-jazzy-rmw-fastrtps-shared-cpp \\
  ros-jazzy-rosidl-typesupport-fastrtps-c \\
  ros-jazzy-rosidl-typesupport-fastrtps-cpp \\
  ros-jazzy-rmw-cyclonedds-cpp

也可以先运行：

src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh

如果只是查看 launch 参数，可用：

ros2 launch kibot_one_sim nav2.launch.py --show-args
"""


def generate_launch_description() -> LaunchDescription:
    sim_pkg_share = Path(get_package_share_directory("kibot_one_sim"))
    nav2_bringup_share = Path(get_package_share_directory("nav2_bringup"))

    default_world = sim_pkg_share / "worlds" / "kibot_one_obstacles.world.sdf"
    sim_with_bridge_launch = sim_pkg_share / "launch" / "sim_with_bridge.launch.py"
    slam_launch = sim_pkg_share / "launch" / "slam.launch.py"
    nav2_navigation_launch = nav2_bringup_share / "launch" / "navigation_launch.py"
    nav2_rviz_config = nav2_bringup_share / "rviz" / "nav2_default_view.rviz"
    nav2_params = sim_pkg_share / "config" / "nav2_params.yaml"

    world_arg = DeclareLaunchArgument(
        name="world",
        default_value=str(default_world),
        description="Gazebo 世界文件的绝对路径。",
    )
    params_file_arg = DeclareLaunchArgument(
        name="params_file",
        default_value=str(nav2_params),
        description="Nav2 参数文件路径。",
    )
    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description="Nav2 是否使用仿真时间。",
    )
    autostart_arg = DeclareLaunchArgument(
        name="autostart",
        default_value="true",
        description="是否自动激活 Nav2 lifecycle nodes。",
    )
    use_composition_arg = DeclareLaunchArgument(
        name="use_composition",
        default_value="False",
        description="是否使用 Nav2 组合节点容器。",
    )
    use_respawn_arg = DeclareLaunchArgument(
        name="use_respawn",
        default_value="False",
        description="Nav2 节点退出后是否自动重启。",
    )
    log_level_arg = DeclareLaunchArgument(
        name="log_level",
        default_value="info",
        description="Nav2 日志等级。",
    )
    start_sim_arg = DeclareLaunchArgument(
        name="start_sim",
        default_value="true",
        description="是否同时启动 Gazebo 和 ros_gz_bridge。",
    )
    run_on_start_arg = DeclareLaunchArgument(
        name="run_on_start",
        default_value="true",
        description="是否使用 -r 让 Gazebo 启动后立即运行仿真。",
    )
    start_slam_arg = DeclareLaunchArgument(
        name="start_slam",
        default_value="true",
        description="是否同时启动 slam_toolbox。",
    )
    start_nav2_arg = DeclareLaunchArgument(
        name="start_nav2",
        default_value="true",
        description="是否启动 Nav2 navigation stack。",
    )
    use_lidar_static_tf_arg = DeclareLaunchArgument(
        name="use_lidar_static_tf",
        default_value="true",
        description="透传给 slam.launch.py，用于补齐 base_link -> lidar_link。",
    )
    use_rviz_arg = DeclareLaunchArgument(
        name="use_rviz",
        default_value="false",
        description="是否启动 RViz Nav2 默认视图。",
    )
    check_runtime_deps_arg = DeclareLaunchArgument(
        name="check_runtime_deps",
        default_value="true",
        description="启动前是否检查 Nav2/FastCDR 运行库兼容性。",
    )

    check_runtime_deps = OpaqueFunction(function=_check_nav2_runtime_deps)

    start_sim = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(str(sim_with_bridge_launch)),
        launch_arguments={
            "world": LaunchConfiguration("world"),
            "run_on_start": LaunchConfiguration("run_on_start"),
        }.items(),
        condition=IfCondition(LaunchConfiguration("start_sim")),
    )

    start_slam = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(str(slam_launch)),
        launch_arguments={
            "use_lidar_static_tf": LaunchConfiguration("use_lidar_static_tf"),
        }.items(),
        condition=IfCondition(LaunchConfiguration("start_slam")),
    )

    start_nav2 = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(str(nav2_navigation_launch)),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "autostart": LaunchConfiguration("autostart"),
            "params_file": LaunchConfiguration("params_file"),
            "use_composition": LaunchConfiguration("use_composition"),
            "use_respawn": LaunchConfiguration("use_respawn"),
            "log_level": LaunchConfiguration("log_level"),
        }.items(),
        condition=IfCondition(LaunchConfiguration("start_nav2")),
    )

    start_rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", str(nav2_rviz_config)],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    return LaunchDescription([
        world_arg,
        params_file_arg,
        use_sim_time_arg,
        autostart_arg,
        use_composition_arg,
        use_respawn_arg,
        log_level_arg,
        start_sim_arg,
        run_on_start_arg,
        start_slam_arg,
        start_nav2_arg,
        use_lidar_static_tf_arg,
        use_rviz_arg,
        check_runtime_deps_arg,
        check_runtime_deps,
        start_sim,
        start_slam,
        start_nav2,
        start_rviz,
    ])
