from pydantic import computed_field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    # ========= environment variables =========

    environment: str = "development"
    
    db_url: str
    db_service_key: str
    
    email_service_api_key: str
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # ========= computed: environment =========

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    # ========== computed: app config ==========

    @computed_field
    @property
    def origins(self) -> list[str]:
        # A DEFINIR O RETORNO EM PRODUCTION
        return [] if self.is_production else ["*"]

    @computed_field
    @property
    def allow_credentials(self) -> bool:
        return self.is_production
    
    @computed_field
    @property
    def docs_url(self) -> str | None:
        return None if self.is_production else "/docs"

    @computed_field
    @property
    def redoc_url(self) -> str | None:
        return None if self.is_production else "/redoc"
    
    @computed_field
    @property
    def openapi_url(self) -> str | None:
        return None if self.is_production else "/openapi.json"
    
    model_config = {"env_file": ".env"}

settings = AppSettings()