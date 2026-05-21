from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = 'development'
    database_url: str = 'sqlite:///./local.db'
    api_host: str = '0.0.0.0'
    api_port: int = 8000

    class Config:
        env_file = '.env'


settings = Settings()
