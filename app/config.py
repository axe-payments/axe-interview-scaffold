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

    # --- Transcript callback (optional) ---
    # So Vapi can POST the call transcript back to us, the app needs a public URL. The
    # `ngrok` service in docker-compose tunnels to us automatically; we discover the random
    # tunnel URL from ngrok's local API. Set `public_base_url` to skip discovery and force a
    # URL (e.g. a reserved ngrok domain); leave it blank to auto-discover.
    public_base_url: str = ""
    ngrok_api_url: str = "http://ngrok:4040/api/tunnels"


settings = Settings()
