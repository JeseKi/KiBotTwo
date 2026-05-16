# 运行依赖

## 为什么需要这一页

Nav2 在运行时依赖 ROS2 的 DDS / FastCDR 类型支持库。当前项目接入 Nav2 后，如果本机 Jazzy 包版本不一致，`controller_server` 会在启动后崩溃，而不是表现为普通参数错误。

本项目已经遇到过这个错误：

```text
symbol lookup error:
/opt/ros/jazzy/lib/libnav2_msgs__rosidl_typesupport_fastrtps_cpp.so:
undefined symbol: eprosima::fastcdr::Cdr::serialize(unsigned int)
```

这表示 `nav2_msgs` 等 Nav2 包较新，但 `ros-jazzy-fastcdr` / FastRTPS 相关包仍是旧版本。

## 先运行检查脚本

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

如果检查通过，再进入 build 和 launch。

## 推荐安装或升级

如果检查脚本提示 FastCDR 符号缺失，执行：

```bash
sudo apt-get update
sudo apt-get install -y \
  ros-jazzy-fastcdr \
  ros-jazzy-fastrtps \
  ros-jazzy-rmw-fastrtps-cpp \
  ros-jazzy-rmw-fastrtps-shared-cpp \
  ros-jazzy-rosidl-typesupport-fastrtps-c \
  ros-jazzy-rosidl-typesupport-fastrtps-cpp \
  ros-jazzy-rmw-cyclonedds-cpp
```

然后重新加载环境：

```bash
source .vscode/project-terminal-init.sh
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

`nav2.launch.py` 默认也会执行同类检查。依赖不满足时，它会在启动 Nav2 之前失败并打印安装命令。临时绕过方式是：

```bash
ros2 launch kibot_one_sim nav2.launch.py check_runtime_deps:=false
```

只建议在排查 launch 参数时短暂使用，不建议用于实际导航。

## 已确认的本机问题

历史问题：

- 当前 `ros-jazzy-nav2-msgs` 是 `1.3.11-1noble.20260412.044112`。
- 旧的 `ros-jazzy-fastcdr` 是 `2.2.5-1noble.20260121.175748`。
- apt 源中的 `ros-jazzy-fastcdr` 候选版本是 `2.2.7-1noble.20260225.051855`。
- 下载并解包候选版本后，确认它导出 `eprosima::fastcdr::Cdr::serialize(unsigned int)`。

已验证修复：

- 用户重新安装依赖后，`ros-jazzy-fastcdr` 为 `2.2.7-1noble.20260225.051855`。
- `/opt/ros/jazzy/lib/libfastcdr.so.2` 已导出 `eprosima::fastcdr::Cdr::serialize(unsigned int)`。
- `src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh` 通过。

如果换机器或重装 ROS2，仍然先运行检查脚本；不要跳过依赖检查直接调 Nav2 参数。

## 不建议的修复

不要通过把 `/opt/ros/kilted` 的库混进 Jazzy 的 `LD_LIBRARY_PATH` 来绕过这个问题。虽然本机 Kilted 的 `libfastcdr.so.2.3.5` 导出了缺失符号，但跨 ROS 发行版混用运行库会制造更隐蔽的问题。
