from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str
    google_client_id: str
    google_client_secret: str
    oauth_redirect_uri: str = "http://localhost:8000/auth/callback"
    secret_key: str

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
