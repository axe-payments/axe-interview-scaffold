"""Application configuration.

The only thing read from the environment is the Vapi API key — the one secret. Locally
it comes from the `.env` file you create from `.env.example` (Docker Compose loads it
automatically). The (non-secret) assistant and phone-number IDs are hard-coded in
`app/vapi.py`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Vapi (the only secret) ---
    # You will be given this value at the start of the interview.
    vapi_api_key: str = ""

    # Postgres connection string used by Tortoise ORM. The default points at the
    # `postgres` service in docker-compose; override only if running outside Docker.
    database_url: str = "postgres://postgres:postgres@postgres:5432/interview"


settings = Settings()
