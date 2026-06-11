import monkeypatch
from rules import RoseEngine
from knowledge_base import load_initial_facts


engine = RoseEngine()
engine.reset()
load_initial_facts(engine)
print("=== Rose Gallery Robot - DFS ===")
print("5x5 | WH:(2,3) | Start:(1,3) | p1(4,2) p2(3,4) p3(5,4) p4(2,5)\n")
engine.run()
print("\n=== Search Completed ===")

print("\n=== Summary ===")
print(f"Generated states: {engine.generated_count}")
print(f"Expanded states: {engine.expanded_count}")