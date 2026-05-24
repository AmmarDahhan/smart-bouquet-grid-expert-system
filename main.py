from rules import RoseEngine
from knowledge_base import load_initial_facts


engine = RoseEngine()

engine.reset()

load_initial_facts(engine)

engine.run()