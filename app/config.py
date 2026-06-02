"""Application configuration, loaded from the environment (.env).

Everything here is read from environment variables. Locally those come from the
`.env` file you create from `.env.example` (Docker Compose loads it automatically).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Vapi: three pre-configured agents + two phone numbers ---
    # You will be given these values at the start of the interview.
    vapi_api_key: str = ""
    vapi_assistant_id_1: str = ""
    vapi_assistant_id_2: str = ""
    vapi_assistant_id_3: str = ""
    vapi_phone_number_id_1: str = ""
    vapi_phone_number_id_2: str = ""

    # The phone number the demo call should ring. Put YOUR phone here (E.164,
    # e.g. +14155551234). The mock CRM uses it as the demo order's contact phone.
    demo_target_phone: str = ""

    # Postgres connection string used by Tortoise ORM. The default points at the
    # `postgres` service in docker-compose; override only if running outside Docker.
    database_url: str = "postgres://postgres:postgres@postgres:5432/interview"

    @property
    def assistant_ids(self) -> list[str]:
        """The configured assistant IDs, in order, skipping any left blank."""
        ids = (self.vapi_assistant_id_1, self.vapi_assistant_id_2, self.vapi_assistant_id_3)
        return [i for i in ids if i]

    @property
    def phone_number_ids(self) -> list[str]:
        """The configured phone-number IDs, in order, skipping any left blank."""
        ids = (self.vapi_phone_number_id_1, self.vapi_phone_number_id_2)
        return [i for i in ids if i]


settings = Settings()
