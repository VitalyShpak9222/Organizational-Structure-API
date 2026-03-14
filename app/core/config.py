from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pydantic.fields import FieldInfo

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost/org_structure"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Кастомная настройка источников настроек."""
        return (init_settings, env_settings, dotenv_settings, file_secret_settings)

settings = Settings()