#!/usr/bin/env bash
set -euo pipefail

missing=0

echo "[check] ROS_DISTRO=${ROS_DISTRO:-unset}"
if [[ "${ROS_DISTRO:-}" != "jazzy" ]]; then
  echo "[error] 请先 source ROS2 Jazzy 环境，例如：source .vscode/project-terminal-init.sh"
  missing=1
fi

if ! command -v ros2 >/dev/null 2>&1; then
  echo "[error] ros2 命令不可用。"
  missing=1
fi

required_packages=(
  nav2_bringup
  nav2_controller
  nav2_planner
  nav2_bt_navigator
  nav2_msgs
  slam_toolbox
  ros_gz_bridge
)

for package_name in "${required_packages[@]}"; do
  if ros2 pkg prefix "${package_name}" >/dev/null 2>&1; then
    echo "[ok] ros2 package ${package_name}"
  else
    echo "[error] 缺少 ROS2 package: ${package_name}"
    missing=1
  fi
done

fastcdr_lib="/opt/ros/jazzy/lib/libfastcdr.so.2"
if [[ -f "${fastcdr_lib}" ]]; then
  fastcdr_symbols="$(nm -D "${fastcdr_lib}" 2>/dev/null | c++filt)"
  if [[ "${fastcdr_symbols}" == *"eprosima::fastcdr::Cdr::serialize(unsigned int)"* ]]; then
    echo "[ok] ${fastcdr_lib} exports Cdr::serialize(unsigned int)"
  else
    echo "[error] ${fastcdr_lib} 缺少 Cdr::serialize(unsigned int)，Nav2 controller_server 会在运行时崩溃。"
    missing=1
  fi
else
  echo "[error] 未找到 ${fastcdr_lib}"
  missing=1
fi

if [[ "${missing}" -ne 0 ]]; then
  cat <<'EOF'

请更新 Nav2/Jazzy 运行依赖：

sudo apt-get update
sudo apt-get install -y \
  ros-jazzy-fastcdr \
  ros-jazzy-fastrtps \
  ros-jazzy-rmw-fastrtps-cpp \
  ros-jazzy-rmw-fastrtps-shared-cpp \
  ros-jazzy-rosidl-typesupport-fastrtps-c \
  ros-jazzy-rosidl-typesupport-fastrtps-cpp \
  ros-jazzy-rmw-cyclonedds-cpp

然后重新 source 环境并再次运行本检查。
EOF
  exit 1
fi

echo "[ok] Nav2 runtime dependencies look usable."
