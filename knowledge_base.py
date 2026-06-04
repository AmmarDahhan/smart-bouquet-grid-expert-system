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
            cost=0,
            path=((3, 1),)
        )
    )

    engine.declare(
        ActiveState(
            state_id=1
        )
    )

    engine.declare(
        OpenState(
            state_id=1
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
        ),
        Pavilion(
            name='p2',
            flower='tulip',
            x=5,
            y=5
        ),
        Pavilion(
            name='p3',
            flower='orchid',
            x=1,
            y=4
        )
    )

    engine.declare(
        PavilionNeed(
            state_id=1,
            pavilion='p1',
            flower='rose',
            color='red',
            count=2
        ),

        PavilionNeed(
            state_id=1,
            pavilion='p1',
            flower='rose',
            color='white',
            count=1
        ),

        PavilionNeed(
            state_id=1,
            pavilion='p2',
            flower='tulip',
            color='yellow',
            count=1
        ),

        PavilionNeed(
            state_id=1,
            pavilion='p3',
            flower='orchid',
            color='purple',
            count=1
        ),
    )

    engine.declare(
        RobotCapacity(
            value=3
        )
    ) 