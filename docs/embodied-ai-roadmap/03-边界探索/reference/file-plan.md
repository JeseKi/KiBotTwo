# 文件计划

## Runtime 文件

| 文件 | 职责 |
| --- | --- |
| `src/kibot_one_control/kibot_one_control/frontier_core.py` | 纯算法：frontier 提取、分组、free-side goal、评分、冷却过滤 |
| `src/kibot_one_control/kibot_one_control/frontier_explorer.py` | ROS2 节点：订阅 `/map`、查询 TF、发送 `NavigateToPose`、处理结果 |
| `src/kibot_one_control/launch/frontier_exploration.launch.py` | 组合阶段 02 Nav2 bringup 与 `frontier_explorer` |
| `src/kibot_one_control/test/test_frontier_core.py` | 核心算法单测 |
| `src/kibot_one_control/setup.py` | 安装 launch 文件并注册 console script |
| `src/kibot_one_control/package.xml` | 声明 `action_msgs`、`nav2_msgs`、`tf2_ros` 依赖 |

## 文档文件

| 文件 | 职责 |
| --- | --- |
| `roadmap/` | 用户主线实施顺序 |
| `reference/frontier-contract.md` | 探索接口、候选定义和运行边界 |
| `reference/final-runtime/` | 探针成品 runtime 文件 `.bak` 副本 |
| `checklist/` | low / medium / high 分层验收 |
| `evidence/` | 探针分支、diff、验证命令和结果 |

## 不修改的文件

阶段 03 不修改：

- `src/kibot_one_sim/config/nav2_params.yaml`
- `src/kibot_one_sim/launch/nav2.launch.py`
- `src/kibot_one_control/kibot_one_control/follow_controller.py`
- `src/kibot_one_control/kibot_one_control/mode_control.py`

这些文件属于阶段 02 或旧控制链路。阶段 03 通过 action 契约接入，不直接改 Nav2 参数。
