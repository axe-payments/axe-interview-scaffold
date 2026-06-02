"""Application configuration, loaded from the environment (.env).

Everything here is read from environment variables. Locally those come from the
`.env` file you create from `.env.example` (Docker Compose loads it automatically).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Vapi: two pre-configured agent / phone-number pairs ---
    # You will be given these values at the start of the interview.
    vapi_api_key: str = ""
    vapi_assistant_id_1: str = ""
    vapi_phone_number_id_1: str = ""
    vapi_assistant_id_2: str = ""
    vapi_phone_number_id_2: str = ""

    # The phone number the demo call should ring. Put YOUR phone here (E.164,
    # e.g. +14155551234). The mock CRM uses it as the demo order's contact phone.
    demo_target_phone: str = ""

    # Postgres connection string used by Tortoise ORM. The default points at the
    # `postgres` service in docker-compose; override only if running outside Docker.
    database_url: str = "postgres://postgres:postgres@postgres:5432/interview"


settings = Settings()
