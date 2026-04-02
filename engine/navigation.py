import heapq
from typing import List, Tuple, Dict, Optional
from engine.map import GameMap

def get_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
    # Use cube coordinates for hexagonal distance
    # Convert axial/offset to cube (pointy-top odd-r)
    def offset_to_cube(pos: Tuple[int, int]):
        x = pos[0] - (pos[1] - (pos[1] & 1)) // 2
        z = pos[1]
        y = -x - z
        return (x, y, z)

    c1 = offset_to_cube(p1)
    c2 = offset_to_cube(p2)
    return max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1]), abs(c1[2] - c2[2]))

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

        # Use hexagonal neighbors
        for next_node in game_map.get_neighbors(current[0], current[1]):
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
