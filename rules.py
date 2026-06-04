from experta import *

from models import *


class RoseEngine(KnowledgeEngine):

    # ==================================
    # PHASE 3: GENERATE MOVES (DFS)
    # Salience determines order: right(40) > down(30) > left(20) > up(10)
    # ==================================

    @Rule(
        NOT(FinalState()),
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        ),
        ActiveState(
            state_id=MATCH.state_id
        ),
        NOT(
            MovesGenerated(
                state_id=MATCH.state_id
            )
        ),
        salience=40
    )
    def generate_moves(self, state_id, x, y, cost):
        # Generate all 4 moves as candidate moves
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_right',
                new_x=x + 1,
                new_y=y,
                new_cost=cost + 1
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_down',
                new_x=x,
                new_y=y + 1,
                new_cost=cost + 1
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_left',
                new_x=x - 1,
                new_y=y,
                new_cost=cost + 1
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_up',
                new_x=x,
                new_y=y - 1,
                new_cost=cost + 1
            )
        )
        self.declare(
            MovesGenerated(
                state_id=state_id
            )
        )

    # ==================================
    # PHASE 4: VALIDATE MOVES (with duplicate pruning)
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
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height),
        NOT(
            StateSignature(
                robot_x=MATCH.x,
                robot_y=MATCH.y
            )
        )
    )
    def validate_move(self, parent, action, x, y, cost):
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
    # PHASE 3: GENERATE NEW STATES
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
    def generate_state(self, counter, valid_move, counter_value, parent, action, x, y, cost):
        new_state_id = counter_value + 1

        self.modify(counter, value=new_state_id)

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

        self.retract(valid_move)

        print(f'\n>>> Generated State {new_state_id}')
        print(f'    Parent: {parent} | Action: {action}')
        print(f'    Position: ({x},{y}) | Cost: {cost}')

    # ==================================
    # PHASE 5: DETECT ROBOT AT WAREHOUSE
    # ==================================

    @Rule(
        Warehouse(
            x=MATCH.wx,
            y=MATCH.wy
        ),
        State(
            id=MATCH.state_id,
            robot_x=MATCH.rx,
            robot_y=MATCH.ry
        ),
        TEST(lambda wx, rx: wx == rx),
        TEST(lambda wy, ry: wy == ry)
    )
    def detect_robot_at_warehouse(self, state_id):
        self.declare(
            RobotAtWarehouse(
                state_id=state_id
            )
        )
        print(f'\n[WAREHOUSE] Robot reached warehouse in state {state_id}')

    # ==================================
    # PHASE 5: LOAD BOUQUET FROM WAREHOUSE
    # ==================================

    @Rule(
        RobotAtWarehouse(
            state_id=MATCH.state_id
        ),
        AS.bouquet << Bouquet(
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.count
        ),
        NOT(
            RobotLoad(
                state_id=MATCH.state_id,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        salience=50
    )
    def load_bouquet(self, bouquet, state_id, flower, color, count):
        self.declare(
            RobotLoad(
                state_id=state_id,
                flower=flower,
                color=color,
                count=count
            )
        )
        self.retract(bouquet)
        print(f'[LOAD] Loaded {count}x {flower} ({color}) in state {state_id}')

    # ==================================
    # PHASE 5: PROPAGATE ROBOT LOAD (sibling states)
    # If robot has load in one state at location X, all states at location X have that load
    # ==================================

    @Rule(
        State(
            id=MATCH.state_with_load,
            robot_x=MATCH.x,
            robot_y=MATCH.y
        ),
        State(
            id=MATCH.new_state,
            robot_x=MATCH.x,
            robot_y=MATCH.y
        ),
        RobotLoad(
            state_id=MATCH.state_with_load,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.count
        ),
        NOT(
            RobotLoad(
                state_id=MATCH.new_state,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        NOT(
            Delivered(
                state_id=MATCH.state_with_load,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        salience=50
    )
    def sync_loads_at_position(self, state_with_load, new_state, flower, color, count):
        self.declare(
            RobotLoad(
                state_id=new_state,
                flower=flower,
                color=color,
                count=count
            )
        )

    # ==================================
    # PHASE 5: DETECT ROBOT AT PAVILION
    # ==================================

    @Rule(
        Pavilion(
            name=MATCH.name,
            x=MATCH.px,
            y=MATCH.py
        ),
        State(
            id=MATCH.state_id,
            robot_x=MATCH.rx,
            robot_y=MATCH.ry
        ),
        TEST(lambda px, rx: px == rx),
        TEST(lambda py, ry: py == ry)
    )
    def detect_robot_at_pavilion(self, state_id, name):
        self.declare(
            RobotAtPavilion(
                state_id=state_id,
                pavilion=name
            )
        )
        print(f'\n[PAVILION] Robot reached pavilion {name} in state {state_id}')

    # ==================================
    # PHASE 5: UNLOAD BOUQUET AT PAVILION
    # ==================================

    @Rule(
        RobotAtPavilion(
            state_id=MATCH.state_id,
            pavilion=MATCH.pavilion
        ),
        PavilionNeed(
            pavilion=MATCH.pavilion,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.need_count
        ),
        AS.load << RobotLoad(
            state_id=MATCH.state_id,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.load_count
        ),
        AS.need << PavilionNeed(
            pavilion=MATCH.pavilion,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.need_count
        ),
        NOT(
            Delivered(
                state_id=MATCH.state_id,
                pavilion=MATCH.pavilion,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        salience=50
    )
    def unload_bouquet(self, load, need, state_id, pavilion, flower, color, need_count, load_count):
        self.retract(load)
        self.modify(need, count=need_count - 1)
        self.declare(
            Delivered(
                state_id=state_id,
                pavilion=pavilion,
                flower=flower,
                color=color
            )
        )
        print(f'[UNLOAD] Delivered {flower} ({color}) to pavilion {pavilion}')

    # ==================================
    # PHASE 5: REMOVE EMPTY LOADS
    # ==================================

    @Rule(
        AS.load << RobotLoad(
            state_id=MATCH.state_id,
            flower=MATCH.flower,
            color=MATCH.color,
            count=0
        ),
        salience=45
    )
    def remove_empty_load(self, load):
        self.retract(load)

    # ==================================
    # PHASE 5: REMOVE COMPLETED NEEDS
    # ==================================

    @Rule(
        AS.need << PavilionNeed(
            pavilion=MATCH.pavilion,
            flower=MATCH.flower,
            color=MATCH.color,
            count=0
        ),
        salience=45
    )
    def remove_completed_need(self, need, pavilion):
        self.retract(need)
        print(f'[COMPLETED] Pavilion {pavilion} need satisfied')

    # ==================================
    # PHASE 6: DETECT ALL NEEDS COMPLETED
    # ==================================

    @Rule(
        NOT(
            PavilionNeed()
        ),
        salience=100
    )
    def all_needs_completed(self):
        self.declare(
            AllNeedsCompleted()
        )
        print('\n=== ALL PAVILION NEEDS COMPLETED ===')

    # ==================================
    # PHASE 6: MARK FINAL STATE
    # ==================================

    @Rule(
        AllNeedsCompleted(),
        NOT(
            RobotLoad()
        ),
        salience=100
    )
    def mark_final_state(self):
        self.declare(
            FinalState(
                state_id=-1
            )
        )
        print('=== GOAL REACHED ===')

    # ==================================
    # PHASE 7: START PATH TRACING
    # ==================================

    @Rule(
        FinalState(),
        salience=99
    )
    def start_path_trace(self):
        self.declare(
            TracePath(
                state_id=-1
            )
        )
        print('\n>>> TRACING PATH <<<')

    # ==================================
    # PHASE 7: TRACE PATH BACKWARDS
    # ==================================

    @Rule(
        TracePath(
            state_id=MATCH.current_id
        ),
        State(
            id=MATCH.current_id,
            parent=MATCH.parent,
            action=MATCH.action,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        ),
        TEST(lambda cid: cid > 0)
    )
    def trace_path_step(self, current_id, parent, action, x, y, cost):
        print(f'PATH[{current_id}]: {action} -> ({x},{y}) cost={cost}')
        self.declare(
            TracePath(
                state_id=parent
            )
        )

    # ==================================
    # PHASE 7: TRACE ROOT STATE
    # ==================================

    @Rule(
        TracePath(
            state_id=MATCH.state_id
        ),
        State(
            id=1,
            robot_x=MATCH.x,
            robot_y=MATCH.y
        ),
        TEST(lambda sid: sid == 1)
    )
    def trace_root_state(self, state_id, x, y):
        print(f'PATH[1]: start -> ({x},{y}) cost=0')
        print('>>> PATH TRACE COMPLETE')

    # ==================================
    # PHASE 3: ACTIVATE NEXT STATE (DFS)
    # Lower salience fires after generation/loading/unloading
    # ==================================

    @Rule(
        AS.active << ActiveState(
            state_id=MATCH.current_state
        ),
        State(
            id=MATCH.next_state,
            parent=MATCH.current_state
        ),
        MovesGenerated(
            state_id=MATCH.current_state
        ),
        salience=-10
    )
    def activate_next_state(self, active, current_state, next_state):
        self.retract(active)
        self.declare(
            ActiveState(
                state_id=next_state
            )
        )
        print(f'\n[SEARCH] Expanding state {next_state}...')