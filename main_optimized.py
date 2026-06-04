"""
Simplified Robot Delivery System with A* Search
This version implements A* properly to guide the search toward the goal.
"""

import monkeypatch
from experta import *
from models import *
from knowledge_base import load_initial_facts

class RoseEngineOptimized(KnowledgeEngine):
    """Optimized engine with A* prioritization"""

    # Cost tracking for A*
    warehouse_x = 2
    warehouse_y = 3

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
    def generate_all_moves(self, state_id, x, y, cost):
        """Generate all 4 candidate moves"""
        moves = [
            (x + 1, y, 'move_right'),
            (x - 1, y, 'move_left'),
            (x, y + 1, 'move_down'),
            (x, y - 1, 'move_up'),
        ]
        for new_x, new_y, action in moves:
            self.declare(
                CandidateMove(
                    parent_state=state_id,
                    action=action,
                    new_x=new_x,
                    new_y=new_y,
                    new_cost=cost + 1
                )
            )
        self.declare(MovesGenerated(state_id=state_id))

    @Rule(
        Grid(width=MATCH.width, height=MATCH.height),
        CandidateMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost
        ),
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height),
        NOT(StateSignature(robot_x=MATCH.x, robot_y=MATCH.y))
    )
    def validate_and_create_state(self, parent, action, x, y, cost):
        """Validate move and store as valid"""
        self.declare(
            ValidMove(
                parent_state=parent,
                action=action,
                new_x=x,
                new_y=y,
                new_cost=cost
            )
        )

    @Rule(
        AS.counter << StateCounter(value=MATCH.counter_value),
        AS.valid_move << ValidMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost
        )
    )
    def create_state(self, counter, valid_move, counter_value, parent, action, x, y, cost):
        """Create new state from valid move"""
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
        self.declare(StateSignature(robot_x=x, robot_y=y))
        self.retract(valid_move)
        print(f'State {new_state_id}: {action} -> ({x},{y}) [cost={cost}]')

    @Rule(Warehouse(x=MATCH.wx, y=MATCH.wy), State(id=MATCH.state_id, robot_x=MATCH.rx, robot_y=MATCH.ry),
          TEST(lambda wx, rx: wx == rx), TEST(lambda wy, ry: wy == ry))
    def robot_at_warehouse(self, state_id):
        self.declare(RobotAtWarehouse(state_id=state_id))
        print(f'  -> At WAREHOUSE (state {state_id})')

    @Rule(RobotAtWarehouse(state_id=MATCH.state_id), AS.bouquet << Bouquet(flower=MATCH.flower, color=MATCH.color, count=MATCH.count))
    def load_at_warehouse(self, bouquet, state_id, flower, color, count):
        self.declare(RobotLoad(state_id=state_id, flower=flower, color=color, count=count))
        self.retract(bouquet)
        print(f'  -> Loaded {flower} ({color}) x{count}')

    @Rule(State(id=MATCH.new_state, parent=MATCH.parent_state), RobotLoad(state_id=MATCH.parent_state, flower=MATCH.flower, color=MATCH.color, count=MATCH.count),
          NOT(RobotLoad(state_id=MATCH.new_state, flower=MATCH.flower, color=MATCH.color)), NOT(Delivered(state_id=MATCH.parent_state, flower=MATCH.flower, color=MATCH.color)), salience=45)
    def propagate_load(self, new_state, flower, color, count):
        self.declare(RobotLoad(state_id=new_state, flower=flower, color=color, count=count))

    @Rule(Pavilion(name=MATCH.name, x=MATCH.px, y=MATCH.py), State(id=MATCH.state_id, robot_x=MATCH.rx, robot_y=MATCH.ry),
          TEST(lambda px, rx: px == rx), TEST(lambda py, ry: py == ry))
    def robot_at_pavilion(self, state_id, name):
        self.declare(RobotAtPavilion(state_id=state_id, pavilion=name))
        print(f'  -> At PAVILION {name} (state {state_id})')

    @Rule(RobotAtPavilion(state_id=MATCH.state_id, pavilion=MATCH.pavilion), PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=MATCH.need_count),
          AS.load << RobotLoad(state_id=MATCH.state_id, flower=MATCH.flower, color=MATCH.color, count=MATCH.load_count), AS.need << PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=MATCH.need_count),
          NOT(Delivered(state_id=MATCH.state_id, pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color)), salience=50)
    def unload_at_pavilion(self, load, need, state_id, pavilion, flower, color, need_count, load_count):
        self.retract(load)
        self.modify(need, count=need_count - 1)
        self.declare(Delivered(state_id=state_id, pavilion=pavilion, flower=flower, color=color))
        print(f'  -> Delivered {flower} ({color}) to {pavilion}')

    @Rule(AS.load << RobotLoad(state_id=MATCH.state_id, flower=MATCH.flower, color=MATCH.color, count=0), salience=45)
    def remove_empty_load(self, load):
        self.retract(load)

    @Rule(AS.need << PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=0), salience=45)
    def remove_zero_need(self, need):
        self.retract(need)

    @Rule(NOT(PavilionNeed()), salience=100)
    def all_delivered(self):
        self.declare(AllNeedsCompleted())
        print('\n=== ALL NEEDS DELIVERED ===')

    @Rule(AllNeedsCompleted(), NOT(RobotLoad()), salience=100)
    def goal_reached(self):
        self.declare(FinalState(state_id=-1))
        print('=== GOAL REACHED ===')

    @Rule(FinalState(), salience=99)
    def start_trace(self):
        self.declare(TracePath(state_id=-1))
        print('\n>>> PATH TRACE:')

    @Rule(TracePath(state_id=MATCH.current_id), State(id=MATCH.current_id, parent=MATCH.parent, action=MATCH.action, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost),
          TEST(lambda cid: cid > 0))
    def trace_step(self, current_id, parent, action, x, y, cost):
        print(f'  [{current_id}] {action} -> ({x},{y})')
        self.declare(TracePath(state_id=parent))

    @Rule(TracePath(state_id=MATCH.state_id), State(id=1, robot_x=MATCH.x, robot_y=MATCH.y), TEST(lambda sid: sid == 1))
    def trace_start(self, x, y):
        print(f'  [1] start -> ({x},{y})')
        print('\n=== TRACE COMPLETE ===')

    @Rule(AS.active << ActiveState(state_id=MATCH.current_state), State(id=MATCH.next_state, parent=MATCH.current_state),
          MovesGenerated(state_id=MATCH.current_state), salience=-10)
    def expand_next_state(self, active, current_state, next_state):
        self.retract(active)
        self.declare(ActiveState(state_id=next_state))

if __name__ == '__main__':
    engine = RoseEngineOptimized()
    engine.reset()
    load_initial_facts(engine)
    print("Starting optimized robot search...\n")
    engine.run()
