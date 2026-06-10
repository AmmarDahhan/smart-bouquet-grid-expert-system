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
    Unique generated state signature
    """
    pass

class CandidateMove(Fact):
    """
    Proposed next move
    """
    pass

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
    pass

class Delivered(Fact):
    pass

class ActiveState(Fact):
    pass

class MovesGenerated(Fact):
    state_id = Field(int)

class StateFValue(Fact):
    """F value for A* (g + h)"""
    state_id = Field(int)
    f_value = Field(int)

class OpenState(Fact):
    pass