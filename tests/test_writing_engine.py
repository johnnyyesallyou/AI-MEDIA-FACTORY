from engines.writing.engine import WritingEngine


def test_writing_engine_creation():

    engine = WritingEngine()

    assert engine is not None



def test_writing_engine_model():

    engine = WritingEngine()

    assert engine.model is not None

