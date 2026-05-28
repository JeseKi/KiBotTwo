# 文件计划

## 已新增

| 文件 | 作用 |
| --- | --- |
| `src/kibot_one_sim/config/nav2_params.yaml` | KiBotTwo 第一版 Nav2 参数 |
| `src/kibot_one_sim/launch/nav2.launch.py` | 仿真、SLAM、Nav2 的统一启动入口 |
| `src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh` | Nav2 运行依赖和 FastCDR 符号检查 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/evidence/reference-runtime.patch` | 阶段 02 成品分支的完整 runtime patch，用于文档复测完全一致审计 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/roadmap/` | 阶段 02 主阅读路径 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/reference/` | 阶段 02 接口和系统事实 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/reference/final-runtime/` | 成品分支 runtime 文件的 `.bak` 完整副本，作为手写合并后的最终答案 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/checklist/` | 阶段 02 分层验收 |
| `docs/embodied-ai-roadmap/02-Nav2-导航接入/evidence/` | 阶段 02 验证和 diff 摘要 |

## 已修改

| 文件 | 修改内容 |
| --- | --- |
| `src/kibot_one_sim/package.xml` | 增加 `nav2_bringup` 运行依赖 |
| `src/kibot_one_sim/CMakeLists.txt` | 安装 `scripts/` 目录 |
| `src/kibot_one_sim/launch/gazebo.launch.py` | 增加 `run_on_start` 参数，支持 Gazebo `-r` |
| `src/kibot_one_sim/launch/sim_with_bridge.launch.py` | 透传 `run_on_start` |
| `docs/embodied-ai-roadmap/index.md` | 更新阶段 02 状态和入口 |

## 成品一致性

阶段 02 的 runtime 成品以 `feat/02-Nav2-导航接入` 为准。共同 baseline 是：

```text
e9b6fa40f7b269d098611b64f983d914f916b84e
```

读者按 roadmap 手写完成后，以下 runtime 文件相对 baseline 的 diff 必须与 `../evidence/reference-runtime.patch` 完全一致：

```text
src/kibot_one_sim/CMakeLists.txt
src/kibot_one_sim/config/nav2_params.yaml
src/kibot_one_sim/config/ros_gz_bridge.yaml
src/kibot_one_sim/launch/gazebo.launch.py
src/kibot_one_sim/launch/nav2.launch.py
src/kibot_one_sim/launch/sim_with_bridge.launch.py
src/kibot_one_sim/package.xml
src/kibot_one_sim/scripts/check_nav2_runtime_deps.sh
```

只有 `docs/` 下的差异可以不同。runtime 文件不允许用“功能等价”替代完全一致。

如果手写片段合并时不确定最终结构，以 `final-runtime/` 里的同名 `.bak` 文件为准。`reference-runtime.patch` 用于 patch 级审计，`final-runtime/` 用于逐文件核对。

## 暂不修改

| 文件 | 原因 |
| --- | --- |
| `src/kibot_one_control/*` | 02 通过独立 launch 隔离旧控制链路，不重构控制节点 |
| `src/kibot_one_sim/launch/kibot_one.launch.py` | 保留旧跟随演示入口 |
| `src/kibot_one_sim/launch/slam.launch.py` | 复用阶段 01 的 SLAM 入口 |
