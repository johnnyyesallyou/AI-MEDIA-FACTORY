from engines.research.engine import ResearchEngine


def test_research_engine_creation():

    engine = ResearchEngine()

    assert engine is not None



def test_research_engine_initial_state():

    engine = ResearchEngine()

    assert engine._initialized is False

