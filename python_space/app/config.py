from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    API_KEYS: str = "test-key-123"
    
    # Rate limiting
    RATE_LIMIT: str = "5/minute"
    
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Downloads
    DOWNLOADS_DIR: str = "./tmp/downloads"
    
    # yt-dlp
    YTDLP_COOKIES_BROWSER: str = "chrome"
    
    # Ollama (AI for comment generation)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def api_keys_list(self) -> List[str]:
        return [key.strip() for key in self.API_KEYS.split(",") if key.strip()]


settings = Settings()


