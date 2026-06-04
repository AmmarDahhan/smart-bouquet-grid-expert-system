import monkeypatch
from rules import RoseEngine
from knowledge_base import load_initial_facts


engine = RoseEngine()
engine.reset()
load_initial_facts(engine)
print("=== Rose Gallery Robot Delivery System ===")
print("Grid: 6x6 | Warehouse: (2,3) | Start: (3,1)")
print("Pavilions: p1=(4,2), p2=(3,4), p3=(5,4), p4=(2,5)")
print("Using: Experta with DFS + State-Based Search\n")
engine.run()
print("\n=== Search Completed ===")