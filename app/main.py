import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, user

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = [] # A definir!
    allow_credentials = True
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    origins = ["*"]
    allow_credentials = False
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"

app = FastAPI(
    title="API da Biblioteca Virtual",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(user.router, prefix="/api/user", tags=["user"])