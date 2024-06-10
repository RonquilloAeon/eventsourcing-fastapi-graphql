from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, case_sensitive=False):
    log_level: str

    model_config = SettingsConfigDict(env_prefix="DM_")


settings = Settings()
