"""Strawberry GraphQL schema definitions."""

from __future__ import annotations

from typing import List

import strawberry
from sqlalchemy.orm import Session
from rq import Queue
import redis

from . import auth, models, storage
from .config import settings
from .worker.jobs import enqueue_analyze_video

redis_conn = redis.from_url(settings.redis_url)
queue = Queue(connection=redis_conn)


@strawberry.type
class UserType:
    id: int
    email: str
    role: str


@strawberry.type
class ExerciseResultType:
    id: int
    label: str
    score: str | None
    feedback: str | None
    input_video_key: str | None
    output_video_key: str | None


@strawberry.type
class SignedUrl:
    url: str
    key: str | None = None


@strawberry.type
class Token:
    access_token: str
    token_type: str = "bearer"


@strawberry.input
class RegisterInput:
    email: str
    password: str


@strawberry.input
class LoginInput(RegisterInput):
    pass


@strawberry.input
class AnalyzeRequestInput:
    key: str


def get_user(session: Session, user_id: int) -> models.User | None:
    return session.query(models.User).filter(models.User.id == user_id).first()


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info) -> UserType | None:
        user_id = info.context.get("user_id")
        db: Session = info.context["db"]
        if user_id is None:
            return None
        user = get_user(db, user_id)
        return UserType(id=user.id, email=user.email, role=user.role) if user else None

    @strawberry.field
    def exercise_results(self, info, limit: int = 10, offset: int = 0) -> List[ExerciseResultType]:
        db: Session = info.context["db"]
        user_id = info.context.get("user_id")
        q = db.query(models.ExerciseResult).filter(models.ExerciseResult.user_id == user_id).offset(offset).limit(limit)
        return [
            ExerciseResultType(
                id=r.id,
                label=r.label,
                score=r.score,
                feedback=r.feedback,
                input_video_key=r.input_video_key,
                output_video_key=r.output_video_key,
            )
            for r in q
        ]

    @strawberry.field
    def get_signed_download_url(self, info, key: str) -> SignedUrl:
        url = storage.presigned_get(key)
        return SignedUrl(url=url, key=key)

    @strawberry.field
    def get_signed_upload_url(self, info, mime: str, filename: str) -> SignedUrl:  # noqa: A002
        url, key = storage.presigned_put(mime, filename)
        return SignedUrl(url=url, key=key)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, info, input: "RegisterInput") -> "Token":  # noqa: A003
        db: Session = info.context["db"]
        existing = db.query(models.User).filter(models.User.email == input.email).first()
        if existing:
            raise ValueError("user exists")
        user = models.User(email=input.email, password_hash=auth.hash_password(input.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        token = auth.create_access_token({"sub": str(user.id), "role": user.role})
        return Token(access_token=token)

    @strawberry.mutation
    def login(self, info, input: "LoginInput") -> "Token":
        db: Session = info.context["db"]
        user = db.query(models.User).filter(models.User.email == input.email).first()
        if not user or not auth.verify_password(input.password, user.password_hash):
            raise ValueError("invalid credentials")
        token = auth.create_access_token({"sub": str(user.id), "role": user.role})
        return Token(access_token=token)

    @strawberry.mutation
    def request_analyze_video(self, info, input: "AnalyzeRequestInput") -> str:
        db: Session = info.context["db"]
        user_id = info.context.get("user_id")
        job = enqueue_analyze_video(queue, db, user_id, input.key)
        return job


schema = strawberry.Schema(query=Query, mutation=Mutation)
