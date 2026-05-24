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