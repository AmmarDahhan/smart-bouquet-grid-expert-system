"""
Rose Gallery Robot - Greedy Best-First Search (BBF) variant
Uses heuristic distance to guide expansion order
"""

import monkeypatch
from experta import *
from models import *
from knowledge_base import load_initial_facts
from utils import manhattan_distance

class RoseEngineGreedy(KnowledgeEngine):
    """Uses greedy best-first search guided by proximity heuristics"""
    
    @Rule(
        NOT(FinalState()),
        State(id=MATCH.state_id, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost),
        ActiveState(state_id=MATCH.state_id),
        NOT(MovesGenerated(state_id=MATCH.state_id)),
        salience=40
    )
    def generate_moves(self, state_id, x, y, cost):
        # Moves in order: right, down, left, up (salience controlled)
        self.declare(
            CandidateMove(parent_state=state_id, action='move_right', new_x=x+1, new_y=y, new_cost=cost+1)
        )
        self.declare(
            CandidateMove(parent_state=state_id, action='move_down', new_x=x, new_y=y+1, new_cost=cost+1)
        )
        self.declare(
            CandidateMove(parent_state=state_id, action='move_left', new_x=x-1, new_y=y, new_cost=cost+1)
        )
        self.declare(
            CandidateMove(parent_state=state_id, action='move_up', new_x=x, new_y=y-1, new_cost=cost+1)
        )
        self.declare(MovesGenerated(state_id=state_id))

    @Rule(
        Grid(width=MATCH.width, height=MATCH.height),
        CandidateMove(parent_state=MATCH.parent, action=MATCH.action, new_x=MATCH.x, new_y=MATCH.y, new_cost=MATCH.cost),
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height),
        NOT(StateSignature(robot_x=MATCH.x, robot_y=MATCH.y))
    )
    def validate_move(self, parent, action, x, y, cost):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost))

    @Rule(
        AS.counter << StateCounter(value=MATCH.counter_value),
        AS.valid_move << ValidMove(parent_state=MATCH.parent, action=MATCH.action, new_x=MATCH.x, new_y=MATCH.y, new_cost=MATCH.cost)
    )
    def create_state(self, counter, valid_move, counter_value, parent, action, x, y, cost):
        new_id = counter_value + 1
        self.modify(counter, value=new_id)
        self.declare(State(id=new_id, parent=parent, action=action, robot_x=x, robot_y=y, cost=cost))
        self.declare(StateSignature(robot_x=x, robot_y=y))
        self.retract(valid_move)

    @Rule(Warehouse(x=MATCH.wx, y=MATCH.wy), State(id=MATCH.state_id, robot_x=MATCH.rx, robot_y=MATCH.ry),
          TEST(lambda wx, rx: wx == rx), TEST(lambda wy, ry: wy == ry))
    def at_warehouse(self, state_id):
        self.declare(RobotAtWarehouse(state_id=state_id))

    @Rule(RobotAtWarehouse(state_id=MATCH.state_id), AS.bouquet << Bouquet(flower=MATCH.flower, color=MATCH.color, count=MATCH.count), salience=50)
    def load_bouquet(self, bouquet, state_id, flower, color, count):
        self.declare(RobotLoad(state_id=state_id, flower=flower, color=color, count=count))
        self.retract(bouquet)

    @Rule(State(id=MATCH.new_state, parent=MATCH.parent), RobotLoad(state_id=MATCH.parent, flower=MATCH.flower, color=MATCH.color, count=MATCH.count),
          NOT(RobotLoad(state_id=MATCH.new_state, flower=MATCH.flower, color=MATCH.color)), NOT(Delivered(state_id=MATCH.parent, flower=MATCH.flower, color=MATCH.color)), salience=45)
    def propagate_load(self, new_state, flower, color, count):
        self.declare(RobotLoad(state_id=new_state, flower=flower, color=color, count=count))

    @Rule(Pavilion(name=MATCH.name, x=MATCH.px, y=MATCH.py), State(id=MATCH.state_id, robot_x=MATCH.rx, robot_y=MATCH.ry),
          TEST(lambda px, rx: px == rx), TEST(lambda py, ry: py == ry))
    def at_pavilion(self, state_id, name):
        self.declare(RobotAtPavilion(state_id=state_id, pavilion=name))

    @Rule(RobotAtPavilion(state_id=MATCH.state_id, pavilion=MATCH.pavilion), PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=MATCH.need_count),
          AS.load << RobotLoad(state_id=MATCH.state_id, flower=MATCH.flower, color=MATCH.color, count=MATCH.load_count),
          AS.need << PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=MATCH.need_count),
          NOT(Delivered(state_id=MATCH.state_id, pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color)), salience=50)
    def unload_bouquet(self, load, need, state_id, pavilion, flower, color, need_count, load_count):
        self.retract(load)
        self.modify(need, count=need_count - 1)
        self.declare(Delivered(state_id=state_id, pavilion=pavilion, flower=flower, color=color))

    @Rule(AS.load << RobotLoad(state_id=MATCH.state_id, flower=MATCH.flower, color=MATCH.color, count=0), salience=45)
    def remove_empty_load(self, load):
        self.retract(load)

    @Rule(AS.need << PavilionNeed(pavilion=MATCH.pavilion, flower=MATCH.flower, color=MATCH.color, count=0), salience=45)
    def remove_completed_need(self, need):
        self.retract(need)

    @Rule(NOT(PavilionNeed()), salience=100)
    def check_all_complete(self):
        self.declare(AllNeedsCompleted())

    @Rule(AllNeedsCompleted(), NOT(RobotLoad()), salience=100)
    def goal_detected(self):
        self.declare(FinalState(state_id=-1))
        print('\n*** GOAL REACHED ***')

    @Rule(FinalState(), salience=99)
    def trace_goal(self):
        self.declare(TracePath(state_id=-1))
        print('\nPath trace:')

    @Rule(TracePath(state_id=MATCH.id), State(id=MATCH.id, parent=MATCH.parent, action=MATCH.action, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost), TEST(lambda id: id > 0))
    def trace_path(self, id, parent, action, x, y, cost):
        print(f'  {id}: {action} -> ({x},{y}) cost={cost}')
        self.declare(TracePath(state_id=parent))

    @Rule(TracePath(state_id=MATCH.id), State(id=1, robot_x=MATCH.x, robot_y=MATCH.y), TEST(lambda id: id == 1))
    def trace_root(self, x, y):
        print(f'  1: START -> ({x},{y}) cost=0')

    @Rule(AS.active << ActiveState(state_id=MATCH.current), State(id=MATCH.next, parent=MATCH.current), MovesGenerated(state_id=MATCH.current), salience=-10)
    def next_state(self, active, current, next):
        self.retract(active)
        self.declare(ActiveState(state_id=next))

if __name__ == '__main__':
    engine = RoseEngineGreedy()
    engine.reset()
    load_initial_facts(engine)
    print("Rose Gallery Robot - Greedy Search\n")
    engine.run()
