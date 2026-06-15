import os
from pathlib import Path
from dotenv import load_dotenv

# Load from the directory this file lives in (works regardless of cwd)
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Creative AI Studio")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION")
    # Set to true in .env for local dev — bypasses Firebase, any credentials work
    DEV_AUTH_BYPASS: bool = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"

    # GCP
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")

    # Cloud SQL / Database
    DB_URL: str = os.getenv("DB_URL", "")              # Full override URL (optional)
    DB_HOST: str = os.getenv("DB_HOST", "")            # Leave blank → SQLite in dev
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "creative_ai_studio")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    CLOUD_SQL_INSTANCE: str = os.getenv("CLOUD_SQL_INSTANCE", "")

    # Firebase / Google Identity Platform
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

    # GCS
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "")

    # Vertex AI
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")

    # Flask Session
    SESSION_TYPE: str = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_PERMANENT: bool = os.getenv("SESSION_PERMANENT", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME: int = int(os.getenv("PERMANENT_SESSION_LIFETIME", "3600"))

    # Firebase Auth REST endpoints
    FIREBASE_SIGN_UP_URL: str = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    )
    FIREBASE_SIGN_IN_URL: str = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    )
    FIREBASE_RESET_URL: str = (
        "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    )
    FIREBASE_REFRESH_URL: str = (
        "https://securetoken.googleapis.com/v1/token"
    )

    @property
    def database_url(self) -> str:
        if self.CLOUD_SQL_INSTANCE and not self.DEBUG:
            # Cloud Run: connect via Unix socket through Cloud SQL connector
            # The Cloud SQL Python Connector overrides the URL; this is a placeholder.
            return (
                f"postgresql+pg8000://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@/{self.DB_NAME}"
            )
        return (
            f"postgresql+pg8000://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
