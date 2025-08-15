"""FastAPI application entry point."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from . import auth
from .config import settings
from .db import SessionLocal
from .graphql_schema import schema
from .rate_limit import rate_limit_dependency

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Virtual Trainer API", dependencies=[Depends(rate_limit_dependency)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


async def get_context(request: Request):
    token = request.headers.get("Authorization")
    user_id = None
    role = "user"
    if token and token.startswith("Bearer "):
        try:
            payload = auth.decode_token(token.split(" ")[1])
            user_id = int(payload.get("sub"))
            role = payload.get("role", "user")
        except Exception:  # pragma: no cover - invalid token
            pass
    return {"request": request, "db": request.state.db, "user_id": user_id, "role": role}


gql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(gql_app, prefix="/graphql")


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
