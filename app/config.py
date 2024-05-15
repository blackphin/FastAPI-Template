from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Credentials
    database_username: str
    database_password: str
    database_hostname: str
    database_port: str
    database_name: str

    # SlowAPI
    rate_limit: str

    # Google OAuth2
    google_client_id: str
    google_client_secret: str
    redirect_url: str

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = r"./.env"


settings = Settings()
