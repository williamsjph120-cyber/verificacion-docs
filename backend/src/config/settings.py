import os
from dataclasses import dataclass, field

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class Settings:
    APP_NAME: str = "Verificación de Documentos"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(PROJECT_ROOT, 'verificacion_docs.db')}"
    )

    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "verificacion-documentos")
    R2_ENDPOINT_URL: str = os.getenv("R2_ENDPOINT_URL", "")

    CAPTCHA_LENGTH: int = 5
    CAPTCHA_WIDTH: int = 200
    CAPTCHA_HEIGHT: int = 80

    CORS_ORIGINS: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","))


settings = Settings()
