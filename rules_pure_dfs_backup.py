from experta import *

from models import *


def manhattan(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

class RoseEngine(KnowledgeEngine):

    generated_count = 0
    expanded_count = 0

    # ==================================
    # PHASE 3: GENERATE MOVES (DFS)
    # Fixed order: right > down > left > up
    # ==================================

    @Rule(
        NOT(FinalState()),
        State(
            id=MATCH.state_id,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost,
            path=MATCH.path
        ),
        ActiveState(
            state_id=MATCH.state_id
        ),
        NOT(
            MovesGenerated(
                state_id=MATCH.state_id
            )
        ),
        salience=30
    )
    def generate_moves(self, state_id, x, y, cost, path):
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_up',
                new_x=x,
                new_y=y - 1,
                new_cost=cost + 1,
                current_path=path
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_left',
                new_x=x - 1,
                new_y=y,
                new_cost=cost + 1,
                current_path=path
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_down',
                new_x=x,
                new_y=y + 1,
                new_cost=cost + 1,
                current_path=path
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_right',
                new_x=x + 1,
                new_y=y,
                new_cost=cost + 1,
                current_path=path
            )
        )
        self.declare(
            MovesGenerated(
                state_id=state_id
            )
        )

    # ==================================
    # PHASE 4: VALIDATE MOVE (pure DFS — no heuristic)
    # Only checks: bounds + path[-6:] dedup + warehouse exception
    # ==================================

    @Rule(
        Grid(width=MATCH.width, height=MATCH.height),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        CandidateMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost,
            current_path=MATCH.path
        ),
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height),
        TEST(lambda x, y, path, wx, wy: (x, y) not in path[-6:] or (x == wx and y == wy)),
        salience=25
    )
    def validate_move(self, parent, action, x, y, cost, path):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost, current_path=path))

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
            new_cost=MATCH.cost,
            current_path=MATCH.path
        )
    )
    def generate_state(self, counter, valid_move, counter_value, parent, action, x, y, cost, path):
        self.generated_count += 1

        new_state_id = counter_value + 1

        self.modify(counter, value=new_state_id)

        new_path = path + ((x, y),)

        self.declare(
            State(
                id=new_state_id,
                parent=parent,
                action=action,
                robot_x=x,
                robot_y=y,
                cost=cost,
                path=new_path
            )
        )

        self.declare(
            OpenState(
                state_id=new_state_id
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
        TEST(lambda wy, ry: wy == ry),
        salience=75
    )
    def detect_robot_at_warehouse(self, state_id):
        self.declare(
            RobotAtWarehouse(
                state_id=state_id
            )
        )
        print(f'\n[WAREHOUSE] Robot reached warehouse in state {state_id}')

    # ==================================
    # PHASE 5: DETECT ROBOT AT PAVILION
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        State(id=MATCH.s, robot_x=MATCH.rx, robot_y=MATCH.ry),
        Pavilion(name=MATCH.pav, x=MATCH.px, y=MATCH.py),
        TEST(lambda rx, px: rx == px),
        TEST(lambda ry, py: ry == py),
        salience=54
    )
    def detect_robot_at_pavilion(self, s, pav):
        self.declare(RobotAtPavilion(state_id=s, pavilion=pav))
        print(f'[PAVILION] Robot arrived at pavilion {pav} in state {s}')

    # ==================================
    # PHASE 5: PROPAGATE NEEDS & LOADS
    # ==================================

    @Rule(
        State(id=MATCH.new_state, parent=MATCH.parent_state),
        PavilionNeed(
            state_id=MATCH.parent_state,
            pavilion=MATCH.pav,
            flower=MATCH.f,
            color=MATCH.c,
            count=MATCH.cnt
        ),
        NOT(PavilionNeed(state_id=MATCH.new_state, pavilion=MATCH.pav, flower=MATCH.f, color=MATCH.c)),
        salience=80
    )
    def propagate_needs(self, new_state, pav, f, c, cnt):
        self.declare(PavilionNeed(state_id=new_state, pavilion=pav, flower=f, color=c, count=cnt))

    @Rule(
        State(id=MATCH.new_state, parent=MATCH.parent_state),
        RobotLoad(state_id=MATCH.parent_state, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt),
        NOT(RobotLoad(state_id=MATCH.new_state, flower=MATCH.f, color=MATCH.c)),
        TEST(lambda cnt: cnt > 0),
        salience=80
    )
    def propagate_loads(self, new_state, f, c, cnt):
        self.declare(RobotLoad(state_id=new_state, flower=f, color=c, count=cnt))

    # ==================================
    # PHASE 5: SMART LOADING AT WAREHOUSE
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        NOT(RobotLoad(state_id=MATCH.s)),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        salience=60
    )
    def start_loading(self, s, f, c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=c, count=cnt))
        print(f'[LOAD] Started loading strategy: {cnt}x {f} ({c}) in state {s}')

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        RobotLoad(state_id=MATCH.s, flower=MATCH.f),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        NOT(RobotLoad(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c)),
        salience=55
    )
    def continue_loading(self, s, f, new_c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=new_c, count=cnt))
        print(f'[LOAD] Added to load: {cnt}x {f} ({new_c}) in state {s}')

    # ==================================
    # PHASE 5: UNLOAD BOUQUET AT PAVILION
    # ==================================

    @Rule(
        RobotAtPavilion(state_id=MATCH.s, pavilion=MATCH.pav),
        AS.load << RobotLoad(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.l_cnt),
        AS.need << PavilionNeed(state_id=MATCH.s, pavilion=MATCH.pav, flower=MATCH.f, color=MATCH.c, count=MATCH.n_cnt),
        TEST(lambda l_cnt: l_cnt > 0),
        TEST(lambda n_cnt: n_cnt > 0),
        salience=50
    )
    def unload_bouquet(self, load, need, s, pav, f, c, n_cnt, l_cnt):
        amount = min(n_cnt, l_cnt)
        self.modify(load, count=l_cnt - amount)
        self.modify(need, count=n_cnt - amount)

        self.declare(Delivered(state_id=s, pavilion=pav, flower=f, color=c))
        print(f'[UNLOAD] Delivered {amount}x {f} ({c}) to {pav} in state {s}')

    # ==================================
    # PHASE 6: DETECT GOAL
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        NOT(PavilionNeed(state_id=MATCH.s, count=P(lambda x: x > 0))),
        NOT(FinalState()),
        salience=100
    )
    def goal_reached(self, s):
        self.declare(FinalState(state_id=s))
        print(f'\n====================================')
        print(f'=== GOAL REACHED IN STATE {s} ===')
        print(f'====================================')


    # ==================================
    # PHASE 7: START PATH TRACING
    # ==================================

    @Rule(
        FinalState(state_id=MATCH.s),
        salience=99
    )
    def start_path_trace(self, s):
        self.declare(
            TracePath(
                state_id=s
            )
        )
        print('\n>>> TRACING PATH <<<')

    # ==================================
    # PHASE 7: TRACE PATH BACKWARDS
    # ==================================

    @Rule(
        TracePath(state_id=MATCH.current_id),
        NOT(PathTraced(state_id=MATCH.current_id)),
        State(id=MATCH.current_id, parent=MATCH.parent, action=MATCH.action, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost),
        TEST(lambda parent: parent > 0),
        salience=99
    )
    def trace_path_step(self, current_id, parent, action, x, y, cost):
        self.declare(PathTraced(state_id=current_id))
        print(f'PATH[{current_id}]: {action} -> ({x},{y}) cost={cost}')
        self.declare(TracePath(state_id=parent))

    @Rule(
        TracePath(state_id=1),
        State(id=1, robot_x=MATCH.x, robot_y=MATCH.y),
        salience=98
    )
    def trace_root_state(self, x, y):
        print(f'PATH[1]: start -> ({x},{y}) cost=0')
        print('>>> PATH TRACE COMPLETE')

    # ==================================
    # PHASE 3: ACTIVATE NEXT STATE (DFS - LIFO)
    # ==================================

    @Rule(
        AS.active << ActiveState(
            state_id=MATCH.current_state
        ),
        MovesGenerated(
            state_id=MATCH.current_state
        ),
        AS.open_node << OpenState(
            state_id=MATCH.next_state
        ),
        NOT(StateExpanded(state_id=MATCH.next_state)),
        salience=-10
    )
    def activate_next_state(self, active, open_node, current_state, next_state):
        self.expanded_count += 1

        self.retract(active)
        self.retract(open_node)
        self.declare(
            StateExpanded(
                state_id=current_state
            )
        )
        self.declare(
            ActiveState(
                state_id=next_state
            )
        )
        print(f'\n[SEARCH] Expanding state {next_state}...')
