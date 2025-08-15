from scripts import ml_core


def test_analyze_returns_expected_keys():
    result = ml_core.analyze(b"data")
    assert {"label", "score", "feedback", "output"} <= result.keys()
