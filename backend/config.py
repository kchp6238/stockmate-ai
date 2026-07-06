from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    FINNHUB_API_KEY:   str = ""
    ALPHA_VANTAGE_KEY: str = ""
    FRONTEND_URL:      str = "http://localhost:5173"
    ENVIRONMENT:       str = "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
