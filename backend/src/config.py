"""Configuration management using Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration - Using uwcourses.com API
    api_base_url: str = "https://static.uwcourses.com"
    request_timeout: int = 10
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    # Notification Settings
    email_enabled: bool = True
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_smtp_user: Optional[str] = None
    email_smtp_pass: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[str] = None

    sms_enabled: bool = False
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_from: Optional[str] = None
    twilio_phone_to: Optional[str] = None

    webhook_enabled: bool = False
    webhook_url: Optional[str] = None

    # Monitoring Settings
    check_interval: int = 300
    max_retries: int = 3
    retry_backoff: int = 2

    # Database
    database_url: str = "sqlite:///./data/courses.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
