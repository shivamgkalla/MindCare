from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "MindCare"

    # Database
    DATABASE_URL: str

    #Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Forgot Password
    RESET_TOKEN_EXPIRE_MINUTES : int = 15

    # SMTP Email Config
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str
    DEV_MODE: bool = True


    class Config:
        env_file = ".env"


settings = Settings()