from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Deque, Dict, Iterable, List, Sequence, Set, Tuple

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


def _validate_grid(data: Sequence[int], info: GridInfo) -> None:
    if info.width <= 0 or info.height <= 0:
        raise ValueError("栅格的宽度和高度必须有效")
    if len(data) != info.width * info.height:
        raise ValueError("栅格数据长度不等于栅格长*宽")


def filter_cooldown_candidates(
    candidates: Iterable[FrontierCandidate],
    cooled_frontiers: Dict[str, float],
    now_seconds: float,
) -> List[FrontierCandidate]:
    return [
        candidate
        for candidate in candidates
        if cooled_frontiers.get(candidate.key, 0.0) <= now_seconds
    ]


def _is_unknown(value: int) -> bool:
    return value < 0


def _is_free(value: int, free_threshold: int) -> bool:
    return 0 <= value <= free_threshold


def _neighbor4(index: int, info: GridInfo) -> Iterable[int]:
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


def _neighbor8(index, info: GridInfo) -> Iterable[int]:
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


def _component_free_centroid(
    component: Sequence[int],
    data: Sequence[int],
    info: GridInfo,
    free_threshold: int
) -> Tuple[float, float]:
    free_neighbors = {
        neighbor
        for index in component
        for neighbor in _neighbor4(index=index, info=info)
        if _is_free(value=data[neighbor], free_threshold=free_threshold)
    }

    if not free_neighbors:
        return _component_centroid(component=component, info=info)
    return _component_centroid(component=sorted(free_neighbors), info=info)


def _index_to_world(index: int, info: GridInfo) -> Tuple[float, float]:
    x = index % info.width
    y = index // info.width
    return(
        info.origin_x + (x + 0.5) * info.resolution,
        info.origin_y + (y + 0.5) * info.resolution
    )

def _component_key(component: Sequence[int], info: GridInfo) -> str:
    centroid_x, centroid_y = _component_centroid(component=component, info=info)
    cell_x = int((centroid_x - info.origin_x) / info.resolution)
    cell_y = int((centroid_y - info.origin_y) / info.resolution)
    return f"{cell_x}:{cell_y}"

def _collect_component(
    start: int, frontier_cells: Set[int], visited: Set[int], info: GridInfo
) -> List[int]:
    component: List[int] = []
    queue: Deque[int] = deque([start])
    visited.add(start)
    
    while queue:
        index = queue.popleft()
        component.append(index)
        for neighbor in _neighbor8(index=index, info=info):
            if neighbor in frontier_cells and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return component


def _component_centroid(
    component: Sequence[int], info: GridInfo
) -> Tuple[float, float]:
    total_x = 0.0
    total_y = 0.0

    for index in component:
        world_x, world_y = _index_to_world(index=index, info=info)
        total_x += world_x
        total_y += world_y

    return total_x / len(component), total_y / len(component)


def find_frontier_candidates(
    data: Sequence[int],
    info: GridInfo,
    robot_x: float,
    robot_y: float,
    *,
    min_frontier_size: int = 3,
    min_goal_distance: float = 0.35,
    max_goal_distance: float = 3,
    free_threshold: int = 20,
) -> List[FrontierCandidate]:
    _validate_grid(data=data, info=info)

    frontier_cells = {
        index
        for index, value in enumerate(data)
        if _is_unknown(value=value)
        and any(
            _is_free(value=data[neighbor], free_threshold=free_threshold)
            for neighbor in _neighbor4(index=index, info=info)
        )
    }

    candidates: List[FrontierCandidate] = []
    visited: Set[int] = set()
    for start in sorted(frontier_cells):
        if start in visited:
            continue
    
        component = _collect_component(start=start, frontier_cells=frontier_cells, visited=visited, info=info)
        if len(component) < min_frontier_size:
            continue
        
        goal_x, goal_y = _component_free_centroid(component=component, data=data, info=info, free_threshold=free_threshold)
        distance = math.hypot(goal_x - robot_x, goal_y - robot_y)
        if distance < min_goal_distance or distance > max_goal_distance:
            continue

        score = float(len(component)) - distance
        candidates.append(
            FrontierCandidate(
                key=_component_key(component=component, info=info),
                map_x=goal_x,
                map_y=goal_y,
                size=len(component),
                distance=distance,
                score=score
            )
        )
    
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)