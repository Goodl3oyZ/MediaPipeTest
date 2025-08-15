# TODO: define background job functions

from rq import Queue

from ..app.storage import upload_file


def enqueue_analyze_video(q: Queue, file_path: str) -> None:
    """Placeholder job enqueue function."""
    q.enqueue(process_video, file_path)


def process_video(file_path: str) -> str:
    """Placeholder video processing task."""
    # In production, call ML core functions here
    with open(file_path, "rb") as f:
        upload_file(f, file_path)
    return "processed"
