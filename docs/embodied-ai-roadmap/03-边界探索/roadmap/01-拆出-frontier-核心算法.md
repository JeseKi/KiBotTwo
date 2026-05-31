# 01-拆出 frontier 核心算法

## 本节目标

先实现一个不依赖 ROS2 node 生命周期的核心模块，把 OccupancyGrid 的扁平数组转换成可排序的 frontier 候选。

本节不要从 `.bak` 文件复制代码。创建空文件后，按下面片段顺序写入；除片段要求外，不新增额外 helper、import 或测试。

## 为什么现在做

探索失败时最难排查的是“地图算法错了”还是“ROS2 runtime 没接通”。先把算法拆出来单测，可以在不启动 Gazebo、SLAM 和 Nav2 的情况下验证核心判断。

本节需要参考：

- `../reference/frontier-contract.md`
- `../reference/file-plan.md`

## 第一步：创建核心算法文件并写入 imports 与 dataclass

创建文件：

```text
src/kibot_one_control/kibot_one_control/frontier_core.py
```

从空文件开始，先写入：

```python
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Iterable, Sequence


@dataclass(frozen=True)
class GridInfo:
    width: int
    height: int
    resolution: float
    origin_x: float
    origin_y: float


@dataclass(frozen=True)
class FrontierCandidate:
    key: str
    map_x: float
    map_y: float
    size: int
    distance: float
    score: float
```

`GridInfo` 是从 `OccupancyGrid.info` 提取出来的最小信息；`FrontierCandidate` 是后续 ROS2 节点要发送给 Nav2 的目标描述。

## 第二步：实现候选提取入口

紧接上一步，在同一个文件继续追加：

```python


def find_frontier_candidates(
    data: Sequence[int],
    info: GridInfo,
    robot_x: float,
    robot_y: float,
    *,
    min_frontier_size: int = 3,
    min_goal_distance: float = 0.35,
    max_goal_distance: float = 3.0,
    free_threshold: int = 20,
) -> list[FrontierCandidate]:
    """Return scored frontier centroids from an OccupancyGrid-like array."""
    _validate_grid(data, info)

    frontier_cells = {
        index
        for index, value in enumerate(data)
        if _is_unknown(value)
        and any(_is_free(data[neighbor], free_threshold) for neighbor in _neighbors4(index, info))
    }

    candidates: list[FrontierCandidate] = []
    visited: set[int] = set()
    for start in sorted(frontier_cells):
        if start in visited:
            continue

        component = _collect_component(start, frontier_cells, visited, info)
        if len(component) < min_frontier_size:
            continue

        goal_x, goal_y = _component_free_centroid(component, data, info, free_threshold)
        distance = math.hypot(goal_x - robot_x, goal_y - robot_y)
        if distance < min_goal_distance or distance > max_goal_distance:
            continue

        # Prefer larger frontiers, but keep the action goal on the known-free side of the boundary.
        score = float(len(component)) - distance
        candidates.append(
            FrontierCandidate(
                key=_component_key(component, info),
                map_x=goal_x,
                map_y=goal_y,
                size=len(component),
                distance=distance,
                score=score,
            )
        )

    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
```

这里有三个细节必须保持一致：

- `frontier_cells` 用 4 邻域判断 unknown 是否贴着 free cell。
- component 用 `_collect_component()` 的 8 邻域合并。
- `map_x` / `map_y` 用 free-side centroid，不用 unknown component centroid。

## 第三步：实现冷却过滤和基础判断

继续追加：

```python


def filter_cooldown_candidates(
    candidates: Iterable[FrontierCandidate],
    cooled_frontiers: dict[str, float],
    now_seconds: float,
) -> list[FrontierCandidate]:
    return [
        candidate
        for candidate in candidates
        if cooled_frontiers.get(candidate.key, 0.0) <= now_seconds
    ]


def _validate_grid(data: Sequence[int], info: GridInfo) -> None:
    if info.width <= 0 or info.height <= 0:
        raise ValueError("grid width and height must be positive")
    if len(data) != info.width * info.height:
        raise ValueError("grid data length does not match width * height")


def _is_unknown(value: int) -> bool:
    return value < 0


def _is_free(value: int, free_threshold: int) -> bool:
    return 0 <= value <= free_threshold
```

`_validate_grid()` 是为了让单测和运行时失败尽早暴露，不要默默在错误长度的数组上选点。

## 第四步：实现 4 邻域和 8 邻域

继续追加：

```python


def _neighbors4(index: int, info: GridInfo) -> Iterable[int]:
    x = index % info.width
    y = index // info.width
    if x > 0:
        yield index - 1
    if x < info.width - 1:
        yield index + 1
    if y > 0:
        yield index - info.width
    if y < info.height - 1:
        yield index + info.width


def _neighbors8(index: int, info: GridInfo) -> Iterable[int]:
    x = index % info.width
    y = index // info.width
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if 0 <= nx < info.width and 0 <= ny < info.height:
                yield ny * info.width + nx
```

4 邻域只用于判断 frontier 和寻找 free-side goal。8 邻域只用于合并同一条 frontier component。

## 第五步：实现 component 遍历和质心计算

继续追加：

```python


def _collect_component(
    start: int,
    frontier_cells: set[int],
    visited: set[int],
    info: GridInfo,
) -> list[int]:
    component: list[int] = []
    queue: deque[int] = deque([start])
    visited.add(start)

    while queue:
        index = queue.popleft()
        component.append(index)
        for neighbor in _neighbors8(index, info):
            if neighbor in frontier_cells and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return component


def _component_centroid(component: Sequence[int], info: GridInfo) -> tuple[float, float]:
    total_x = 0.0
    total_y = 0.0
    for index in component:
        world_x, world_y = _index_to_world(index, info)
        total_x += world_x
        total_y += world_y
    return total_x / len(component), total_y / len(component)
```

`_collect_component()` 使用 `deque` 做 BFS，保证遍历顺序稳定。`_component_centroid()` 用 cell center 转世界坐标。

## 第六步：实现 free-side centroid、坐标转换和 key

最后追加：

```python


def _component_free_centroid(
    component: Sequence[int],
    data: Sequence[int],
    info: GridInfo,
    free_threshold: int,
) -> tuple[float, float]:
    free_neighbors = {
        neighbor
        for index in component
        for neighbor in _neighbors4(index, info)
        if _is_free(data[neighbor], free_threshold)
    }
    if not free_neighbors:
        return _component_centroid(component, info)
    return _component_centroid(sorted(free_neighbors), info)


def _index_to_world(index: int, info: GridInfo) -> tuple[float, float]:
    x = index % info.width
    y = index // info.width
    return (
        info.origin_x + (x + 0.5) * info.resolution,
        info.origin_y + (y + 0.5) * info.resolution,
    )


def _component_key(component: Sequence[int], info: GridInfo) -> str:
    centroid_x, centroid_y = _component_centroid(component, info)
    cell_x = int((centroid_x - info.origin_x) / info.resolution)
    cell_y = int((centroid_y - info.origin_y) / info.resolution)
    return f"{cell_x}:{cell_y}"
```

这里的 `key` 来自 unknown component centroid；Nav2 goal 来自 free-side centroid。不要把这两个概念合并。

## 第七步：创建核心算法测试文件

创建文件：

```text
src/kibot_one_control/test/test_frontier_core.py
```

从空文件写入以下测试。测试名、数据和断言值都要保持一致，因为它们同时约束算法行为和最终 patch。

```python
from kibot_one_control.frontier_core import GridInfo
from kibot_one_control.frontier_core import filter_cooldown_candidates
from kibot_one_control.frontier_core import find_frontier_candidates


def test_find_frontier_candidates_groups_unknown_cells_next_to_free_space() -> None:
    grid = GridInfo(width=5, height=5, resolution=1.0, origin_x=0.0, origin_y=0.0)
    data = [
        100, 100, 100, 100, 100,
        100, 0, 0, -1, 100,
        100, 0, 0, -1, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
    ]

    candidates = find_frontier_candidates(
        data,
        grid,
        robot_x=1.5,
        robot_y=1.5,
        min_frontier_size=2,
        max_goal_distance=5.0,
    )

    assert len(candidates) == 1
    assert candidates[0].key == "3:2"
    assert candidates[0].map_x == 2.5
    assert candidates[0].map_y == 2.0
    assert candidates[0].size == 2


def test_find_frontier_candidates_filters_small_and_far_frontiers() -> None:
    grid = GridInfo(width=5, height=5, resolution=1.0, origin_x=0.0, origin_y=0.0)
    data = [
        0, -1, 100, 100, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 0, -1,
        100, 100, 100, 0, -1,
    ]

    candidates = find_frontier_candidates(
        data,
        grid,
        robot_x=0.5,
        robot_y=0.5,
        min_frontier_size=2,
        max_goal_distance=2.0,
    )

    assert candidates == []


def test_filter_cooldown_candidates_removes_recent_failures() -> None:
    grid = GridInfo(width=5, height=5, resolution=1.0, origin_x=0.0, origin_y=0.0)
    data = [
        100, 100, 100, 100, 100,
        100, 0, 0, -1, 100,
        100, 0, 0, -1, 100,
        100, 100, 100, 100, 100,
        100, 100, 100, 100, 100,
    ]
    candidates = find_frontier_candidates(data, grid, 1.5, 1.5, min_frontier_size=2, max_goal_distance=5.0)

    assert filter_cooldown_candidates(candidates, {candidates[0].key: 20.0}, now_seconds=10.0) == []
    assert filter_cooldown_candidates(candidates, {candidates[0].key: 20.0}, now_seconds=21.0) == candidates
```

## 做完应该看到什么

完成本节后，可以在不启动 ROS2 图的情况下运行：

```bash
source .vscode/project-terminal-init.sh
PYTHONPATH=src/kibot_one_control python3 -m pytest -q src/kibot_one_control/test/test_frontier_core.py
```

期望结果：

```text
3 passed
```

## 本节小结

本节交付的是一个纯算法层：输入地图数组和机器人位置，输出按分数排序的 frontier goal。下一节把它接到 ROS2 的 `/map`、TF 和 Nav2 action。
