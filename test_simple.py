import monkeypatch
from rules import RoseEngine
from knowledge_base import load_initial_facts

engine = RoseEngine()
engine.reset()
load_initial_facts(engine)

# Print facts before running
print("=== INITIAL FACTS ===")
print(f"Grid: 6x6")
print(f"Warehouse: (2,3)")
print(f"Initial Robot position: (3,1)")
print(f"Pavilions: p1=(4,2), p2=(3,4), p3=(5,4), p4=(2,5)")
print(f"Total Bouquets: 6")
print(f"Total Pavilion Needs: 7")
print(f"\nStarting search... (limiting to 100 states for testing)")

# Run with a limit
state_counter = 0
max_states = 100
original_declare = engine.declare

def limited_declare(fact):
    global state_counter
    if hasattr(fact, '__class__') and 'State' in str(fact.__class__):
        state_counter += 1
        if state_counter % 20 == 0:
            print(f"[{state_counter}] State created")
        if state_counter > max_states:
            print(f"\n!! Reached state limit of {max_states}, halting")
            raise Exception("State limit reached")
    return original_declare(fact)

engine.declare = limited_declare

try:
    engine.run()
except:
    pass

print(f"\nGenerated {state_counter} states before stopping")
