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
            cost=MATCH.cost
        ),
        ActiveState(
            state_id=MATCH.state_id
        ),
        NOT(
            MovesGenerated(
                state_id=MATCH.state_id
            )
        )
        ,
        salience=40
    )
    def generate_move_right(self,state_id,x,y,cost):

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
            MovesGenerated(
                state_id=state_id
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
            cost=MATCH.cost
        ),
        ActiveState(
            state_id=MATCH.state_id
        ),
        NOT(
            MovesGenerated(
                state_id=MATCH.state_id
            )
        )
        ,
        salience=20
    )
    def generate_move_left(self,state_id,x,y,cost):

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
        )
        ,
        salience=10
    )
    def generate_move_up(self,state_id,x,y,cost):

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
        )
        ,
        salience=30
    )
    def generate_move_down(self,state_id,x,y,cost):

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
    def validate_move(self,parent,action,x,y,cost):

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
            new_cost=MATCH.cost
        ),
        NOT(
            StateSignature(
                robot_x=MATCH.x,
                robot_y=MATCH.y
            )
        )
    )
    def generate_state(self,counter,valid_move,counter_value,parent,action,x,y,cost):

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
        )
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

    @Rule(
        RobotAtWarehouse(
            state_id=MATCH.state_id
        ),

        AS.bouquet << Bouquet(
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.count
        )
    )
    def load_bouquet(self,bouquet,state_id,flower,color,count):

        self.declare(
            RobotLoad(
                state_id=state_id,
                flower=flower,
                color=color,
                count=count
            )
        )

        self.retract(
            bouquet
        )

        print(
            f'\nLoaded bouquet in state {state_id}'
        )

        print(
            f'{flower} - {color} - {count}'
        )

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

    # ==================================
    # UNLOAD BOUQUET
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
        )
    )
    def unload_bouquet(self,load,need,state_id,pavilion,flower,color,need_count,load_count):
        
        # self.modify(
        #     load,
        #     count=load_count - 1
        # )
        self.retract(
            load
        )
        # self.retract(
        #     need
        # )
        self.modify(
            need,
            count=need_count - 1
        )

        self.declare(
            Delivered(
                state_id=state_id,
                pavilion=pavilion,
                flower=flower,
                color=color
            )
        )

        print(
            f'\nUnloaded bouquet at pavilion {pavilion}'
        )

        print(
            f'{flower} - {color}'
        )

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
    # MATCH LOAD WITH PAVILION NEED
    # ==================================

    @Rule(
        RobotAtPavilion(
            state_id=MATCH.state_id,
            pavilion=MATCH.pavilion
        ),

        RobotLoad(
            state_id=MATCH.state_id,
            flower=MATCH.flower,
            color=MATCH.color,
            count=MATCH.load_count
        ),

        PavilionNeed(
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
        )
    )
    def match_load_with_need(self,state_id,pavilion,flower,color):

        self.declare(
            MatchingLoad(
                state_id=state_id,
                pavilion=pavilion,
                flower=flower,
                color=color
            )
        )

        print(
            f'\nMatching bouquet for pavilion {pavilion}'
        )    

    # ==================================
    # REMOVE COMPLETED NEED
    # ==================================

    @Rule(
        AS.need << PavilionNeed(
            pavilion=MATCH.pavilion,
            flower=MATCH.flower,
            color=MATCH.color,
            count=0
        )
    )
    def remove_completed_need(self,need,pavilion,flower,color):

        self.retract(
            need
        )

        print(
            f'\nNeed completed for pavilion {pavilion}'
        )

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

    # ==================================
    # REMOVE EMPTY LOAD
    # ==================================

    @Rule(
        AS.load << RobotLoad(
            state_id=MATCH.state_id,
            flower=MATCH.flower,
            color=MATCH.color,
            count=0
        )
    )
    def remove_empty_load(self,load,flower,color):

        self.retract(
            load
        )

        print(
            f'\nLoad consumed: {flower} - {color}'
        )

    # ==================================
    # ACTIVATE NEXT STATE
    # ==================================

    @Rule(
        AS.active << ActiveState(
            state_id=MATCH.current_state
        ),

        AS.state << State(
            id=MATCH.current_state
        ),

        State(
            id=MATCH.next_state,
            parent=MATCH.current_state
        ),

        NOT(
            MovesGenerated(
                state_id=MATCH.current_state
            )
        ),

        salience=-10
    )
    def activate_next_state(self,active,state,current_state,next_state):

        self.retract(active)

        self.declare(
            MovesGenerated(
                state_id=current_state
            )
        )

        self.declare(
            ActiveState(
                state_id=next_state
            )
        )

        print(
            f'\nActive state moved to {next_state}'
        )