"""Background jobs for analyzing videos."""

from __future__ import annotations

from typing import Optional

from rq import Queue
from sqlalchemy.orm import Session

from ..app import storage
from ..app.models import ExerciseResult, JobAudit
from scripts import ml_core


def enqueue_analyze_video(queue: Queue, db: Session, user_id: int, input_key: str) -> str:
    audit = JobAudit(user_id=user_id, job_id="", status="queued", input_key=input_key)
    db.add(audit)
    db.commit()
    db.refresh(audit)
    job = queue.enqueue(run_analyze_video, audit.id)
    audit.job_id = job.id
    db.commit()
    return job.id


def run_analyze_video(audit_id: int) -> None:
    # In a real implementation we'd download from S3 using the input_key.
    from ..app.db import SessionLocal

    db = SessionLocal()
    audit = db.query(JobAudit).get(audit_id)
    try:
        result = ml_core.analyze(b"dummy")
        output_key = f"results/{audit.job_id}.txt"
        storage.upload_bytes(result["output"], output_key, "text/plain")
        exercise = ExerciseResult(
            user_id=audit.user_id,
            label=result["label"],
            score=str(result["score"]),
            feedback=result["feedback"],
            input_video_key=audit.input_key,
            output_video_key=output_key,
        )
        db.add(exercise)
        audit.status = "finished"
        audit.output_key = output_key
        db.commit()
    except Exception as exc:  # pragma: no cover - simple error handling
        audit.status = "failed"
        audit.error = str(exc)
        db.commit()
    finally:
        db.close()
