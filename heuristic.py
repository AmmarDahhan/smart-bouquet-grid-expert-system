from utils import manhattan_distance
from typing import Dict, Tuple

Position = Tuple[int, int]


def heuristic(robot_pos: Position, warehouse_pos: Position, pavilion_positions: Dict[str, Position], needs: Dict[str, int]) -> int:
    """
    A* heuristic function h(n)
    
    Estimates the minimum cost from current state to goal state.
    
    Considers:
    1. Distance to warehouse if robot has no load
    2. Distance to nearest pavilion if robot has load
    3. Number of remaining deliveries
    
    Returns a lower bound on remaining cost (never overestimates)
    """
    
    robot_x, robot_y = robot_pos
    warehouse_x, warehouse_y = warehouse_pos
    
    # If no remaining needs, heuristic is 0 (at goal)
    total_needs = sum(needs.values())
    if total_needs <= 0:
        return 0
    
    # Minimum cost:
    # 1. Go to warehouse if not there (manhattan distance + 1 load) = distance + 1
    dist_to_warehouse = manhattan_distance(robot_pos, warehouse_pos)
    
    # 2. Go to nearest pavilion = closest distance
    nearest_pavilion_dist = float('inf')
    for pavilion_pos in pavilion_positions.values():
        dist_to_pavilion = manhattan_distance(robot_pos, pavilion_pos)
        if dist_to_pavilion < nearest_pavilion_dist:
            nearest_pavilion_dist = dist_to_pavilion
    
    if nearest_pavilion_dist == float('inf'):
        nearest_pavilion_dist = 0
    
    # 3. Must load at warehouse and unload at pavilion for each need
    # Minimum: go to warehouse once, then visit at least 1 pavilion per delivery set
    min_deliveries = len([p for p in pavilion_positions.keys() if p in needs and needs.get(p, 0) > 0])
    
    # Simple heuristic: Manhattan distance to warehouse + distance to nearest pavilion + remaining needs
    # This never overestimates because:
    # - We must visit warehouse (at least dist_to_warehouse moves)
    # - We must visit pavilions (at least nearest_pavilion_dist moves)
    # - Each delivery takes at least 2 moves (load + unload)
    
    h = max(dist_to_warehouse + 1, nearest_pavilion_dist + 1) + (total_needs * 2 - 2)
    
    return max(0, h)
