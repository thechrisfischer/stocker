from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "StockRocker"
    database_url: str = "sqlite:////data/stocker.db"
    secret_key: str = "change-me-in-production"
    token_expire_minutes: int = 20160  # 2 weeks

    # Mailgun (optional)
    mailgun_api_key: str = ""
    mailgun_domain: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
