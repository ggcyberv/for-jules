import heapq
from typing import List, Tuple, Dict, Optional
from engine.map import GameMap

def get_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    # Using Chebyshev distance for 8-directional movement
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def astar(game_map: GameMap, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    if start == end:
        return [start]

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    cost_so_far: Dict[Tuple[int, int], float] = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == end:
            break

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                next_node = (current[0] + dx, current[1] + dy)
                tile = game_map.get_tile(next_node[0], next_node[1])

                if tile:
                    new_cost = cost_so_far[current] + tile.movement_cost
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + get_distance(next_node, end)
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current

    if end not in came_from:
        return None

    # Reconstruct path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
