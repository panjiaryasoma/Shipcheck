from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    github_token: str | None = None

    shipcheck_model: str | None = None
    shipcheck_fallback_models: str = "gemini-3.6-flash,gemini-3.5-flash"
    shipcheck_env: str = "development"
    shipcheck_request_timeout_seconds: int = 20
    shipcheck_rules_cache_ttl_seconds: int = 3600
    shipcheck_firestore_enabled: bool = False
    shipcheck_firestore_database: str = "(default)"
    shipcheck_firestore_collection: str = "shipcheck_inspections"


settings = Settings()
