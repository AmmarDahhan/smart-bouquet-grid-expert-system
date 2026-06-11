from __future__ import annotations

from copy import deepcopy
from functools import reduce
from typing import Dict, Iterable, Tuple, TypeVar


Position = Tuple[int, int]
T = TypeVar("T")


def in_bounds(pos: Position, width: int, height: int) -> bool:
    x, y = pos
    return 0 <= x <= width and 0 <= y <= height


def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def deep_copy(obj: T) -> T:
    return deepcopy(obj)


def total_nested_counts(load: Dict[str, Dict[str, int]]) -> int:
    return sum(map(sum, load.values()))


def total_needs(needs: Dict[str, int]) -> int:
    return sum(needs.values())


def max_from_iterable(values: Iterable[int]) -> int:
    values_list = list(values)
    return reduce(lambda a, b: a if a > b else b, values_list)


def path_to_text(path: Iterable[str]) -> str:
    return " -> ".join(path)
