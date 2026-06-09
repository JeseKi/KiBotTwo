# 验证记录

## 探针验证

日期：2026-06-08

分支与提交：

- `roadmap-probe/04-vision-flag-detection`
- `0406c08`

命令：

```bash
source .vscode/project-terminal-init.sh
colcon build --packages-select kibot_one_interface kibot_one_control kibot_one_sim
python -m pytest -q src/kibot_one_control/test/test_frontier_core.py src/kibot_one_control/test/test_flag_detection_core.py
```

结果：

- 构建通过：`3 packages finished`。
- 直接 pytest 通过：`6 passed in 0.01s`。

`colcon test` 结果：

```bash
colcon test --packages-select kibot_one_control --event-handlers console_direct+
```

返回：

```text
NO TESTS RAN
Failed <<< kibot_one_control [exited with code 5]
```

判读：

- 这是当前 `kibot_one_control` 测试发现配置缺口。
- 阶段 04 的核心算法仍通过直接 pytest 验证。
- 后续可以单独整理 `ament_python` pytest 集成，不阻塞本阶段 detection contract。

## launch 冒烟

命令：

```bash
timeout 20s ros2 launch kibot_one_control flag_detection.launch.py start_sim:=true run_on_start:=true
ros2 topic list
```

结果：

- `/camera/image_raw` 出现在 ROS graph。
- `/flag_detection` 出现在 ROS graph。

读取一条检测消息：

```bash
ros2 topic echo --once /flag_detection
```

结果：

- 收到 `detected: true`。
- `header.frame_id: camera_link`。
- `image_width: 320`，`image_height: 240`。
- 消息不包含全局位姿。

## 文档复测

### 第一次复测：未通过

日期：2026-06-08

复测结果：

- runtime 行为通过：构建、直接 pytest、launch、topic list 和 `/flag_detection` echo 均成功。
- patch 审计未通过：复测实现把 `flag_detector` console script 放在 `frontier_explorer` 后面，而参考 patch 放在 `frontier_explorer` 前面。
- 复测还发现临时 worktree 缺少 `install/setup.sh` / `.venv` 时，`.vscode/project-terminal-init.sh` 不能直接用于首次 bootstrap。

修正：

- `roadmap/04-接入-flag-detector-节点与-launch.md` 已补充 `setup.py` 中 launch data file 和 console script 的精确插入位置。
- `reference/dependencies.md` 与 `evidence/usage.md` 已补充临时 worktree 首次构建说明。

### 下一次复测要求

需要复测者从干净 baseline 只按 `roadmap/` 手写 runtime，运行 `evidence/usage.md` 中的构建、pytest、launch 冒烟和 `/flag_detection` echo，然后把非 `docs/` patch 与 `evidence/reference-runtime.patch` 做字节级一致审计。

### 第二次复测：通过

日期：2026-06-08

复测结果：

- 临时 worktree 首次 `source .vscode/project-terminal-init.sh` 因缺少 `install/setup.sh` 和 `.venv/bin/activate` 失败，复测者按 `reference/dependencies.md` 的 bootstrap 说明处理。
- bootstrap 构建通过：`Summary: 3 packages finished [6.17s]`。
- 直接 pytest 通过：`6 passed in 0.01s`。
- launch/topic 验证通过：`/camera/image_raw` 和 `/flag_detection` 均存在。
- `/flag_detection` echo 收到消息：`frame_id: camera_link`、`detected: true`、`image_width: 320`、`image_height: 240`。
- 复测者清理后检查残留进程，没有实际残留。

patch 审计：

- 复测者已对新增 runtime 文件执行 `git add -N`。
- 复测 worktree 中 `git diff --no-ext-diff main -- src` 与 `evidence/reference-runtime.patch` 在 CRLF/LF 归一化后字节一致。
- 归一化后 sha256 均为 `dbf161fe86e7a3e0b7c20f47c4f13cf5f2514ab825ee225c2c163b5886eeecef`。

残留风险：

- 临时 worktree 需要 bootstrap 环境，已写入 `reference/dependencies.md` 和 `evidence/usage.md`。
- Ctrl-C 清理 launch 时，复测者观察到 `flag_detector` 的 rclpy shutdown traceback 和 `ros_gz_bridge` 清理阶段退出码 `-11`；检测链路验证已完成，且无残留进程。该清理行为后续如影响 CI 或演示体验，可在运行脚本层单独处理。

## 可阅读性重写

日期：2026-06-08

重写范围：

- `roadmap/index.md`
- `roadmap/01-定义视觉检测事件.md`
- `roadmap/02-接入前向相机与图像桥接.md`
- `roadmap/03-实现红色旗面检测核心.md`
- `roadmap/04-接入-flag-detector-节点与-launch.md`
- `roadmap/05-验证视觉闭环并交付契约.md`

重写结果：

- 保留代码片段、文件路径、实现顺序、验证命令和交付边界。
- 主线 roadmap 未包含 `.bak`、reference patch、字节级审计、sub agent 或 oracle 语境。
- 第 03 节增加算法职责表，第 04 节增加节点调用图，让读者先理解纯函数、回调和节点入口之间的关系。
- 将测试配置缺口、阶段不承诺内容和 topic 判读改写成工程化的分层验收说明。

## 可阅读性重写后复测：通过

日期：2026-06-08

复测结果：

- 临时 worktree 首次 `source .vscode/project-terminal-init.sh` 因缺少 `install/setup.sh` 和 `.venv/bin/activate` 失败，复测者按 `reference/dependencies.md` 的 bootstrap 说明处理。
- 构建通过：`Summary: 3 packages finished [1.45s]`。
- 直接 pytest 通过：`6 passed in 0.01s`。
- launch/topic 验证通过：`/camera/image_raw` 和 `/flag_detection` 均存在。
- `/camera/image_raw` header 为 `frame_id: camera_link`。
- `/flag_detection` echo 收到消息：`frame_id: camera_link`、`detected: true`、`image_width: 320`、`image_height: 240`、`pixel_count: 333`。

patch 审计：

- 复测者已对新增 runtime 文件执行 `git add -N`。
- 复测 worktree 中相对 `main` 的非 `docs/` patch 与 `evidence/reference-runtime.patch` 忽略 CRLF/LF 后一致。
- 归一化后字节数均为 `13332`。

收尾警告：

- Ctrl-C 关闭 launch 时，复测者观察到 `flag_detector` 的 rclpy shutdown 已调用异常，以及 bridge 进程退出码 `-11`。
- Gazebo 运行期间有 `gz_frame_id` SDF warning、Qt binding warning 和 `libEGL warning`。
- 上述警告没有阻止相机图像、检测消息和 patch 审计通过；复测后残留进程检查为空。
