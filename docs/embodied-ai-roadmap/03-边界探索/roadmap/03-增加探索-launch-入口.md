# 03-增加探索 launch 入口

## 本节目标

新增 `frontier_exploration.launch.py`，让用户可以一条命令启动阶段 02 的 Nav2 bringup 和阶段 03 的 `frontier_explorer`。

本节从空文件开始按片段顺序追加。不要新增其他 launch action。

## 为什么现在做

探索不是孤立节点。它需要 Gazebo、bridge、SLAM、Nav2 和 TF 都在同一运行图里。复用阶段 02 的 `nav2.launch.py` 可以避免重复维护仿真和导航参数。

## 第一步：创建 launch 文件并写入 imports

创建文件：

```text
src/kibot_one_control/launch/frontier_exploration.launch.py
```

从空文件写入：

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

## 第二步：定位阶段 02 的 Nav2 launch

继续追加：

```python


def generate_launch_description() -> LaunchDescription:
    sim_share = Path(get_package_share_directory("kibot_one_sim"))
    nav2_launch = sim_share / "launch" / "nav2.launch.py"
```

这里依赖阶段 02 已经安装的 `kibot_one_sim` launch 入口。

## 第三步：声明三个参数

仍在 `generate_launch_description()` 中继续追加：

```python

    world_arg = DeclareLaunchArgument(
        "world",
        default_value=str(sim_share / "worlds" / "kibot_one_obstacles.world.sdf"),
        description="Gazebo 世界文件的绝对路径。",
    )
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="false",
        description="是否启动 RViz Nav2 默认视图。",
    )
    start_explorer_arg = DeclareLaunchArgument(
        "start_explorer",
        default_value="true",
        description="是否启动 frontier_explorer 节点。",
    )
```

只暴露 `world`、`use_rviz`、`start_explorer`。其他 Nav2 参数继续由阶段 02 launch 管理。

## 第四步：Include 阶段 02 的 Nav2 launch

继续追加：

```python

    start_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_launch)),
        launch_arguments={
            "world": LaunchConfiguration("world"),
            "use_rviz": LaunchConfiguration("use_rviz"),
        }.items(),
    )
```

不要在这里重新声明 Nav2 参数；阶段 02 已经负责 `params_file`、SLAM、bridge、lifecycle 和 runtime dependency check。

## 第五步：启动 explorer 节点

继续追加：

```python

    explorer = Node(
        package="kibot_one_control",
        executable="frontier_explorer",
        name="frontier_explorer",
        output="screen",
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(LaunchConfiguration("start_explorer")),
    )
```

`use_sim_time` 必须跟 Nav2 和 SLAM 一致，否则 goal timeout 和 TF 查询会变得难以解释。

## 第六步：返回 LaunchDescription

最后追加：

```python

    return LaunchDescription([
        world_arg,
        use_rviz_arg,
        start_explorer_arg,
        start_nav2,
        explorer,
    ])
```

`return LaunchDescription([...])` 使用列表形式，不要改成 `initial_entities=`，以保持最终 patch 一致。

## 做完应该看到什么

完成后重新构建并 source：

```bash
source .vscode/project-terminal-init.sh
colcon build --packages-select kibot_one_control
source install/setup.bash
```

运行：

```bash
ros2 launch kibot_one_control frontier_exploration.launch.py --show-args
```

应该看到 `world`、`use_rviz`、`start_explorer`，以及从阶段 02 Nav2 launch 透传出来的参数。

## 本节小结

现在阶段 03 有了独立入口。下一节用这个入口做代码验证和短时仿真验证。
