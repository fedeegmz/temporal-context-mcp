from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    data_dir: str = "data"
    contexts_file_name: str = "context.json"
    recommendations_file_name: str = "recommendations.json"


settings = Settings()
