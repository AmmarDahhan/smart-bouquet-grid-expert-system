from models import *


def load_initial_facts(engine):
    # Grid configuration
    engine.declare(
        Grid(
            width=6,
            height=6
        )
    )

    # Warehouse location
    engine.declare(
        Warehouse(
            x=2,
            y=3
        )
    )

    # Initial State - Robot at (3,1) with no cost
    engine.declare(
        State(
            id=1,
            parent=0,
            action='start',
            robot_x=3,
            robot_y=1,
            cost=0,
            path=((3, 1),)
        )
    )

    # Initialize state counter for generating unique state IDs
    engine.declare(
        StateCounter(value=1)
    )

    # Mark initial state position as visited
    engine.declare(
        StateSignature(
            robot_x=3,
            robot_y=1
        )
    )

    # Activate the initial state for search
    engine.declare(
        ActiveState(
            state_id=1
        )
    )

    # Pavilion 1: Rose pavilion at (4,2)
    engine.declare(
        Pavilion(
            name='p1',
            flower='rose',
            x=4,
            y=2
        )
    )

    # Pavilion 2: Tulip pavilion at (3,4)
    engine.declare(
        Pavilion(
            name='p2',
            flower='tulip',
            x=3,
            y=4
        )
    )

    # Pavilion 3: Orchid pavilion at (5,4)
    engine.declare(
        Pavilion(
            name='p3',
            flower='orchid',
            x=5,
            y=4
        )
    )

    # Pavilion 4: Juliet Rose pavilion at (2,5)
    engine.declare(
        Pavilion(
            name='p4',
            flower='juliet_rose',
            x=2,
            y=5
        )
    )

    # Pavilion needs - P1 (rose pavilion)
    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p1',
            flower='rose',
            color='red',
            count=2
        )
    )

    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p1',
            flower='rose',
            color='pink',
            count=1
        )
    )

    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p1',
            flower='rose',
            color='white',
            count=1
        )
    )

    # Pavilion needs - P2 (tulip pavilion)
    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p2',
            flower='tulip',
            color='yellow',
            count=1
        )
    )

    # Pavilion needs - P3 (orchid pavilion)
    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p3',
            flower='orchid',
            color='purple',
            count=1
        )
    )

    # Pavilion needs - P4 (juliet rose pavilion)
    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p4',
            flower='juliet_rose',
            color='red',
            count=1
        )
    )

    # Available bouquets at warehouse
    engine.declare(
        Bouquet(
            flower='rose',
            color='red',
            count=2
        )
    )

    engine.declare(
        Bouquet(
            flower='rose',
            color='pink',
            count=1
        )
    )

    engine.declare(
        Bouquet(
            flower='rose',
            color='white',
            count=1
        )
    )

    engine.declare(
        Bouquet(
            flower='tulip',
            color='yellow',
            count=1
        )
    )

    engine.declare(
        Bouquet(
            flower='orchid',
            color='purple',
            count=1
        )
    )

    engine.declare(
        Bouquet(
            flower='juliet_rose',
            color='red',
            count=1
        )
    )