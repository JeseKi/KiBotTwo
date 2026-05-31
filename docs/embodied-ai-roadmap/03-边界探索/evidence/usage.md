# 使用与验证记录

## 环境准备

```bash
source .vscode/project-terminal-init.sh
```

注意：这个脚本会 source 当前工作目录下的 `install/setup.sh` 和 `.venv/bin/activate`。如果在临时 git worktree 中复测，而该 worktree 还没有这些生成物，可以先在主 workspace source 环境，再切回临时 worktree 执行验证：

```bash
cd /home/jese--ki/Projects/dev/KiBots/KiBotTwo
source .vscode/project-terminal-init.sh
cd /tmp/kibot-redo-03
```

如果要运行 launch，先构建并加载 workspace：

```bash
colcon build --packages-select kibot_one_control
source install/setup.bash
```

## 静态与单测验证

```bash
python3 -m py_compile \
  src/kibot_one_control/kibot_one_control/frontier_core.py \
  src/kibot_one_control/kibot_one_control/frontier_explorer.py \
  src/kibot_one_control/launch/frontier_exploration.launch.py

PYTHONPATH=src/kibot_one_control \
  python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py
```

探针结果：

```text
3 passed in 0.01s
```

## Launch 冒烟

```bash
ros2 launch kibot_one_control frontier_exploration.launch.py --show-args
```

探针结果：参数正常展示，包含 `world`、`use_rviz`、`start_explorer` 和阶段 02 Nav2 参数。

不启动仿真时的节点冒烟：

```bash
timeout 8s ros2 launch kibot_one_control frontier_exploration.launch.py \
  start_sim:=false start_slam:=false start_nav2:=false check_runtime_deps:=false
```

探针结果：

```text
[frontier_explorer-1]: process started
```

退出码 `124` 是 `timeout` 主动截断，未出现 traceback。

## 短时完整仿真

```bash
timeout 35s ros2 launch kibot_one_control frontier_exploration.launch.py use_rviz:=false
```

关键观测：

```text
frontier_explorer: sending frontier 7:11 at (0.56, 0.06), size=30
bt_navigator: Action server is inactive. Rejecting the goal.
frontier_explorer: frontier goal 7:11 was rejected
...
lifecycle_manager_navigation: Managed nodes are active
...
frontier_explorer: sending frontier 7:11 at (0.56, 0.06), size=30
bt_navigator: Begin navigating from current location ... to (0.56, 0.06)
controller_server: Reached the goal!
bt_navigator: Goal succeeded
frontier_explorer: frontier goal 7:11 succeeded
frontier_explorer: sending frontier 8:18 at (0.64, 0.40), size=11
```

判定：

- 第一次 rejected 是 Nav2 lifecycle 尚未 active 的启动竞态。
- cooldown 后再次发送同一 frontier，并成功到达。
- 成功后 explorer 继续选择第二个 frontier。

## 收尾清理

短时仿真后检查残留进程：

```bash
pgrep -af 'gz sim server|frontier_explorer|controller_server|bt_navigator|async_slam_toolbox_node|bridge_node' || true
```

如看到残留 `gz sim server`，终止对应 PID 后再继续下一次验证。

## runtime patch 完全一致审计

如果复测 worktree 中有新增文件，先把 runtime 文件加入 intent-to-add，否则 `git diff` 不会包含 untracked 文件：

```bash
git add -N \
  src/kibot_one_control/package.xml \
  src/kibot_one_control/setup.py \
  src/kibot_one_control/kibot_one_control/frontier_core.py \
  src/kibot_one_control/kibot_one_control/frontier_explorer.py \
  src/kibot_one_control/launch/frontier_exploration.launch.py \
  src/kibot_one_control/test/test_frontier_core.py
```

```bash
git diff --binary --no-ext-diff \
  6f0ef3bb59e898d3f11ecabb04518b37321be9b5...roadmap-probe/03-frontier-exploration \
  -- . ':(exclude)docs/**' > /tmp/reference-03.diff

git diff --binary --no-ext-diff \
  6f0ef3bb59e898d3f11ecabb04518b37321be9b5 \
  -- . ':(exclude)docs/**' > /tmp/redo-03.diff

diff -u docs/embodied-ai-roadmap/03-边界探索/evidence/reference-runtime.patch /tmp/reference-03.diff
diff -u docs/embodied-ai-roadmap/03-边界探索/evidence/reference-runtime.patch /tmp/redo-03.diff
```

`diff` 没有输出才算通过。
