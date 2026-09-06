import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # LangSmith Tracing
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "neeraj-portfolio-chatbot"
    LANGSMITH_TRACING: str = "true"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"

    # Frontend URL & CORS
    FRONTEND_URL: str = "https://personal-portfolio-1-uo2v.onrender.com"
    ADDITIONAL_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    # Server port
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_cors_origins(self) -> List[str]:
        origins = set()
        if self.FRONTEND_URL:
            for item in self.FRONTEND_URL.split(","):
                item = item.strip().rstrip("/")
                if item:
                    origins.add(item)
                    origins.add(f"{item}/")
        if self.ADDITIONAL_CORS_ORIGINS:
            for item in self.ADDITIONAL_CORS_ORIGINS.split(","):
                item = item.strip().rstrip("/")
                if item:
                    origins.add(item)
                    origins.add(f"{item}/")
        return list(origins)

    def setup_environment(self):
        """Export LangSmith configuration to environment variables for automated tracing."""
        if self.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGSMITH_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
            os.environ["LANGSMITH_PROJECT"] = self.LANGSMITH_PROJECT
            os.environ["LANGCHAIN_TRACING_V2"] = self.LANGSMITH_TRACING
            os.environ["LANGSMITH_TRACING"] = self.LANGSMITH_TRACING
            os.environ["LANGCHAIN_ENDPOINT"] = self.LANGSMITH_ENDPOINT

settings = Settings()
settings.setup_environment()
