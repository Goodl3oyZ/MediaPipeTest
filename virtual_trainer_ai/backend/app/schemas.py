"""Pydantic models for request/response bodies."""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterInput(BaseModel):
    email: EmailStr
    password: str


class LoginInput(RegisterInput):
    pass


class SignedUrlInput(BaseModel):
    mime: str
    filename: str


class AnalyzeRequestInput(BaseModel):
    key: str


class ExerciseResultOut(BaseModel):
    id: int
    label: str
    score: str | None = None
    feedback: str | None = None
    input_video_key: str | None = None
    output_video_key: str | None = None

    class Config:
        orm_mode = True
