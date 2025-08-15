from pydantic import BaseModel


# TODO: define Pydantic schemas for request/response models

class HealthResponse(BaseModel):
    status: str
