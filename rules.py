from experta import *

from models import *


class RoseEngine(KnowledgeEngine):

    # ==================================
    # GENERATE RIGHT MOVE
    # ==================================

    @Rule(
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        )
        ,
        salience=40
    )
    def generate_move_right(
        self,
        state_id,
        x,
        y,
        cost
    ):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_right',
                new_x=x + 1,
                new_y=y,
                new_cost=cost + 1
            )
        )

    # ==================================
    # GENERATE LEFT MOVE
    # ==================================

    @Rule(
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        )
        ,
        salience=20
    )
    def generate_move_left(
        self,
        state_id,
        x,
        y,
        cost
    ):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_left',
                new_x=x - 1,
                new_y=y,
                new_cost=cost + 1
            )
        )

    # ==================================
    # GENERATE UP MOVE
    # ==================================

    @Rule(
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        )
        ,
        salience=10
    )
    def generate_move_up(
        self,
        state_id,
        x,
        y,
        cost
    ):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_up',
                new_x=x,
                new_y=y - 1,
                new_cost=cost + 1
            )
        )

    # ==================================
    # GENERATE DOWN MOVE
    # ==================================

    @Rule(
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        )
        ,
        salience=30
    )
    def generate_move_down(
        self,
        state_id,
        x,
        y,
        cost
    ):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_down',
                new_x=x,
                new_y=y + 1,
                new_cost=cost + 1
            )
        )
    
    # ==================================
    # VALIDATE GRID BOUNDARIES + DUPLICATES
    # ==================================

    @Rule(
        Grid(
            width=MATCH.width,
            height=MATCH.height
        ),

        CandidateMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost
        ),

        TEST(lambda x: x >= 1),
        TEST(lambda y: y >= 1),
        TEST(lambda x, width: x <= width),
        TEST(lambda y, height: y <= height),

        NOT(
            StateSignature(
                robot_x=MATCH.x,
                robot_y=MATCH.y
            )
        )
    )
    def validate_move(
        self,
        parent,
        action,
        x,
        y,
        cost
    ):

        self.declare(
            ValidMove(
                parent_state=parent,
                action=action,
                new_x=x,
                new_y=y,
                new_cost=cost
            )
        )

    # ==================================
    # SHOW VALID MOVES
    # ==================================

    @Rule(
        ValidMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y
        )
    )
    def show_valid_move(
        self,
        parent,
        action,
        x,
        y
    ):

        print(
            f'Valid move from state {parent}'
        )

        print(
            f'{action} -> ({x},{y})'
        )


    # ==================================
    # GENERATE NEW STATE
    # ==================================

    @Rule(
        AS.counter << StateCounter(
            value=MATCH.counter_value
        ),

        AS.valid_move << ValidMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost
        )
    )
    def generate_state(
        self,
        counter,
        valid_move,
        counter_value,
        parent,
        action,
        x,
        y,
        cost
    ):

        new_state_id = counter_value + 1

        self.modify(
            counter,
            value=new_state_id
        )

        self.declare(
            State(
                id=new_state_id,
                parent=parent,
                action=action,
                robot_x=x,
                robot_y=y,
                cost=cost
            )
        )

        self.declare(
            StateSignature(
                robot_x=x,
                robot_y=y
            )
        )

        self.retract(
            valid_move
        )

        print(
            f'\nGenerated State {new_state_id}'
        )

        print(
            f'Parent: {parent}'
        )

        print(
            f'Action: {action}'
        )

        print(
            f'Position: ({x},{y})'
        )

        print(
            f'Cost: {cost}'
        )