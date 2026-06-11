import monkeypatch
from experta import *
from models import *
from knowledge_base import load_initial_facts
from heuristic import heuristic_a_star

class DebugEngine(KnowledgeEngine):
    def _compute_heuristic(self, sid):
        robot_x = robot_y = None
        load_facts = []; need_facts = []
        for f in self.facts.values():
            if isinstance(f, State) and f['id'] == sid:
                robot_x, robot_y = f['robot_x'], f['robot_y']
            elif isinstance(f, RobotLoad) and f['state_id'] == sid and f['count'] > 0:
                load_facts.append((f['flower'], f['color'], f['count']))
            elif isinstance(f, PavilionNeed) and f['state_id'] == sid and f['count'] > 0:
                need_facts.append((f['pavilion'], f['flower'], f['color'], f['count']))
        return heuristic_a_star(robot_x, robot_y, load_facts, need_facts)

    def _compute_load_hash(self, sid):
        load_items = tuple(
            sorted(
                (f['flower'], f['color'], f['count'])
                for f in self.facts.values()
                if isinstance(f, RobotLoad) and f['state_id'] == sid and f['count'] > 0
            )
        )
        if load_items:
            return hash(load_items)
        need_items = tuple(
            sorted(
                (f['pavilion'], f['flower'], f['color'], f['count'])
                for f in self.facts.values()
                if isinstance(f, PavilionNeed) and f['state_id'] == sid and f['count'] > 0
            )
        )
        return hash(need_items) if need_items else 0

    def _select_best_open_state(self):
        best = min((f for f in self.facts.values() if isinstance(f, OpenState)), key=lambda f: f['f_value'], default=None)
        if best is None: return -1
        return best['state_id']

    @Rule(NOT(FinalState()), State(id=MATCH.state_id, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost, path=MATCH.path), ActiveState(state_id=MATCH.state_id), NOT(MovesGenerated(state_id=MATCH.state_id)), salience=30)
    def generate_moves(self, state_id, x, y, cost, path):
        lh = self._compute_load_hash(state_id)
        self.declare(CandidateMove(parent_state=state_id, action='move_right', new_x=x+1, new_y=y, new_cost=cost+1, current_path=path, load_hash=lh))
        self.declare(CandidateMove(parent_state=state_id, action='move_down', new_x=x, new_y=y+1, new_cost=cost+1, current_path=path, load_hash=lh))
        self.declare(CandidateMove(parent_state=state_id, action='move_left', new_x=x-1, new_y=y, new_cost=cost+1, current_path=path, load_hash=lh))
        self.declare(CandidateMove(parent_state=state_id, action='move_up', new_x=x, new_y=y-1, new_cost=cost+1, current_path=path, load_hash=lh))
        self.declare(MovesGenerated(state_id=state_id))

    @Rule(Grid(width=MATCH.width, height=MATCH.height), CandidateMove(parent_state=MATCH.parent, action=MATCH.action, new_x=MATCH.x, new_y=MATCH.y, new_cost=MATCH.cost, current_path=MATCH.path), Warehouse(x=MATCH.x, y=MATCH.y), TEST(lambda x, width: 1<=x<=width), TEST(lambda y, height: 1<=y<=height))
    def validate_move_wh(self, parent, action, x, y, cost, path):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost, current_path=path))
        print(f'  [VALID WH] State {parent} -> ({x},{y}) by {action}')

    @Rule(Grid(width=MATCH.width, height=MATCH.height), Warehouse(x=MATCH.wx, y=MATCH.wy), CandidateMove(parent_state=MATCH.parent, action=MATCH.action, new_x=MATCH.x, new_y=MATCH.y, new_cost=MATCH.cost, current_path=MATCH.path, load_hash=MATCH.lh), NOT(StateSignature(x=MATCH.x, y=MATCH.y, load_hash=MATCH.lh)), TEST(lambda x, y, wx, wy: not (x==wx and y==wy)), TEST(lambda x, width: 1<=x<=width), TEST(lambda y, height: 1<=y<=height))
    def validate_move_normal(self, parent, action, x, y, cost, path, wx, wy, lh):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost, current_path=path))
        print(f'  [VALID NORM] State {parent} -> ({x},{y}) by {action} (lh={lh})')

    @Rule(AS.counter << StateCounter(value=MATCH.counter_value), AS.valid_move << ValidMove(parent_state=MATCH.parent, action=MATCH.action, new_x=MATCH.x, new_y=MATCH.y, new_cost=MATCH.cost, current_path=MATCH.path))
    def generate_state(self, counter, valid_move, counter_value, parent, action, x, y, cost, path):
        new_id = counter_value + 1
        self.modify(counter, value=new_id)
        self.declare(State(id=new_id, parent=parent, action=action, robot_x=x, robot_y=y, cost=cost, path=path + ((x, y),)))
        self.retract(valid_move)
        print(f'  [GEN] State {new_id} at ({x},{y}) from {parent} ({action})')

    @Rule(State(id=MATCH.new_state, parent=MATCH.parent_state), PavilionNeed(state_id=MATCH.parent_state, pavilion=MATCH.pav, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt), NOT(PavilionNeed(state_id=MATCH.new_state, pavilion=MATCH.pav, flower=MATCH.f, color=MATCH.c)), salience=80)
    def propagate_needs(self, new_state, pav, f, c, cnt):
        self.declare(PavilionNeed(state_id=new_state, pavilion=pav, flower=f, color=c, count=cnt))

    @Rule(State(id=MATCH.new_state, parent=MATCH.parent_state), RobotLoad(state_id=MATCH.parent_state, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt), NOT(RobotLoad(state_id=MATCH.new_state, flower=MATCH.f, color=MATCH.c)), TEST(lambda cnt: cnt > 0), salience=80)
    def propagate_loads(self, new_state, f, c, cnt):
        self.declare(RobotLoad(state_id=new_state, flower=f, color=c, count=cnt))

    @Rule(ActiveState(state_id=MATCH.s), State(id=MATCH.s, robot_x=MATCH.x, robot_y=MATCH.y), MovesGenerated(state_id=MATCH.s), salience=5)
    def mark_visited(self, s, x, y):
        lh = self._compute_load_hash(s)
        self.declare(StateSignature(x=x, y=y, load_hash=lh))
        print(f'  [MARK] State {s} at ({x},{y}) lh={lh}')

    @Rule(State(id=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.g), NOT(OpenState(state_id=MATCH.sid)), NOT(MovesGenerated(state_id=MATCH.sid)), salience=70)
    def compute_fvalue(self, sid, x, y, g):
        h = self._compute_heuristic(sid)
        fv = float(g + h - g * 1e-10)
        self.declare(OpenState(state_id=sid, f_value=fv))

    @Rule(Warehouse(x=MATCH.wx, y=MATCH.wy), State(id=MATCH.state_id, robot_x=MATCH.rx, robot_y=MATCH.ry), TEST(lambda wx, rx: wx==rx), TEST(lambda wy, ry: wy==ry), salience=75)
    def detect_robot_at_warehouse(self, state_id):
        self.declare(RobotAtWarehouse(state_id=state_id))
        print(f'[WH] State {state_id} at warehouse')

    @Rule(ActiveState(state_id=MATCH.s), State(id=MATCH.s, robot_x=MATCH.rx, robot_y=MATCH.ry), Pavilion(name=MATCH.pav, x=MATCH.px, y=MATCH.py), TEST(lambda rx, px: rx==px), TEST(lambda ry, py: ry==py), salience=54)
    def detect_robot_at_pavilion(self, s, pav):
        self.declare(RobotAtPavilion(state_id=s, pavilion=pav))
        print(f'  [PAVILION] Robot at pavilion {pav} in state {s}')

    @Rule(ActiveState(state_id=MATCH.s), RobotAtWarehouse(state_id=MATCH.s), AS.rl << RobotLoad(state_id=MATCH.s, count=0), salience=65)
    def reset_exhausted_load(self, s, rl):
        self.retract(rl)
        print(f'[RESET] State {s} reset exhausted load')

    @Rule(ActiveState(state_id=MATCH.s), RobotAtWarehouse(state_id=MATCH.s), NOT(RobotLoad(state_id=MATCH.s)), PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt), TEST(lambda cnt: cnt>0), salience=60)
    def start_loading(self, s, f, c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=c, count=cnt))
        print(f'[LOAD] State {s}: loaded {cnt}x {f}({c})')

    @Rule(ActiveState(state_id=MATCH.s), RobotAtWarehouse(state_id=MATCH.s), RobotLoad(state_id=MATCH.s, flower=MATCH.f), PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c, count=MATCH.cnt), TEST(lambda cnt: cnt>0), NOT(RobotLoad(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c)), salience=55)
    def continue_loading(self, s, f, new_c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=new_c, count=cnt))
        print(f'[LOAD+] State {s}: added {cnt}x {f}({new_c})')

    @Rule(RobotAtPavilion(state_id=MATCH.s, pavilion=MATCH.pav), AS.load << RobotLoad(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.l_cnt), AS.need << PavilionNeed(state_id=MATCH.s, pavilion=MATCH.pav, flower=MATCH.f, color=MATCH.c, count=MATCH.n_cnt), TEST(lambda l_cnt: l_cnt>0), TEST(lambda n_cnt: n_cnt>0), salience=50)
    def unload_bouquet(self, load, need, s, pav, f, c, n_cnt, l_cnt):
        amount = min(n_cnt, l_cnt)
        self.modify(load, count=l_cnt-amount)
        self.modify(need, count=n_cnt-amount)
        print(f'[UNLOAD] State {s}: {amount}x {f}({c}) to {pav}')

    @Rule(ActiveState(state_id=MATCH.s), NOT(PavilionNeed(state_id=MATCH.s, count=P(lambda x: x>0))), NOT(FinalState()), salience=100)
    def goal_reached(self, s):
        self.declare(FinalState(state_id=s))
        print(f'\n*** GOAL REACHED State {s} ***\n')

    @Rule(FinalState(state_id=MATCH.s), salience=99)
    def start_path_trace(self, s):
        self.declare(TracePath(state_id=s))

    @Rule(TracePath(state_id=MATCH.current_id), NOT(PathTraced(state_id=MATCH.current_id)), State(id=MATCH.current_id, parent=MATCH.parent, action=MATCH.action, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost), TEST(lambda parent: parent > 0), salience=99)
    def trace_path_step(self, current_id, parent, action, x, y, cost):
        self.declare(PathTraced(state_id=current_id))
        print(f'PATH[{current_id}]: {action} -> ({x},{y}) cost={cost}')
        self.declare(TracePath(state_id=parent))

    @Rule(TracePath(state_id=MATCH.state_id), State(id=1, robot_x=MATCH.x, robot_y=MATCH.y), TEST(lambda sid: sid==1), salience=98)
    def trace_root_state(self, state_id, x, y):
        print(f'PATH[1]: start -> ({x},{y}) cost=0')
        print('>>> PATH TRACE COMPLETE')

    @Rule(AS.active << ActiveState(state_id=MATCH.current_state), MovesGenerated(state_id=MATCH.current_state), AS.os << OpenState(state_id=MATCH.current_state), NOT(FinalState()), salience=-5)
    def retract_frontier(self, active, os, current_state):
        self.retract(active)
        self.retract(os)

    @Rule(NOT(ActiveState()), NOT(FinalState()), salience=-6)
    def select_best_frontier(self):
        best_id = self._select_best_open_state()
        self.declare(ActiveState(state_id=best_id))
        print(f'[A*] Expanding state {best_id}...')

engine = DebugEngine()
engine.reset()
load_initial_facts(engine)
engine.run()
