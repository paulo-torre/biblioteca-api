from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import computed_field
from pydantic_settings import BaseSettings

from app.routers import auth, books, user


class AppSettings(BaseSettings):
    environment: str = "development"

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
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
    
    class Config:
        env_file = ".env"

settings = AppSettings()

app = FastAPI(
    title="API da Biblioteca Virtual",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(user.router, prefix="/api/user", tags=["user"])