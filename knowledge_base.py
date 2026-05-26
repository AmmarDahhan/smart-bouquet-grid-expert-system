from models import *


def load_initial_facts(engine):

    engine.declare(
        Grid(
            width=6,
            height=6
        )
    )

    engine.declare(
        Warehouse(
            x=2,
            y=3
        )
    )

    # Initial State

    engine.declare(
        State(
            id=1,
            parent=0,
            action='start',
            robot_x=3,
            robot_y=1,
            cost=0
        )
    )

    # Pavilion 1

    engine.declare(
        Pavilion(
            name='p1',
            flower='rose',
            x=4,
            y=2
        )
    )

    engine.declare(
        Need(
            state_id=1,
            pavilion='p1',
            color='red',
            count=2
        )
    )

    engine.declare(
        Need(
            state_id=1,
            pavilion='p1',
            color='pink',
            count=1
        )
    )

    engine.declare(
        Need(
            state_id=1,
            pavilion='p1',
            color='white',
            count=1
        )
    )

    engine.declare(
        VisitedState(
            robot_x=3,
            robot_y=1
        )
    )

    engine.declare(
        StateCounter(value=1)
    )

    engine.declare(
        StateSignature(
            robot_x=3,
            robot_y=1
        )
    )

    # temporary 
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
            color='white',
            count=1
        )
    )

    engine.declare(
        Pavilion(
            name='p1',
            flower='rose',
            x=4,
            y=2
        )
    )

    engine.declare(
        PavilionNeed(
            pavilion='p1',
            flower='rose',
            color='red',
            count=2
        ),

        PavilionNeed(
            pavilion='p1',
            flower='rose',
            color='white',
            count=1
        ),

        PavilionNeed(
            pavilion='p2',
            flower='tulip',
            color='yellow',
            count=1
        ),

        PavilionNeed(
            pavilion='p3',
            flower='orchid',
            color='purple',
            count=1
        ),
    )