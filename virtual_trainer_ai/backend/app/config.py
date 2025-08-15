"""Application configuration loaded from environment variables."""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Central application configuration using :class:`pydantic.BaseSettings`."""

    database_url: str = Field(
        "postgresql://postgres:mypassword@db:5432/fitnessai",
        env="DATABASE_URL",
    )
    secret_key: str = Field("CHANGE_ME", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")

    s3_endpoint: str = Field("http://minio:9000", env="S3_ENDPOINT")
    s3_access_key: str = Field("minio", env="S3_ACCESS_KEY")
    s3_secret_key: str = Field("minio123", env="S3_SECRET_KEY")
    s3_bucket: str = Field("virtual-trainer", env="S3_BUCKET")
    s3_region: str = Field("us-east-1", env="S3_REGION")
    s3_use_ssl: bool = Field(False, env="S3_USE_SSL")

    allowed_origins: list[str] = Field(default_factory=lambda: ["*"], env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"


settings = Settings()

