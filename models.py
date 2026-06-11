from experta import *


class State(Fact):
    """
    Search state
    """
    pass


class Warehouse(Fact):
    """
    Warehouse position
    """
    pass


class Pavilion(Fact):
    """
    Pavilion static information
    """
    pass


class Need(Fact):
    """
    Remaining pavilion needs
    """
    pass


class Load(Fact):
    """
    Robot carried bouquets
    """
    pass


class Grid(Fact):
    """
    Grid dimensions
    """
    pass


class Goal(Fact):
    """
    Goal reached
    """
    pass

class VisitedState(Fact):
    """
    Visited search state
    """
    pass

class StateCounter(Fact):
    """
    Generates unique state ids
    """
    pass

class StateSignature(Fact):
    """
    Unique generated state signature (x, y, load_hash)
    """
    load_hash = Field(int, default=0)

class Target(Fact):
    """
    Heuristic target for DFS guidance
    """
    pass

class CandidateMove(Fact):
    """
    Proposed next move
    """
    load_hash = Field(int, default=0)

class ValidMove(Fact):
    """
    Valid legal move
    """
    pass

class RobotAtWarehouse(Fact):
    """
    Robot is currently inside warehouse
    """
    pass

class Bouquet(Fact):
    """
    Flower bouquet
    """
    pass

class RobotLoad(Fact):
    """
    Current robot load
    """
    pass

class RobotHasLoad(Fact):
    """
    Robot currently carries bouquets
    """
    pass

class Pavilion(Fact):
    """
    Pavilion inside gallery
    """
    pass

class RobotAtPavilion(Fact):
    """
    Robot currently inside pavilion
    """
    pass

class PavilionNeed(Fact):
    """
    Pavilion remaining needs
    """
    pass

class FinalState(Fact):
    """
    Final successful state
    """
    pass

class TracePath(Fact):
    """
    Request path tracing
    """
    pass

class MatchingLoad(Fact):
    """
    Robot carries bouquet matching pavilion need
    """
    pass

class AllNeedsCompleted(Fact):
    """
    All pavilion needs have been completed
    """
    pass

class Delivered(Fact):
    """
    Record of a delivered bouquet
    """
    pass

class ActiveState(Fact):
    """
    Currently active search state
    """
    pass

class MovesGenerated(Fact):
    """
    Moves have been generated for the state
    """
    state_id = Field(int)

class StateExpanded(Fact):
    """
    State has been expanded in search
    """
    state_id = Field(int)

class StateFValue(Fact):
    """
    F value for A* (g + h)
    """
    state_id = Field(int)
    f_value = Field(int)

class OpenState(Fact):
    """
    Open search state awaiting expansion
    """
    state_id = Field(int)
    f_value = Field(float, default=0.0)

class PathTraced(Fact):
    """
    State has been traced in path output
    """
    state_id = Field(int)

class LoadStrategy(Fact):
    """
    Selected loading strategy (type or color) with starting item
    """
    strategy = Field(str)
    start_flower = Field(str)
    start_color = Field(str)


class TypeTotal(Fact):
    """Accumulated total need per flower type"""
    state_id = Field(int)
    flower = Field(str)
    total = Field(int, default=0)


class ColorTotal(Fact):
    """Accumulated total need per color"""
    state_id = Field(int)
    color = Field(str)
    total = Field(int, default=0)


class PavilionTotal(Fact):
    """Accumulated total need per pavilion"""
    state_id = Field(int)
    pavilion = Field(str)
    total = Field(int, default=0)


class AggMark(Fact):
    """Marker: a PavilionNeed has been aggregated"""
    state_id = Field(int)
    dim = Field(str)  # 'type', 'color', 'pavilion'
    pavilion = Field(str)
    flower = Field(str)
    color = Field(str)


class Eliminated(Fact):
    """Marker: item eliminated from max-finding"""
    state_id = Field(int)
    dim = Field(str)
    key = Field(str)


class MaxLoadFact(Fact):
    """Maximum load (highest pavilion total)"""
    state_id = Field(int)
    value = Field(int)


class BestType(Fact):
    """Best by-type strategy"""
    state_id = Field(int)
    flower = Field(str)
    total = Field(int)
    start_color = Field(str)


class BestColor(Fact):
    """Best by-color strategy"""
    state_id = Field(int)
    color = Field(str)
    total = Field(int)
    start_flower = Field(str)