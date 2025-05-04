from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # General
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dooscorp Payment Gateway")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Database settings
    #POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Payment
    FLW_SECRET_KEY: str = os.getenv("FLW_SECRET_KEY")
    FLW_PUBLIC_KEY: str = os.getenv("FLW_PUBLIC_KEY")
    FLW_ENCRYPTION_KEY: str = os.getenv("FLW_ENCRYPTION_KEY")
    FLW_SECRET_HASH: str = os.getenv("FLW_SECRET_HASH")

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")
    STRPE_ENDPOINT_SECRET: str = os.getenv("STRPE_ENDPOINT_SECRET")

    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET")

    # Email service
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")
    NOREPLY_EMAIL: str = os.getenv("NOREPLY_EMAIL")
    PAYMENT_UPDATE_EMAIL: str = os.getenv("PAYMENT_UPDATE_EMAIL")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("BACKEND_CORS_ORIGINS", "[]").strip('[]').replace('"', '').split(',')

    class Config:
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
            )

settings = Settings() 