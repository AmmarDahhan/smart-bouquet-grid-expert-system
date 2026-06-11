from utils import manhattan_distance

WAREHOUSE_POS = (2, 3)

PAVILION_COORDS = {
    'p1': (4, 2),
    'p2': (3, 4),
    'p3': (5, 4),
    'p4': (2, 5),
}

PAVILION_FLOWER = {
    'p1': 'rose',
    'p2': 'tulip',
    'p3': 'orchid',
    'p4': 'juliet_rose',
}


def optimal_remaining_cost(robot_x, robot_y, carried_flowers, remaining_pavs):
    wx, wy = WAREHOUSE_POS

    if not remaining_pavs:
        return 0.0

    dist_to_wh = manhattan_distance((robot_x, robot_y), (wx, wy))

    h = 0.0

    if carried_flowers:
        matched = None
        for pav in remaining_pavs:
            if PAVILION_FLOWER[pav] in carried_flowers:
                matched = pav
                break
        if matched:
            px, py = PAVILION_COORDS[matched]
            h += manhattan_distance((robot_x, robot_y), (px, py))
            h += manhattan_distance((px, py), (wx, wy))
            remaining_pavs = [p for p in remaining_pavs if p != matched]
        else:
            h += dist_to_wh
    else:
        h += dist_to_wh

    for pav in remaining_pavs:
        px, py = PAVILION_COORDS[pav]
        h += manhattan_distance((wx, wy), (px, py)) * 2

    return h


def heuristic_a_star(robot_x, robot_y, load_facts, need_facts):
    remaining_pavs = set()
    for pav, f, c, cnt in need_facts:
        if cnt > 0:
            remaining_pavs.add(pav)
    if not remaining_pavs:
        return 0.0

    carried = set()
    for f, c, cnt in load_facts:
        if cnt > 0:
            carried.add(f)

    return optimal_remaining_cost(robot_x, robot_y, carried, list(remaining_pavs))
