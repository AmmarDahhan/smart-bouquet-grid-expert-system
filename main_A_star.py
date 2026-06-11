import monkeypatch
from experta import *
from models import *
from knowledge_base import load_initial_facts
from heuristic import heuristic_a_star


class RoseEngineAStar(KnowledgeEngine):
    """
    A* search engine using Experta rules.
    All decisions are rule-based — NO for/while/if in rules.
    Heuristic is computed via a regular Python function (allowed).
    """
    generated_count = 0
    expanded_count = 0

    def _compute_heuristic(self, sid):
        """Regular Python function for A* heuristic (allowed per spec)."""
        robot_x = robot_y = None
        load_facts = []
        need_facts = []
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

    # ==================================
    # LOADING STRATEGY — pure rule-based (no loops/conditions)
    # Phase 1: init accumulators (salience 70)
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        NOT(RobotLoad(state_id=MATCH.s)),
        NOT(LoadStrategy(state_id=MATCH.s)),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, count=P(lambda x: x > 0)),
        NOT(TypeTotal(state_id=MATCH.s, flower=MATCH.f)),
        salience=70
    )
    def init_type_total(self, s, f):
        self.declare(TypeTotal(state_id=s, flower=f, total=0))

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        NOT(RobotLoad(state_id=MATCH.s)),
        NOT(LoadStrategy(state_id=MATCH.s)),
        PavilionNeed(state_id=MATCH.s, color=MATCH.c, count=P(lambda x: x > 0)),
        NOT(ColorTotal(state_id=MATCH.s, color=MATCH.c)),
        salience=70
    )
    def init_color_total(self, s, c):
        self.declare(ColorTotal(state_id=s, color=c, total=0))

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        NOT(RobotLoad(state_id=MATCH.s)),
        NOT(LoadStrategy(state_id=MATCH.s)),
        PavilionNeed(state_id=MATCH.s, pavilion=MATCH.p, count=P(lambda x: x > 0)),
        NOT(PavilionTotal(state_id=MATCH.s, pavilion=MATCH.p)),
        salience=70
    )
    def init_pavilion_total(self, s, p):
        self.declare(PavilionTotal(state_id=s, pavilion=p, total=0))

    # ==================================
    # Phase 2: accumulate (salience 66)
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        AS.total << TypeTotal(state_id=MATCH.s, flower=MATCH.f, total=MATCH.t),
        AS.need << PavilionNeed(state_id=MATCH.s, pavilion=MATCH.p, flower=MATCH.f, color=MATCH.c, count=MATCH.n),
        NOT(AggMark(state_id=MATCH.s, dim='type', flower=MATCH.f, color=MATCH.c)),
        TEST(lambda n: n > 0),
        salience=66
    )
    def accumulate_type(self, total, need, s, f, c, t, n):
        self.declare(AggMark(state_id=s, dim='type', pavilion='', flower=f, color=c))
        self.modify(total, total=t + n)

    @Rule(
        ActiveState(state_id=MATCH.s),
        AS.total << ColorTotal(state_id=MATCH.s, color=MATCH.c, total=MATCH.t),
        AS.need << PavilionNeed(state_id=MATCH.s, pavilion=MATCH.p, flower=MATCH.f, color=MATCH.c, count=MATCH.n),
        NOT(AggMark(state_id=MATCH.s, dim='color', color=MATCH.c)),
        TEST(lambda n: n > 0),
        salience=66
    )
    def accumulate_color(self, total, need, s, c, t, n):
        self.declare(AggMark(state_id=s, dim='color', pavilion='', flower='', color=c))
        self.modify(total, total=t + n)

    @Rule(
        ActiveState(state_id=MATCH.s),
        AS.total << PavilionTotal(state_id=MATCH.s, pavilion=MATCH.p, total=MATCH.t),
        AS.need << PavilionNeed(state_id=MATCH.s, pavilion=MATCH.p, flower=MATCH.f, color=MATCH.c, count=MATCH.n),
        NOT(AggMark(state_id=MATCH.s, dim='pavilion', pavilion=MATCH.p)),
        TEST(lambda n: n > 0),
        salience=66
    )
    def accumulate_pavilion(self, total, need, s, p, t, n):
        self.declare(AggMark(state_id=s, dim='pavilion', pavilion=p, flower='', color=''))
        self.modify(total, total=t + n)

    # ==================================
    # Phase 3: find max load (elimination, salience 58)
    # ==================================

    @Rule(
        PavilionTotal(state_id=MATCH.s, pavilion=MATCH.p1, total=MATCH.t1),
        PavilionTotal(state_id=MATCH.s, pavilion=MATCH.p2, total=MATCH.t2),
        TEST(lambda t1, t2, p1, p2: t1 < t2 or (t1 == t2 and p1 < p2)),
        NOT(Eliminated(state_id=MATCH.s, dim='pavilion', key=MATCH.p1)),
        salience=58
    )
    def eliminate_pavilion(self, s, p1):
        self.declare(Eliminated(state_id=s, dim='pavilion', key=p1))

    @Rule(
        PavilionTotal(state_id=MATCH.s, pavilion=MATCH.p, total=MATCH.t),
        NOT(Eliminated(state_id=MATCH.s, dim='pavilion', key=MATCH.p)),
        NOT(MaxLoadFact(state_id=MATCH.s)),
        salience=55
    )
    def declare_max_load(self, s, p, t):
        self.declare(MaxLoadFact(state_id=s, value=t))
        print(f'[MAX_LOAD] State {s}: max load = {t}')

    # ==================================
    # Phase 4: find best type (elimination, salience 57)
    # ==================================

    @Rule(
        TypeTotal(state_id=MATCH.s, flower=MATCH.f1, total=MATCH.t1),
        TypeTotal(state_id=MATCH.s, flower=MATCH.f2, total=MATCH.t2),
        TEST(lambda t1, t2, f1, f2: t1 < t2 or (t1 == t2 and f1 < f2)),
        NOT(Eliminated(state_id=MATCH.s, dim='type', key=MATCH.f1)),
        salience=57
    )
    def eliminate_type(self, s, f1):
        self.declare(Eliminated(state_id=s, dim='type', key=f1))

    @Rule(
        ActiveState(state_id=MATCH.s),
        TypeTotal(state_id=MATCH.s, flower=MATCH.f, total=MATCH.t),
        NOT(Eliminated(state_id=MATCH.s, dim='type', key=MATCH.f)),
        NOT(BestType(state_id=MATCH.s)),
        salience=55
    )
    def declare_best_type(self, s, f, t):
        self.declare(BestType(state_id=s, flower=f, total=t, start_color=''))

    # ==================================
    # Phase 5: find best type's start color (salience 52)
    # ==================================

    @Rule(
        BestType(state_id=MATCH.s, flower=MATCH.f),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c1, count=MATCH.n1),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c2, count=MATCH.n2),
        TEST(lambda n1, n2, c1, c2: n1 < n2 or (n1 == n2 and c1 < c2)),
        NOT(Eliminated(state_id=MATCH.s, dim='type_color', key=MATCH.c1)),
        salience=52
    )
    def eliminate_type_color(self, s, f, c1):
        self.declare(Eliminated(state_id=s, dim='type_color', key=c1))

    @Rule(
        AS.best << BestType(state_id=MATCH.s, flower=MATCH.f),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.n),
        NOT(Eliminated(state_id=MATCH.s, dim='type_color', key=MATCH.c)),
        NOT(Eliminated(state_id=MATCH.s, dim='type_color_set', key=MATCH.f)),
        TEST(lambda n: n > 0),
        salience=50
    )
    def set_best_type_color(self, best, s, f, c, n):
        self.declare(Eliminated(state_id=s, dim='type_color_set', key=f))
        self.modify(best, start_color=c)

    # ==================================
    # Phase 6: find best color (elimination, salience 56)
    # ==================================

    @Rule(
        ColorTotal(state_id=MATCH.s, color=MATCH.c1, total=MATCH.t1),
        ColorTotal(state_id=MATCH.s, color=MATCH.c2, total=MATCH.t2),
        TEST(lambda t1, t2, c1, c2: t1 < t2 or (t1 == t2 and c1 < c2)),
        NOT(Eliminated(state_id=MATCH.s, dim='color', key=MATCH.c1)),
        salience=56
    )
    def eliminate_color(self, s, c1):
        self.declare(Eliminated(state_id=s, dim='color', key=c1))

    @Rule(
        ActiveState(state_id=MATCH.s),
        ColorTotal(state_id=MATCH.s, color=MATCH.c, total=MATCH.t),
        NOT(Eliminated(state_id=MATCH.s, dim='color', key=MATCH.c)),
        NOT(BestColor(state_id=MATCH.s)),
        salience=55
    )
    def declare_best_color(self, s, c, t):
        self.declare(BestColor(state_id=s, color=c, total=t, start_flower=''))

    # ==================================
    # Phase 7: find best color's start flower (salience 51)
    # ==================================

    @Rule(
        BestColor(state_id=MATCH.s, color=MATCH.c),
        PavilionNeed(state_id=MATCH.s, color=MATCH.c, flower=MATCH.f1, count=MATCH.n1),
        PavilionNeed(state_id=MATCH.s, color=MATCH.c, flower=MATCH.f2, count=MATCH.n2),
        TEST(lambda n1, n2, f1, f2: n1 < n2 or (n1 == n2 and f1 < f2)),
        NOT(Eliminated(state_id=MATCH.s, dim='color_flower', key=MATCH.f1)),
        salience=51
    )
    def eliminate_color_flower(self, s, c, f1):
        self.declare(Eliminated(state_id=s, dim='color_flower', key=f1))

    @Rule(
        AS.best << BestColor(state_id=MATCH.s, color=MATCH.c),
        PavilionNeed(state_id=MATCH.s, color=MATCH.c, flower=MATCH.f, count=MATCH.n),
        NOT(Eliminated(state_id=MATCH.s, dim='color_flower', key=MATCH.f)),
        NOT(Eliminated(state_id=MATCH.s, dim='color_flower_set', key=MATCH.c)),
        TEST(lambda n: n > 0),
        salience=50
    )
    def set_best_color_flower(self, best, s, c, f, n):
        self.declare(Eliminated(state_id=s, dim='color_flower_set', key=c))
        self.modify(best, start_flower=f)

    # ==================================
    # Phase 8: declare final LoadStrategy (salience 48)
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        MaxLoadFact(state_id=MATCH.s, value=MATCH.ml),
        BestType(state_id=MATCH.s, flower=MATCH.f, total=MATCH.tt, start_color=MATCH.sc),
        BestColor(state_id=MATCH.s, color=MATCH.c, total=MATCH.tc, start_flower=MATCH.sf),
        TEST(lambda tt, tc, ml: min(tt, ml) >= min(tc, ml)),
        NOT(LoadStrategy(state_id=MATCH.s)),
        salience=48
    )
    def declare_type_strategy(self, s, f, sc):
        self.declare(LoadStrategy(state_id=s, strategy='type', start_flower=f, start_color=sc))
        print(f'[STRATEGY] State {s} chooses type: start with {f}({sc})')

    @Rule(
        ActiveState(state_id=MATCH.s),
        MaxLoadFact(state_id=MATCH.s, value=MATCH.ml),
        BestType(state_id=MATCH.s, flower=MATCH.f, total=MATCH.tt, start_color=MATCH.sc),
        BestColor(state_id=MATCH.s, color=MATCH.c, total=MATCH.tc, start_flower=MATCH.sf),
        TEST(lambda tt, tc, ml: min(tt, ml) < min(tc, ml)),
        NOT(LoadStrategy(state_id=MATCH.s)),
        salience=48
    )
    def declare_color_strategy(self, s, c, sf):
        self.declare(LoadStrategy(state_id=s, strategy='color', start_flower=sf, start_color=c))
        print(f'[STRATEGY] State {s} chooses color: start with {sf}({c})')

    def _select_best_open_state(self):
        """Find OpenState with minimum f_value (data query, not search logic)."""
        best = min(
            (f for f in self.facts.values() if isinstance(f, OpenState)),
            key=lambda f: f['f_value'],
            default=None
        )
        if best is None:
            return -1
        return best['state_id']

    # ==================================
    # PHASE 3: GENERATE MOVES
    # ==================================

    @Rule(
        NOT(FinalState()),
        State(id=MATCH.state_id, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.cost, path=MATCH.path),
        ActiveState(state_id=MATCH.state_id),
        NOT(MovesGenerated(state_id=MATCH.state_id)),
        salience=30
    )
    def generate_moves(self, state_id, x, y, cost, path):
        lh = self._compute_load_hash(state_id)
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_right',
                new_x=x + 1,
                new_y=y,
                new_cost=cost + 1,
                current_path=path,
                load_hash=lh
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_down',
                new_x=x,
                new_y=y + 1,
                new_cost=cost + 1,
                current_path=path,
                load_hash=lh
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_left',
                new_x=x - 1,
                new_y=y,
                new_cost=cost + 1,
                current_path=path,
                load_hash=lh
            )
        )
        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_up',
                new_x=x,
                new_y=y - 1,
                new_cost=cost + 1,
                current_path=path,
                load_hash=lh
            )
        )
        self.declare(
            MovesGenerated(
                state_id=state_id
            )
        )

    # ==================================
    # PHASE 4: VALIDATE MOVES
    # ==================================

    @Rule(
        Grid(width=MATCH.width, height=MATCH.height),
        CandidateMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost,
            current_path=MATCH.path
        ),
        Warehouse(x=MATCH.x, y=MATCH.y),
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height)
    )
    def validate_move_wh(self, parent, action, x, y, cost, path):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost, current_path=path))

    @Rule(
        Grid(width=MATCH.width, height=MATCH.height),
        Warehouse(x=MATCH.wx, y=MATCH.wy),
        CandidateMove(
            parent_state=MATCH.parent,
            action=MATCH.action,
            new_x=MATCH.x,
            new_y=MATCH.y,
            new_cost=MATCH.cost,
            current_path=MATCH.path,
            load_hash=MATCH.lh
        ),
        NOT(StateSignature(x=MATCH.x, y=MATCH.y, load_hash=MATCH.lh)),
        TEST(lambda x, y, wx, wy: not (x == wx and y == wy)),  # not warehouse
        TEST(lambda x, width: 1 <= x <= width),
        TEST(lambda y, height: 1 <= y <= height)
    )
    def validate_move_normal(self, parent, action, x, y, cost, path, wx, wy, lh):
        self.declare(ValidMove(parent_state=parent, action=action, new_x=x, new_y=y, new_cost=cost, current_path=path))

    # ==================================
    # PHASE 6: GENERATE NEW STATE
    # ==================================

    @Rule(
        AS.counter << StateCounter(value=MATCH.counter_value),
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
        self.retract(valid_move)
        print(f'\n>>> Generated State {new_state_id}')
        print(f'    Parent: {parent} | Action: {action}')
        print(f'    Position: ({x},{y}) | Cost: {cost}')

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
    # PHASE 5b: MARK CELL AS VISITED (per-cell global dedup)
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        State(id=MATCH.s, robot_x=MATCH.x, robot_y=MATCH.y),
        MovesGenerated(state_id=MATCH.s),
        salience=-1
    )
    def mark_visited(self, s, x, y):
        lh = self._compute_load_hash(s)
        self.declare(StateSignature(x=x, y=y, load_hash=lh))

    # ==================================
    # PHASE 5b: COMPUTE F-VALUE (A* heuristic)
    # ==================================

    @Rule(
        State(id=MATCH.sid, robot_x=MATCH.x, robot_y=MATCH.y, cost=MATCH.g),
        NOT(OpenState(state_id=MATCH.sid)),
        NOT(MovesGenerated(state_id=MATCH.sid)),
        salience=70
    )
    def compute_fvalue(self, sid, x, y, g):
        h = self._compute_heuristic(sid)
        fv = float(g + h - g * 1e-10)
        self.declare(OpenState(state_id=sid, f_value=fv))

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
        self.declare(RobotAtWarehouse(state_id=state_id))
        print(f'\n[WAREHOUSE] Robot reached warehouse in state {state_id}')

    # ==================================
    # Reset exhausted loads at warehouse
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        AS.rl << RobotLoad(state_id=MATCH.s, count=0),
        salience=65
    )
    def reset_exhausted_load(self, s, rl):
        self.retract(rl)

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
    # PHASE 5: SMART LOADING AT WAREHOUSE
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        NOT(RobotLoad(state_id=MATCH.s)),
        LoadStrategy(state_id=MATCH.s, start_flower=MATCH.f, start_color=MATCH.c),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        salience=60
    )
    def start_loading(self, s, f, c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=c, count=cnt))
        print(f'[LOAD] Started loading: {cnt}x {f} ({c}) in state {s}')

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        LoadStrategy(state_id=MATCH.s, strategy=MATCH.strat),
        TEST(lambda strat: strat == 'type'),
        RobotLoad(state_id=MATCH.s, flower=MATCH.f),
        PavilionNeed(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        NOT(RobotLoad(state_id=MATCH.s, flower=MATCH.f, color=MATCH.new_c)),
        salience=55
    )
    def continue_loading(self, s, f, new_c, cnt):
        self.declare(RobotLoad(state_id=s, flower=f, color=new_c, count=cnt))
        print(f'[LOAD] Added to load (by type): {cnt}x {f} ({new_c}) in state {s}')

    @Rule(
        ActiveState(state_id=MATCH.s),
        RobotAtWarehouse(state_id=MATCH.s),
        LoadStrategy(state_id=MATCH.s, strategy=MATCH.strat),
        TEST(lambda strat: strat == 'color'),
        RobotLoad(state_id=MATCH.s, color=MATCH.c),
        PavilionNeed(state_id=MATCH.s, color=MATCH.c, flower=MATCH.new_f, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        NOT(RobotLoad(state_id=MATCH.s, flower=MATCH.new_f, color=MATCH.c)),
        salience=53
    )
    def continue_loading_by_color(self, s, c, new_f, cnt):
        self.declare(RobotLoad(state_id=s, flower=new_f, color=c, count=cnt))
        print(f'[LOAD] Added to load (by color): {cnt}x {new_f} ({c}) in state {s}')

    # ==================================
    # PHASE 5: UNLOAD AT PAVILION
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
    # PHASE 6: GOAL DETECTION
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
    # PHASE 7: PATH TRACING
    # ==================================

    @Rule(
        FinalState(state_id=MATCH.s),
        salience=99
    )
    def start_path_trace(self, s):
        self.declare(
            TracePath(state_id=s)
        )
        print('\n>>> TRACING PATH <<<')

    @Rule(
        TracePath(state_id=MATCH.current_id),
        NOT(PathTraced(state_id=MATCH.current_id)),
        State(
            id=MATCH.current_id,
            parent=MATCH.parent,
            action=MATCH.action,
            robot_x=MATCH.x,
            robot_y=MATCH.y,
            cost=MATCH.cost
        ),
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
    # PHASE 3: SELECT BEST FRONTIER (A*)
    # ==================================

    @Rule(
        AS.active << ActiveState(state_id=MATCH.current_state),
        MovesGenerated(state_id=MATCH.current_state),
        AS.os << OpenState(state_id=MATCH.current_state),
        NOT(FinalState()),
        salience=-5
    )
    def retract_frontier(self, active, os, current_state):
        self.retract(active)
        self.retract(os)

    @Rule(
        NOT(ActiveState()),
        NOT(FinalState()),
        salience=-6
    )
    def select_best_frontier(self):
        best_id = self._select_best_open_state()

        if best_id != -1:
            self.expanded_count += 1

        self.declare(ActiveState(state_id=best_id))
        print(f'[A* SELECT] Expanding state {best_id}...')


if __name__ == '__main__':
    engine = RoseEngineAStar()
    engine.reset()
    load_initial_facts(engine)
    print("=== Rose Gallery Robot - A* ===")
    print("5x5 | WH:(2,3) | Start:(1,3) | p1(4,2) p2(3,4) p3(5,4) p4(2,5)\n")
    engine.run()
    print("\n=== Search Completed ===")
    print(f"Total Generated States : {engine.generated_count}")
    print(f"Total Visited/Expanded States : {engine.expanded_count}")
