# mypy: disable-error-code="import-untyped"

from pathlib import Path
import os

from ament_index_python.packages import get_package_share_directory # type: ignore
from launch import LaunchDescription # type: ignore
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable # type: ignore
from launch.conditions import IfCondition, UnlessCondition # type: ignore
from launch.substitutions import LaunchConfiguration # type: ignore


def generate_launch_description():
    pkg_share = Path(get_package_share_directory('kibot_one_sim'))
    default_world = pkg_share / 'worlds' / 'kibot_one.world.sdf'
    models_path = pkg_share / 'models'

    existing_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    resource_path = (
        f'{existing_resource_path}:{models_path}' if existing_resource_path else str(models_path)
    )

    world_arg = DeclareLaunchArgument(
        name='world',
        default_value=str(default_world),
        description='Gazebo 世界文件的绝对路径。',
    )
    run_on_start_arg = DeclareLaunchArgument(
        name='run_on_start',
        default_value='false',
        description='是否使用 -r 让 Gazebo 启动后立即运行仿真。',
    )

    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=resource_path,
    )

    start_gazebo_paused = ExecuteProcess(
        cmd=['gz', 'sim', '-v', '4', LaunchConfiguration('world')],
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('run_on_start')),
    )

    start_gazebo_running = ExecuteProcess(
        cmd=['gz', 'sim', '-v', '4', '-r', LaunchConfiguration('world')],
        output='screen',
        condition=IfCondition(LaunchConfiguration('run_on_start')),
    )

    return LaunchDescription([
        world_arg,
        run_on_start_arg,
        gz_resource_path,
        start_gazebo_paused,
        start_gazebo_running,
    ])
