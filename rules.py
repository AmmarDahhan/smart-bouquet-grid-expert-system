
from experta import *

from models import *


class RoseEngine(KnowledgeEngine):

    # ==================================
    # GENERATE RIGHT MOVE
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
        )
        ,
        salience=10
    )
    def generate_move_right(self,state_id,x,y,cost,path):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_right',
                new_x=x + 1,
                new_y=y,
                new_cost=cost + 1,
                path=path
            )
        )

    # ==================================
    # GENERATE LEFT MOVE
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
        )
        ,
        salience=10
    )
    def generate_move_left(self,state_id,x,y,cost,path):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_left',
                new_x=x - 1,
                new_y=y,
                new_cost=cost + 1,
                path=path
            )
        )

    # ==================================
    # GENERATE UP MOVE
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
        )
        ,
        salience=10
    )
    def generate_move_up(self,state_id,x,y,cost,path):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_up',
                new_x=x,
                new_y=y - 1,
                new_cost=cost + 1,
                path=path
            )
        )

    # ==================================
    # GENERATE DOWN MOVE
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
        ) 
        ,
        salience=10
    )
    def generate_move_down(self,state_id,x,y,cost,path):

        self.declare(
            CandidateMove(
                parent_state=state_id,
                action='move_down',
                new_x=x,
                new_y=y + 1,
                new_cost=cost + 1,
                path=path
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
            new_cost=MATCH.cost,
            path=MATCH.path
        ),

        TEST(lambda x: x >= 1),
        TEST(lambda y: y >= 1),
        TEST(lambda x, width: x <= width),
        TEST(lambda y, height: y <= height),
        TEST(lambda x, y, path: (x, y) not in path),
    )
    def validate_move(self,parent,action,x,y,cost,path):

        self.declare(
            ValidMove(
                parent_state=parent,
                action=action,
                new_x=x,
                new_y=y,
                new_cost=cost,
                path=path
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
    def show_valid_move(self,parent,action,x,y):

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
            new_cost=MATCH.cost,
            path=MATCH.path
        ),
    )
    def generate_state(self,counter,valid_move,counter_value,parent,action,x,y,cost,path):

        new_state_id = counter_value + 1
        new_path = path + ((x, y),)

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
                cost=cost,
                path=new_path
            )
        )

        self.declare(
            OpenState(
                state_id=new_state_id
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
        print(
            f"STATE CREATED: {new_state_id} parent={parent}"
        )

    # ==================================
    # PROPAGATE ROBOT LOAD
    # ==================================

    @Rule(
        State(
            id=MATCH.new_state,
            parent=MATCH.parent_state
        ),

        RobotLoad(
            state_id=MATCH.parent_state,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.count
        ),

        NOT(
            Delivered(
                state_id=MATCH.parent_state,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),        

        NOT(
            RobotLoad(
                state_id=MATCH.new_state,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        salience = 150
    )
    def propagate_robot_load(self,new_state,flower,color,count):

        self.declare(
            RobotLoad(
                state_id=new_state,
                flower=flower,
                color=color,
                count=count
            )
        )

        print(
            f'\nLoad propagated to state {new_state}'
        )

    # ==================================
    # DETECT ROBOT AT WAREHOUSE
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
    def detect_robot_at_warehouse(self,state_id):

        self.declare(
            RobotAtWarehouse(
                state_id=state_id
            )
        )

        print(
            f'\nRobot reached warehouse in state {state_id}'
        )

    # ==================================
    # LOAD BOUQUET
    # ==================================

    # option1
    @Rule(
        ActiveState(state_id=MATCH.state_id),
        RobotAtWarehouse(state_id=MATCH.state_id),
        NOT(RobotLoad(state_id=MATCH.state_id)), 
        PavilionNeed(state_id=MATCH.state_id, flower=MATCH.f, color=MATCH.c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        salience=160
    )
    def start_loading(self, state_id, f, c, cnt):
        self.declare(RobotLoad(state_id=state_id, flower=f, color=c, count=cnt))
        print(f"\n[LOAD] Started loading: {cnt} {f} ({c}) in state {state_id}")

    # الخطوة 2: متابعة التحميل لباقات من (نفس النوع) ولكن ألوان مختلفة لنفس الجناح
    @Rule(
        ActiveState(state_id=MATCH.state_id),
        RobotAtWarehouse(state_id=MATCH.state_id),
        RobotLoad(state_id=MATCH.state_id, flower=MATCH.f), 
        PavilionNeed(state_id=MATCH.state_id, flower=MATCH.f, color=MATCH.new_c, count=MATCH.cnt),
        TEST(lambda cnt: cnt > 0),
        NOT(RobotLoad(state_id=MATCH.state_id, flower=MATCH.f, color=MATCH.new_c)), 
        salience=150
    )
    def continue_loading_same_flower(self, state_id, f, new_c, cnt):
        self.declare(RobotLoad(state_id=state_id, flower=f, color=new_c, count=cnt))
        print(f"[LOAD] Added to load: {cnt} {f} ({new_c}) in state {state_id}")
    # ==================================
    # DETECT ROBOT HAS LOAD
    # ==================================

    @Rule(
        RobotLoad(
            state_id=MATCH.state_id
        ),
        NOT(
            Delivered(
                state_id=MATCH.state_id,
                flower=MATCH.flower,
                color=MATCH.color
            )
        )
    )
    def detect_robot_has_load(self,state_id):

        self.declare(
            RobotHasLoad(
                state_id=state_id
            )
        )

        print(
            f'\nRobot has load in state {state_id}'
        )

    # ==================================
    # DETECT ROBOT AT PAVILION
    # ==================================

    @Rule(
        Pavilion(
            name=MATCH.name,
            flower=MATCH.flower,
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
    def detect_robot_at_pavilion(self,state_id,name):

        self.declare(
            RobotAtPavilion(
                state_id=state_id,
                pavilion=name
            )
        )

        print(
            f'\nRobot reached pavilion {name}'
        )
        
        print(f'STATE = {state_id}')

    # ==================================
    # UNLOAD BOUQUET
    # ==================================

    @Rule(
        ActiveState(state_id=MATCH.state_id),
        
        RobotAtPavilion(
            state_id=MATCH.state_id,
            pavilion=MATCH.pavilion
        ),

        AS.load << RobotLoad(
            state_id=MATCH.state_id,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.load_count
        ),
        AS.need << PavilionNeed(
            state_id=MATCH.state_id,
            pavilion=MATCH.pavilion,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.need_count
        ),
        TEST(lambda load_count: load_count > 0),
        TEST(lambda need_count: need_count > 0),
        salience = 200
    )
    def unload_bouquet(self,load,need,state_id,pavilion,flower,color,need_count,load_count):
        amount_to_unload = min(need_count, load_count)

        self.modify(
            load,
            count=load_count - amount_to_unload
        )
        self.modify(
            need,
            count=need_count - amount_to_unload
        )    

        print(f'\n[SUCCESS] Unloaded {amount_to_unload} bouquets of {flower} ({color}) at pavilion {pavilion} in state {state_id}')

    # ==================================
    # SHOW FINAL PATH
    # ==================================

    @Rule(
        FinalState(
            state_id=MATCH.state_id
        ),

        State(
            id=MATCH.state_id,
            parent=MATCH.parent,
            action=MATCH.action
        )
    )
    def show_final_path(self,state_id,parent,action):

        print(
            f'\nFINAL STATE: {state_id}'
        )

        print(
            f'Last action: {action}'
        )

        print(
            f'Parent state: {parent}'
        )

    # ==================================
    # START PATH TRACE
    # ==================================

    @Rule(
        FinalState(
            state_id=MATCH.state_id
        )
    )
    def start_path_trace(self,state_id):

        self.declare(
            TracePath(
                state_id=state_id
            )
        )

    # ==================================
    # TRACE PATH
    # ==================================

    @Rule(
        TracePath(
            state_id=MATCH.state_id
        ),

        State(
            id=MATCH.state_id,
            parent=MATCH.parent,
            action=MATCH.action,
            robot_x=MATCH.x,
            robot_y=MATCH.y
        )
    )
    def trace_path(self,state_id,parent,action,x,y):

        print(
            f'\nPATH STATE {state_id}'
        )

        print(
            f'Action: {action}'
        )

        print(
            f'Position: ({x},{y})'
        )

        self.declare(
            TracePath(
                state_id=parent
            )
        )

    # ==================================
    # TRACE ROOT STATE
    # ==================================

    @Rule(
        TracePath(
            state_id=1
        )
    )
    def trace_root(self):

        print(
            '\nReached initial state'
        )

        # self.halt()

    # ==================================
    # DETECT ALL NEEDS COMPLETED
    # ==================================

    @Rule(
        NOT(
            PavilionNeed()
        )
    )
    def all_needs_completed(self):

        self.declare(
            AllNeedsCompleted()
        )

        print(
            '\nALL PAVILION NEEDS COMPLETED'
        )

    # ==================================
    # FINAL GOAL
    # ==================================

    @Rule(
        AllNeedsCompleted()
    )
    def final_goal(self):

        print(
            '\nALL PAVILIONS COMPLETED'
        )

        self.declare(
            FinalState(
                state_id=-1
            )
        )

    @Rule(
        State(id=MATCH.new_state, parent=MATCH.parent_state),
        PavilionNeed(
            state_id=MATCH.parent_state,
            pavilion=MATCH.pav,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.count
        ),
        NOT(
            PavilionNeed(
                state_id=MATCH.new_state,
                pavilion=MATCH.pav,
                flower=MATCH.flower,
                color=MATCH.color
            )
        ),
        salience = 150
    )
    def propagate_pavilion_need(self, new_state, pav, flower, color, count):
        print(
            f"PROPAGATE NEED -> {new_state}"
        )
        self.declare(
            PavilionNeed(
                state_id=new_state,
                pavilion=pav,
                flower=flower,
                color=color,
                count=count
            )
        )
        
    # ==================================
    # CHECK FINAL GOAL
    # ==================================
    @Rule(
        ActiveState(state_id=MATCH.s),
        # القاعدة تقول: إذا لم يوجد أي جناح يمتلك احتياجاً أكبر من صفر
        NOT(
            PavilionNeed(state_id=MATCH.s, count=MATCH.c),
            TEST(lambda c: c > 0)
        ),
        NOT(FinalState()),
        salience=210
    )
    def goal_reached(self, s):
        self.declare(FinalState(state_id=s))
        print(f"\n=========================================")
        print(f"[!!!] GOAL REACHED in State {s}! All needs satisfied.")
        print(f"=========================================")
        self.halt()
 

    # ==================================
    # SELECT NEXT STATE TO EXPLORE (Uniform Cost Search)
    # ==================================
    @Rule(
        AS.active << ActiveState(
            state_id=MATCH.old_id
        ),

        AS.open_st << OpenState(
            state_id=MATCH.new_id
        ),

        salience=-10
    )
    def select_next_state(
        self,
        active,
        open_st,
        new_id
    ):

        self.retract(active)

        self.retract(open_st)

        self.declare(
            ActiveState(
                state_id=new_id
            )
        )

        print(
            f"\n[MOVE] Active state moved to {new_id}"
        )

    @Rule(
        PavilionNeed(
            state_id=MATCH.s,
            pavilion=MATCH.p,
            flower=MATCH.f,
            color=MATCH.c,
            count=MATCH.n
        )
    )
    def debug_need(self,s,p,f,c,n):

        print(
            f"NEED: state={s} {p} {f} {c} {n}"
        )

    @Rule(
        RobotAtWarehouse(
            state_id=MATCH.s
        )
    )
    def debug_warehouse(self, s):

        print(f"\nWAREHOUSE FACT FOUND : {s}")

    @Rule(
        ActiveState(
            state_id=MATCH.s
        )
    )
    def debug_active(self, s):

        print(f"\nACTIVE = {s}")