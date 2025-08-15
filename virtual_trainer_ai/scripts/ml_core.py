"""Pure ML core functions with no external side effects."""

from __future__ import annotations


def analyze(data: bytes) -> dict[str, object]:
    """Fake analysis returning dummy results."""
    # A real implementation would run MediaPipe / scikit-learn here.
    return {
        "label": "squat",
        "score": 0.9,
        "feedback": "Good form",
        "output": b"analysis-results",
    }
