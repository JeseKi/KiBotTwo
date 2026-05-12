# mypy: disable-error-code="import-untyped"

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description() -> LaunchDescription:
    pkg_share = Path(get_package_share_directory(package_name="kibot_one_sim"))
    slam_toolbox_share = Path(get_package_share_directory(package_name="slam_toolbox")) # 获取 SLAMBox 的 share 目录
    params_file = pkg_share / "config" / "slam_toolbox.yaml"
    online_async_launch = slam_toolbox_share / "launch" / "online_async_launch.py" # 获取在线 SLAM 的启动文件

    use_lidar_static_tf_arg = DeclareLaunchArgument(
        name="use_lidar_static_tf",
        default_value="true",
        description="如果 Gazebo 没有提供 base_link -> lidar_link, 就补一个静态 TF"
    )

    lidar_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="base_to_lidar_static_tf",
        arguments=["0.20","0.0","0.165","0.0","0.0","0.0","base_link","lidar_link"],
        condition=IfCondition(LaunchConfiguration(variable_name="use_lidar_static_tf"))
    )

    slam_toolbox = IncludeLaunchDescription( # 直接使用 SLAMBox 官方的启动文件，避免自己写
        launch_description_source=PythonLaunchDescriptionSource(str(online_async_launch)),
        launch_arguments={
            "slam_params_file": str(params_file),
            "use_sim_time": "true",
            "autostart": "true",
            "use_lifecycle_manager": "false",
        }.items(),
    )

    return LaunchDescription([
        use_lidar_static_tf_arg,
        lidar_static_tf,
        slam_toolbox
    ])
