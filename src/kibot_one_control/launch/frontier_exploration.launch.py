from pathlib import Path

from ament_index_python.packages import get_package_share_directory  # type: ignore
from launch import LaunchDescription  # type: ignore
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription  # type: ignore
from launch.conditions import IfCondition  # type: ignore
from launch.launch_description_sources import PythonLaunchDescriptionSource  # type: ignore
from launch.substitutions import LaunchConfiguration  # type: ignore
from launch_ros.actions import Node  # type: ignore

def generate_launch_description() -> LaunchDescription:
    sim_share = Path(get_package_share_directory(package_name="kibot_one_sim"))
    nav2_launch = sim_share / "launch" / "nav2.launch.py"

    world_arg = DeclareLaunchArgument(
        name="world",
        default_value=str(sim_share / "worlds" / "kibot_one_obstacles.world.sdf"),
        description="Gazebo 世界的绝对路径。"
    )
    use_rviz_arg = DeclareLaunchArgument(
        name="use_rviz",
        default_value="false",
        description="是否启动 RViz Nav2 默认视图"
    )
    start_explore_arg = DeclareLaunchArgument(
        name="start_explorer",
        default_value="true",
        description="是否启动 frontier_explorer 节点"
    )
    start_nav2 = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource(launch_file_path=str(nav2_launch)),
        launch_arguments={
            "world": LaunchConfiguration(variable_name="world"),
            "use_rviz": LaunchConfiguration(variable_name="use_rviz")
        }.items(),
    )
    
    explorer = Node(
        package="kibot_one_control",
        executable="frontier_explorer",
        name="frontier_explorer",
        output="screen",
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(predicate_expression=LaunchConfiguration(variable_name="start_explorer"))
    )

    return LaunchDescription(initial_entities=[
        world_arg,
        use_rviz_arg,
        start_explore_arg,
        start_nav2,
        explorer
    ])