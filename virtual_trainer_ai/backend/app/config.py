from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:mypassword@db:5432/fitnessai"
    secret_key: str = "CHANGE_ME"  # TODO: use secure value in production

    class Config:
        env_file = ".env"


settings = Settings()
