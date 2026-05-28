# Diff 摘要

## 功能代码

- 新增 `src/kibot_one_sim/config/nav2_params.yaml`。
- 修改 `src/kibot_one_sim/config/ros_gz_bridge.yaml`，把 Nav2 的 `/cmd_vel_smoothed` 桥接到 Gazebo diff drive。
- 新增 `src/kibot_one_sim/launch/nav2.launch.py`。
- 新增 `src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh`，用于提前发现 Nav2/FastCDR 运行库不一致。
- 修改 `src/kibot_one_sim/package.xml`，加入 `nav2_bringup`。
- 修改 `src/kibot_one_sim/CMakeLists.txt`，安装 `scripts/` 目录。
- 修改 `src/kibot_one_sim/launch/gazebo.launch.py` 和 `sim_with_bridge.launch.py`，增加 `run_on_start`，让 02 可以默认运行 Gazebo 仿真而不是停在暂停状态。

## 完整 runtime patch

阶段 02 的 runtime 成品 patch 已固化在：

```text
docs/embodied-ai-roadmap/02-Nav2-导航接入/evidence/reference-runtime.patch
```

它来自：

```bash
git diff --binary --no-ext-diff \
  e9b6fa40f7b269d098611b64f983d914f916b84e...feat/02-Nav2-导航接入 \
  -- \
  src/kibot_one_sim/CMakeLists.txt \
  src/kibot_one_sim/config/nav2_params.yaml \
  src/kibot_one_sim/config/ros_gz_bridge.yaml \
  src/kibot_one_sim/launch/gazebo.launch.py \
  src/kibot_one_sim/launch/nav2.launch.py \
  src/kibot_one_sim/launch/sim_with_bridge.launch.py \
  src/kibot_one_sim/package.xml \
  src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

文档复测时，读者按 roadmap 手写出的 runtime diff 必须与该 patch 完全一致。只有 `docs/` 下的差异可以不同。

成品 runtime 文件的 `.bak` 完整副本已固化在：

```text
docs/embodied-ai-roadmap/02-Nav2-导航接入/reference/final-runtime/src/kibot_one_sim/
```

`roadmap/` 章节里的代码片段用于解释实现过程；最终合并结果以这些 `.bak` 完整副本为准。

## 文档

- 新增阶段 02 的 `roadmap/`、`reference/`、`checklist/` 和 `evidence/`。
- 更新顶层 `docs/embodied-ai-roadmap/index.md` 和阶段 02 教程，记录依赖检查、运行命令和验证结论。
- 新增 `reference/dependencies.md`，把 Nav2 运行依赖、安装命令和已确认的 FastCDR 问题写入教程。

## 关键取舍

- 不把 Nav2 塞进旧 `kibot_one.launch.py`，避免旧控制节点和 Nav2 争夺 `/cmd_vel`。
- 复用阶段 01 的 `slam.launch.py`，让 Nav2 专注处理导航层。
- 第一版使用 `base_link`，不引入 `base_footprint`。
- 第一版保留 Nav2 bringup 的标准 navigation stack，收敛机器人半径、速度、加速度、planner tolerance 和 goal tolerance。
- global costmap 使用 rolling obstacle/inflation 配置，避免 SLAM 初始小地图和 unknown 区域阻断探索目标执行。
- `nav2.launch.py` 默认 `run_on_start:=true`，因为 Nav2 lifecycle 激活需要 `odom -> base_link` TF，而暂停的 Gazebo 不会及时提供这条链路。
